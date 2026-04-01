from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.admin import admin
from app.utils import role_required
from app.models import db, User, Product, Alert, StockTransaction, Category
from app.admin.forms import UserForm
from datetime import datetime, timedelta

@admin.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Stats for top cards
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.minimum_threshold).count()
    out_of_stock = Product.query.filter(Product.quantity == 0).count()
    unread_alerts = Alert.query.filter_by(is_read=False).count()
    
    today = datetime.utcnow().date()
    today_transactions = StockTransaction.query.filter(
        db.func.date(StockTransaction.created_at) == today
    ).count()
    
    total_categories = Category.query.count()
    
    # Recent transactions (last 5)
    recent_transactions = StockTransaction.query.order_by(
        StockTransaction.created_at.desc()
    ).limit(5).all()
    
    # Unread alerts (last 5)
    recent_alerts = Alert.query.filter_by(is_read=False).order_by(
        Alert.created_at.desc()
    ).limit(5).all()
    
    # Chart data — last 14 days IN vs OUT
    chart_labels = []
    chart_in = []
    chart_out = []
    for i in range(13, -1, -1):
        d = datetime.utcnow().date() - timedelta(days=i)
        chart_labels.append(d.strftime('%d %b'))
        ins = db.session.query(db.func.sum(StockTransaction.quantity)).filter(
            StockTransaction.transaction_type == 'IN',
            db.func.date(StockTransaction.created_at) == d
        ).scalar() or 0
        outs = db.session.query(db.func.sum(StockTransaction.quantity)).filter(
            StockTransaction.transaction_type == 'OUT',
            db.func.date(StockTransaction.created_at) == d
        ).scalar() or 0
        chart_in.append(int(ins))
        chart_out.append(int(outs))

    # Top 5 most consumed products (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    top_consumed = db.session.query(
        Product.name,
        db.func.sum(StockTransaction.quantity).label('total')
    ).join(StockTransaction).filter(
        StockTransaction.transaction_type == 'OUT',
        StockTransaction.created_at >= thirty_days_ago
    ).group_by(Product.id).order_by(db.text('total DESC')).limit(5).all()

    return render_template('admin/dashboard.html',
        total_products=total_products,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        unread_alerts=unread_alerts,
        today_transactions=today_transactions,
        total_categories=total_categories,
        recent_transactions=recent_transactions,
        recent_alerts=recent_alerts,
        chart_labels=chart_labels,
        chart_in=chart_in,
        chart_out=chart_out,
        top_consumed=top_consumed
    )

@admin.route('/users')
@login_required
@role_required('admin')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
        else:
            user = User(
                name=form.name.data,
                email=form.email.data,
                role=form.role.data,
                is_active=form.is_active.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.name} created successfully.', 'success')
            return redirect(url_for('admin.users'))
    return render_template('admin/users.html', form=form, mode='add')

@admin.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/users.html', form=form, user=user, mode='edit')

@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == 1:
        flash('Cannot delete primary admin.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))
