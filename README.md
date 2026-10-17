# STOCKR — Smart Inventory & Stock Prediction System

> **Live Interactive Demo:** [https://albert101255.github.io/Smart-Inventory-System-/](https://albert101255.github.io/Smart-Inventory-System-/)

A Flask inventory application with role-based stock management, reporting and a simple historical-consumption stockout estimator.

## Try it in your browser

Explore the live interactive Risograph UI sandbox at **[https://albert101255.github.io/Smart-Inventory-System-/](https://albert101255.github.io/Smart-Inventory-System-/)** — switch between Dashboard, Products, Stock IN/OUT Transactions, 30-Day Stockout Predictions, and Low-Stock Alerts, and record simulated transactions to watch the 30-day stockout velocity recalculate in real time.

## What it does

- Manage products and stock transactions
- Record IN / OUT / ADJUST operations
- Separate admin, manager and staff workflows
- Visualize inventory activity
- Estimate how many days of stock remain
- Create low-stock alerts
- Send admin email notifications when configured

## Stock prediction logic

The prediction engine is deliberately simple and explainable.

For each product it:

1. Reads **OUT transactions from the last 30 days**.
2. Calculates total units consumed.
3. Divides by 30 to estimate average daily consumption.
4. Calculates:

```text
days_remaining = current_quantity / average_daily_consumption
```

5. Estimates a stockout date from that value.
6. Creates a low-stock alert when the estimate falls below 7 days.

This is a rolling historical-consumption estimate, **not a machine-learning forecasting model**. It does not currently model seasonality, promotions, demand shocks or irregular consumption patterns.

## Technology

- Python
- Flask
- SQLAlchemy
- SQLite for local development / PostgreSQL via Docker Compose
- Chart.js
- HTML/CSS/JavaScript
- Flask-Mail for configured email alerts

## Run locally

```bash
git clone https://github.com/Albert101255/Smart-Inventory-System-.git
cd Smart-Inventory-System-

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python seed_data.py
python run.py
```

## Development accounts

The seed script creates local demonstration users. Treat all seeded credentials as local-development credentials only; never reuse them for a public deployment.

## Design

The UI uses a risograph-inspired visual style with grain textures, strong spot colors and custom interaction details.
