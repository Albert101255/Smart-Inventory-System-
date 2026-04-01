from datetime import datetime, timedelta
from app.models import db, Product, StockTransaction, Prediction, Alert, User
from flask_mail import Message
from flask import current_app

def calculate_prediction(product_id):
    """
    Calculate stock prediction for a given product.
    Uses last 30 days of OUT transactions to find average daily consumption.
    """
    product = Product.query.get(product_id)
    if not product:
        return None

    # Get last 30 days of outgoing transactions
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = StockTransaction.query.filter_by(
        product_id=product_id,
        transaction_type='OUT'
    ).filter(
        StockTransaction.created_at >= thirty_days_ago
    ).all()

    if not transactions:
        return None

    # Calculate total consumed in 30 days
    total_consumed = sum(t.quantity for t in transactions)

    # Average daily consumption
    avg_daily = total_consumed / 30

    if avg_daily == 0:
        return None

    # Days remaining
    days_remaining = product.quantity / avg_daily

    # Predicted stockout date
    stockout_date = datetime.utcnow() + timedelta(days=days_remaining)

    # Save to predictions table
    prediction = Prediction(
        product_id=product_id,
        predicted_days_remaining=round(days_remaining, 2),
        average_daily_consumption=round(avg_daily, 2),
        predicted_stockout_date=stockout_date.date()
    )
    db.session.add(prediction)

    # Trigger low stock alert if less than 7 days remaining
    if days_remaining < 7:
        alert_msg = f"{product.name} will run out in {int(days_remaining)} days (approx. {stockout_date.strftime('%d %b %Y')}). Current stock: {product.quantity} {product.unit}."
        alert = Alert(
            product_id=product_id,
            alert_type='LOW_STOCK',
            message=alert_msg
        )
        db.session.add(alert)
        
        # Send email to admin
        send_low_stock_email(product, days_remaining, stockout_date)

    db.session.commit()
    return prediction


def run_all_predictions():
    """Run predictions for all products."""
    products = Product.query.all()
    results = []
    for product in products:
        result = calculate_prediction(product.id)
        if result:
            results.append(result)
    return results

def send_low_stock_email(product, days_remaining, stockout_date):
    """Sends low stock notification email to all admin users."""
    try:
        from app import mail
        admins = User.query.filter_by(role='admin').all()
        recipients = [admin.email for admin in admins]
        
        if not recipients:
            return

        msg = Message(
            subject=f"⚠️ Low Stock Alert — {product.name}",
            recipients=recipients,
            body=f"""Product: {product.name}
SKU: {product.sku}
Current Stock: {product.quantity} {product.unit}
Minimum Threshold: {product.minimum_threshold}
Predicted Stockout Date: {stockout_date.strftime('%d %b %Y')} ({int(days_remaining)} days remaining)

Please restock immediately.

— Smart Inventory System"""
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
