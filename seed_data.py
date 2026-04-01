import os
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Category, Product, StockTransaction, Alert, Prediction

def seed_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Creating users...")
        admin = User(name="Admin User", email="admin@inventory.com", role="admin")
        admin.set_password("Admin@123")
        
        manager = User(name="Manager User", email="manager@inventory.com", role="manager")
        manager.set_password("Manager@123")
        
        staff = User(name="Staff User", email="staff@inventory.com", role="staff")
        staff.set_password("Staff@123")
        
        db.session.add_all([admin, manager, staff])
        db.session.commit()

        print("Creating categories...")
        categories = [
            Category(name="Electronics", description="Gadgets, devices and accessories"),
            Category(name="Stationery", description="Office and school supplies"),
            Category(name="Food & Beverage", description="Packaged food and drinks"),
            Category(name="Cleaning Supplies", description="Detergents and tools"),
            Category(name="Furniture", description="Office and home furniture")
        ]
        db.session.add_all(categories)
        db.session.commit()

        print("Creating products...")
        product_data = [
            ("Laptop Pro x1", "LAP-001", 1, 50, "pcs", 10, 100, 800, 1200, "TechWorld"),
            ("Wireless Mouse", "MOU-001", 1, 150, "pcs", 20, 300, 15, 35, "LogiSupplies"),
            ("A4 Paper Box", "PAP-001", 2, 200, "boxes", 30, 500, 20, 30, "PaperCo"),
            ("Ballpoint Pen Blue", "PEN-001", 2, 1000, "units", 100, 2000, 0.5, 1, "InkMaster"),
            ("Mineral Water 500ml", "WAT-001", 3, 500, "bottles", 50, 1000, 0.2, 0.5, "AquaPure"),
            ("Espresso Beans 1kg", "COF-001", 3, 40, "bags", 10, 100, 12, 25, "BeanRoast"),
            ("Disinfectant Spray", "CLE-001", 4, 80, "bottles", 15, 200, 5, 12, "EcoClean"),
            ("Microfiber Cloth", "CLE-002", 4, 300, "pcs", 50, 1000, 1, 3, "EcoClean"),
            ("Office Chair", "FUR-001", 5, 20, "units", 5, 50, 60, 150, "ComfortSeat"),
            ("Desk Lamp", "FUR-002", 5, 45, "units", 10, 100, 25, 55, "LightHouse")
        ]

        products = []
        for name, sku, cat_id, qty, unit, min_t, max_c, p_price, s_price, supp in product_data:
            p = Product(
                name=name, sku=sku, category_id=cat_id, quantity=qty, unit=unit,
                minimum_threshold=min_t, maximum_capacity=max_c,
                purchase_price=p_price, selling_price=s_price, supplier=supp
            )
            db.session.add(p)
            products.append(p)
        db.session.commit()

        print("Creating 60 days of historical transactions...")
        now = datetime.utcnow()
        for product in products:
            # Starting quantity was actually higher before 60 days
            # Let's simulate a baseline
            running_qty = product.quantity + 300 
            
            for d in range(60, 0, -1):
                date = now - timedelta(days=d)
                
                # Randomized outgoing transactions
                # Some products consume more than others
                if product.category_id == 3: # Food/Drink (High consumption)
                    out_qty = random.randint(5, 15)
                elif product.category_id == 2: # Stationery (Medium)
                    out_qty = random.randint(2, 10)
                else:
                    out_qty = random.randint(0, 5)
                
                if out_qty > 0 and running_qty >= out_qty:
                    running_qty -= out_qty
                    t_out = StockTransaction(
                        product_id=product.id,
                        transaction_type='OUT',
                        quantity=out_qty,
                        note=f"Daily sale simulation",
                        performed_by=random.choice([admin.id, staff.id]),
                        created_at=date + timedelta(hours=random.randint(9, 17))
                    )
                    db.session.add(t_out)
                
                # Occasional restock (IN)
                if running_qty < product.minimum_threshold * 2:
                    in_qty = random.randint(50, 100)
                    running_qty += in_qty
                    t_in = StockTransaction(
                        product_id=product.id,
                        transaction_type='IN',
                        quantity=in_qty,
                        note=f"Monthly restock simulation",
                        performed_by=admin.id,
                        created_at=date + timedelta(hours=8)
                    )
                    db.session.add(t_in)

            # Update final quantity to match simulation
            product.quantity = running_qty
        
        db.session.commit()
        print("Data seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
