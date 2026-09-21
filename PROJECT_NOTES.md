# Project Recall — STOCKR

## One-line explanation
Flask inventory system that estimates stockout dates using the last 30 days of outgoing stock transactions.

## Prediction formula
total consumed in last 30 days / 30 = average daily consumption

current quantity / average daily consumption = estimated days remaining

If estimated days remaining < 7, the system creates a low-stock alert and can email admins.

## Important limitation
This is a simple historical average, not machine learning or advanced demand forecasting.

## Main technical pieces
- Flask
- SQLAlchemy
- Role-based workflows
- Stock transactions
- Prediction table
- Alerts
- Flask-Mail
- Chart.js

## Interview questions
1. Why use OUT transactions only?
2. What happens when there are no recent transactions?
3. What assumptions does a 30-day average make?
4. How would seasonality break this model?
5. How would you evaluate prediction quality?

## Next improvements
- Tests
- Configurable prediction window
- Forecast evaluation
- PostgreSQL deployment
