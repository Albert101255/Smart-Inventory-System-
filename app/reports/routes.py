from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.reports import reports
from app.utils import role_required
from app.models import db, Product, Alert, Prediction, StockTransaction, Category
from app.prediction_engine import run_all_predictions
from datetime import datetime, timedelta

@reports.route('/reports')
@login_required
@role_required('admin', 'manager')
def reports_page():
    # Low stock products
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.minimum_threshold
    ).all()
    
    out_of_stock = Product.query.filter(Product.quantity == 0).all()
    
    # Category breakdown for doughnut chart
    categories = Category.query.all()
    cat_labels = [c.name for c in categories]
    cat_values = []
    for c in categories:
        total = sum(p.quantity for p in c.products)
        cat_values.append(total)
    
    # 30-day consumption by product for bar chart
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    top_consumed = db.session.query(
        Product.name,
        db.func.sum(StockTransaction.quantity).label('total')
    ).join(StockTransaction).filter(
        StockTransaction.transaction_type == 'OUT',
        StockTransaction.created_at >= thirty_days_ago
    ).group_by(Product.id).order_by(db.text('total DESC')).limit(8).all()
    
    return render_template('reports/reports.html',
        low_stock_products=low_stock_products,
        out_of_stock=out_of_stock,
        cat_labels=cat_labels,
        cat_values=cat_values,
        top_consumed=top_consumed
    )

@reports.route('/predictions')
@login_required
@role_required('admin', 'manager')
def predictions_page():
    # Re-run predictions for fresh data
    run_all_predictions()
    
    # Get latest prediction per product
    products = Product.query.all()
    prediction_data = []
    for p in products:
        latest = Prediction.query.filter_by(product_id=p.id)\
            .order_by(Prediction.calculated_at.desc()).first()
        if latest:
            prediction_data.append({
                'product': p,
                'prediction': latest,
                'status': 'critical' if latest.predicted_days_remaining < 7
                          else 'warning' if latest.predicted_days_remaining < 14
                          else 'ok'
            })
    
    # Sort by days remaining ascending (most urgent first)
    prediction_data.sort(key=lambda x: x['prediction'].predicted_days_remaining)
    
    return render_template('reports/predictions.html', prediction_data=prediction_data)

@reports.route('/alerts')
@login_required
@role_required('admin', 'manager')
def alerts_page():
    page = request.args.get('page', 1, type=int)
    show_read = request.args.get('show_read', False, type=bool)
    
    query = Alert.query
    if not show_read:
        query = query.filter_by(is_read=False)
    
    pagination = query.order_by(Alert.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    unread_count = Alert.query.filter_by(is_read=False).count()
    
    return render_template('reports/alerts.html',
        alerts=pagination.items,
        pagination=pagination,
        unread_count=unread_count,
        show_read=show_read
    )

@reports.route('/alerts/dismiss/<int:alert_id>', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def dismiss_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    flash('Alert dismissed.', 'success')
    return redirect(url_for('reports.alerts_page'))

@reports.route('/alerts/dismiss-all', methods=['POST'])
@login_required
@role_required('admin', 'manager')
def dismiss_all_alerts():
    Alert.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All alerts dismissed.', 'success')
    return redirect(url_for('reports.alerts_page'))
