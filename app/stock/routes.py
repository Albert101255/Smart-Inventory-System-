from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from app.stock import stock
from app.utils import role_required
from app.models import db, Product, StockTransaction, Alert, User
from app.stock.forms import TransactionForm
from app.prediction_engine import calculate_prediction, run_all_predictions
from datetime import datetime, timedelta
import csv, io

@stock.route('/stock/transaction', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'staff')
def transaction():
    form = TransactionForm()
    form.product_id.choices = [(p.id, f"{p.name} ({p.sku}) — Stock: {p.quantity}") for p in Product.query.order_by(Product.name).all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        qty = form.quantity.data
        t_type = form.transaction_type.data
        
        # Stock validation
        if t_type == 'OUT' and product.quantity < qty:
            flash(f'Insufficient stock. Only {product.quantity} {product.unit} available.', 'danger')
            return render_template('stock/transaction.html', form=form)
        
        # Update quantity
        if t_type == 'IN':
            product.quantity += qty
        elif t_type == 'OUT':
            product.quantity -= qty
        elif t_type == 'ADJUSTMENT':
            product.quantity = qty  # Set absolute value
        
        # Record transaction
        t = StockTransaction(
            product_id=product.id,
            transaction_type=t_type,
            quantity=qty,
            note=form.note.data,
            performed_by=current_user.id
        )
        db.session.add(t)
        
        # Check for out-of-stock alert
        if product.quantity == 0:
            alert = Alert(
                product_id=product.id,
                alert_type='OUT_OF_STOCK',
                message=f"{product.name} (SKU: {product.sku}) is now OUT OF STOCK."
            )
            db.session.add(alert)
        elif product.quantity <= product.minimum_threshold:
            alert = Alert(
                product_id=product.id,
                alert_type='LOW_STOCK',
                message=f"{product.name} is below minimum threshold. Current: {product.quantity} {product.unit}. Minimum: {product.minimum_threshold}."
            )
            db.session.add(alert)
        
        db.session.commit()
        
        # Run prediction after OUT transaction
        if t_type == 'OUT':
            calculate_prediction(product.id)
        
        flash(f'Transaction recorded. {product.name} stock is now {product.quantity} {product.unit}.', 'success')
        return redirect(url_for('stock.transaction'))
    
    return render_template('stock/transaction.html', form=form)

@stock.route('/staff/dashboard')
@login_required
@role_required('staff')
def staff_dashboard():
    form = TransactionForm()
    form.product_id.choices = [(p.id, f"{p.name} — Stock: {p.quantity} {p.unit}") for p in Product.query.order_by(Product.name).all()]
    recent = StockTransaction.query.filter_by(performed_by=current_user.id)\
        .order_by(StockTransaction.created_at.desc()).limit(5).all()
    return render_template('staff/dashboard.html', form=form, recent=recent)

@stock.route('/stock/history')
@login_required
@role_required('admin', 'manager')
def history():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    t_type = request.args.get('type', '')
    
    query = StockTransaction.query
    if search:
        query = query.join(Product).filter(Product.name.ilike(f'%{search}%'))
    if t_type:
        query = query.filter_by(transaction_type=t_type)
    
    pagination = query.order_by(StockTransaction.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('stock/history.html', transactions=pagination.items, pagination=pagination, search=search, type_filter=t_type)

@stock.route('/stock/history/export')
@login_required
@role_required('admin', 'manager')
def export_history():
    transactions = StockTransaction.query.order_by(StockTransaction.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Product', 'SKU', 'Type', 'Quantity', 'Note', 'Performed By'])
    for t in transactions:
        performer = User.query.get(t.performed_by)
        writer.writerow([
            t.created_at.strftime('%Y-%m-%d %H:%M'),
            t.product.name, t.product.sku,
            t.transaction_type, t.quantity, t.note or '',
            performer.name if performer else ''
        ])
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=transactions.csv'})
