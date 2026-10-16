import pytest
from datetime import datetime, timedelta
from config import Config
from app import create_app, db
from app.models import User, Category, Product, StockTransaction, Alert, Prediction
from app.prediction_engine import calculate_prediction, run_all_predictions


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        admin = User(name="Admin User", email="admin@test.com", role="admin")
        admin.set_password("Admin@123")
        manager = User(name="Manager User", email="manager@test.com", role="manager")
        manager.set_password("Manager@123")
        staff = User(name="Staff User", email="staff@test.com", role="staff")
        staff.set_password("Staff@123")

        cat = Category(name="Electronics", description="Test category")
        db.session.add_all([admin, manager, staff, cat])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email, password):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)


# --- 1. Authentication & Role-Based Access ---

def test_index_redirects_to_login(client):
    res = client.get('/')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_login_and_role_redirects(client):
    # Admin redirects to /admin/dashboard
    res = client.post('/login', data={'email': 'admin@test.com', 'password': 'Admin@123'})
    assert res.status_code == 302
    assert '/admin/dashboard' in res.headers['Location']
    client.get('/logout')

    # Manager redirects to /reports
    res = client.post('/login', data={'email': 'manager@test.com', 'password': 'Manager@123'})
    assert res.status_code == 302
    assert '/reports' in res.headers['Location']
    client.get('/logout')

    # Staff redirects to /staff/dashboard
    res = client.post('/login', data={'email': 'staff@test.com', 'password': 'Staff@123'})
    assert res.status_code == 302
    assert '/staff/dashboard' in res.headers['Location']
    client.get('/logout')


def test_invalid_login(client):
    res = login(client, 'admin@test.com', 'WrongPass')
    assert b'Invalid email or password.' in res.data


def test_role_based_access_control(client):
    # Staff cannot access admin dashboard or products list or reports
    login(client, 'staff@test.com', 'Staff@123')
    assert client.get('/admin/dashboard').status_code == 403
    assert client.get('/products').status_code == 403
    assert client.get('/reports').status_code == 403
    assert client.get('/staff/dashboard').status_code == 200
    assert client.get('/stock/transaction').status_code == 200
    client.get('/logout')

    # Manager can view products & reports, cannot access admin dashboard or add products
    login(client, 'manager@test.com', 'Manager@123')
    assert client.get('/admin/dashboard').status_code == 403
    assert client.get('/products/add').status_code == 403
    assert client.get('/products').status_code == 200
    assert client.get('/reports').status_code == 200
    assert client.get('/predictions').status_code == 200
    assert client.get('/alerts').status_code == 200
    client.get('/logout')

    # Admin can access admin dashboard, user management, products
    login(client, 'admin@test.com', 'Admin@123')
    assert client.get('/admin/dashboard').status_code == 200
    assert client.get('/admin/users').status_code == 200
    assert client.get('/products').status_code == 200


# --- 2. Product Creation & Stock Transactions (IN and OUT) ---

