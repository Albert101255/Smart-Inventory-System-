from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required
from app.products import products
from app.utils import role_required
from app.models import db, Product, Category, StockTransaction
from app.products.forms import ProductForm
import csv
import io

@products.route('/products')
@login_required
@role_required('admin', 'manager')
def list_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_filter = request.args.get('category', 0, type=int)
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.sku.ilike(f'%{search}%'))
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    
    pagination = query.order_by(Product.name).paginate(page=page, per_page=10, error_out=False)
    categories = Category.query.all()
    return render_template('products/list.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        category_filter=category_filter
    )

@products.route('/products/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        if Product.query.filter_by(sku=form.sku.data).first():
            flash('SKU already exists.', 'danger')
        else:
            p = Product(
                name=form.name.data, sku=form.sku.data,
                category_id=form.category_id.data, quantity=form.quantity.data,
                unit=form.unit.data, minimum_threshold=form.minimum_threshold.data,
                maximum_capacity=form.maximum_capacity.data,
                purchase_price=form.purchase_price.data,
                selling_price=form.selling_price.data, supplier=form.supplier.data
            )
            db.session.add(p)
            db.session.commit()
            flash(f'Product "{p.name}" added successfully.', 'success')
            return redirect(url_for('products.list_products'))
    return render_template('products/add.html', form=form)

@products.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        p.name = form.name.data
        p.sku = form.sku.data
        p.category_id = form.category_id.data
        p.unit = form.unit.data
        p.minimum_threshold = form.minimum_threshold.data
        p.maximum_capacity = form.maximum_capacity.data
        p.purchase_price = form.purchase_price.data
        p.selling_price = form.selling_price.data
        p.supplier = form.supplier.data
        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/edit.html', form=form, product=p)

@products.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('products.list_products'))

@products.route('/products/<int:product_id>')
@login_required
@role_required('admin', 'manager')
def product_detail(product_id):
    p = Product.query.get_or_404(product_id)
    history = StockTransaction.query.filter_by(product_id=product_id)\
        .order_by(StockTransaction.created_at.desc()).limit(20).all()
    latest_prediction = p.predictions[-1] if p.predictions else None
    return render_template('products/detail.html', product=p, history=history, prediction=latest_prediction)

@products.route('/products/export')
@login_required
@role_required('admin', 'manager')
def export_products():
    products_all = Product.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['SKU', 'Name', 'Category', 'Quantity', 'Unit', 'Min Threshold', 'Supplier'])
    for p in products_all:
        writer.writerow([p.sku, p.name, p.category.name if p.category else '', p.quantity, p.unit, p.minimum_threshold, p.supplier])
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=products.csv'})