def test_product_creation_and_transactions(client, app):
    login(client, 'admin@test.com', 'Admin@123')
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    # Create product
    res = client.post('/products/add', data={
        'name': 'Test Router',
        'sku': 'RTR-001',
        'category_id': cat_id,
        'quantity': 50,
        'unit': 'pcs',
        'minimum_threshold': 10,
        'maximum_capacity': 200,
        'purchase_price': '40.00',
        'selling_price': '75.00',
        'supplier': 'NetCorp'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Test Router' in res.data

    with app.app_context():
        product = Product.query.filter_by(sku='RTR-001').first()
        assert product is not None
        assert product.quantity == 50
        p_id = product.id

    # Record Stock IN transaction (+30 -> 80)
    res = client.post('/stock/transaction', data={
        'product_id': p_id,
        'transaction_type': 'IN',
        'quantity': 30,
        'note': 'Restock batch'
    }, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        p = db.session.get(Product, p_id)
        assert p.quantity == 80

    # Record Stock OUT transaction (-25 -> 55)
    res = client.post('/stock/transaction', data={
        'product_id': p_id,
        'transaction_type': 'OUT',
        'quantity': 25,
        'note': 'Customer order'
    }, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        p = db.session.get(Product, p_id)
        assert p.quantity == 55

    # Insufficient stock validation on OUT
    res = client.post('/stock/transaction', data={
        'product_id': p_id,
        'transaction_type': 'OUT',
        'quantity': 100,
        'note': 'Too large'
    }, follow_redirects=True)
    assert b'Insufficient stock' in res.data
    with app.app_context():
        p = db.session.get(Product, p_id)
        assert p.quantity == 55


# --- 3. 30-Day Stockout Prediction & Low-Stock Alert (< 7 days) ---

def test_30_day_prediction_and_low_stock_alert(app):
    with app.app_context():
        cat = Category.query.first()
        admin = User.query.filter_by(role='admin').first()

        # Product with 60 units left, consuming 300 units over last 30 days (10/day -> 6.0 days remaining)
        p = Product(
            name="Fast Moving Item",
            sku="FAST-001",
            category_id=cat.id,
            quantity=60,
            unit="units",
            minimum_threshold=15,
            maximum_capacity=500
        )
        db.session.add(p)
        db.session.commit()

        t1 = StockTransaction(
            product_id=p.id,
            transaction_type='OUT',
            quantity=150,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        t2 = StockTransaction(
            product_id=p.id,
            transaction_type='OUT',
            quantity=150,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        # Transaction older than 30 days should be ignored
        t_old = StockTransaction(
            product_id=p.id,
            transaction_type='OUT',
            quantity=900,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=40)
        )
        # IN transaction should be ignored by consumption calculation
        t_in = StockTransaction(
            product_id=p.id,
            transaction_type='IN',
            quantity=200,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add_all([t1, t2, t_old, t_in])
        db.session.commit()

        pred = calculate_prediction(p.id)
        assert pred is not None
        assert pred.average_daily_consumption == 10.0
        assert pred.predicted_days_remaining == 6.0

        # Since days_remaining (6.0) < 7, a LOW_STOCK alert must be generated
        alerts = Alert.query.filter_by(product_id=p.id, alert_type='LOW_STOCK').all()
        assert len(alerts) == 1
        assert "will run out in 6 days" in alerts[0].message


def test_prediction_above_7_days_does_not_alert(app):
    with app.app_context():
        cat = Category.query.first()
        admin = User.query.filter_by(role='admin').first()

        # Product with 150 units left, consuming 150 units in 30 days (5/day -> 30 days remaining)
        p = Product(
            name="Steady Item",
            sku="STD-001",
            category_id=cat.id,
            quantity=150,
            unit="units",
            minimum_threshold=10,
            maximum_capacity=500
        )
        db.session.add(p)
        db.session.commit()

        t = StockTransaction(
            product_id=p.id,
            transaction_type='OUT',
            quantity=150,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(t)
        db.session.commit()

        pred = calculate_prediction(p.id)
        assert pred is not None
        assert pred.average_daily_consumption == 5.0
        assert pred.predicted_days_remaining == 30.0

        alerts = Alert.query.filter_by(product_id=p.id).all()
        assert len(alerts) == 0


# --- 4. Edge Cases (Zero Consumption, New Product with No Transactions) ---

def test_edge_cases_new_product_and_zero_consumption(app):
    with app.app_context():
        cat = Category.query.first()
        admin = User.query.filter_by(role='admin').first()

        # New product with no transactions at all
        p_new = Product(
            name="Brand New Product",
            sku="NEW-001",
            category_id=cat.id,
            quantity=100,
            unit="pcs",
            minimum_threshold=10,
            maximum_capacity=200
        )
        db.session.add(p_new)
        db.session.commit()

        assert calculate_prediction(p_new.id) is None

        # Product with only IN transactions (zero OUT consumption in last 30 days)
        t_in = StockTransaction(
            product_id=p_new.id,
            transaction_type='IN',
            quantity=50,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        # And an OUT transaction with 0 quantity
        t_zero_out = StockTransaction(
            product_id=p_new.id,
            transaction_type='OUT',
            quantity=0,
            performed_by=admin.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add_all([t_in, t_zero_out])
        db.session.commit()

        assert calculate_prediction(p_new.id) is None
        assert calculate_prediction(999999) is None
        assert run_all_predictions() == []
