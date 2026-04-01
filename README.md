# 📦 STOCKR — Smart Inventory & Stock Prediction System

![STOCKR Dashboard](https://github.com/Albert101255/Smart-Inventory-System-/raw/main/screenshots/dashboard.png)

## 🎨 Design Philosophy: The Risograph Aesthetic
STOCKR is not just an inventory tool; it's a visual experience. Inspired by **Risograph printing**, the UI features:
- **Cream Grain Texture**: A tactile, paper-like background.
- **Misregistration Effects**: Subtle offsets in typography for a retro-analog feel.
- **Vibrant Spot Colors**: A palette of Riso Navy, Coral, Teal, and Yellow.
- **Custom Cursor**: A ring-and-dot interactive cursor for precise control.

## 🚀 Key Features

### 1. Smart Stock Prediction Engine
Using a rolling average of historical consumption, STOCKR predicts exactly when your products will run out. No more guessing.

### 2. Role-Based Access Control (RBAC)
- **Admin**: Full system control, user management, and global statistics.
- **Manager**: Catalog management, stock history, and reporting.
- **Staff**: Quick floor-ops for recording transactions (IN/OUT/ADJUST).

### 3. Real-Time Alerting
Automated visual and email alerts trigger when stock reaches critical thresholds or depletion dates are near.

### 4. Interactive Data Visualization
Beautiful Chart.js implementations tracking consumption trends, category breakdowns, and stock movement.

## 🛠️ Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLAlchemy (SQLite for development)
- **Frontend**: Vanilla CSS (Custom Design System), JavaScript (Chart.js)
- **Logic**: Custom Prediction Engine for trend analysis.

## 🚀 Quick Start

### 1. Clone the repository:
```bash
git clone https://github.com/Albert101255/Smart-Inventory-System-
cd Smart-Inventory-System-
```

### 2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Seed the Database:
```bash
python seed_data.py
```

### 4. Run the Application:
```bash
python run.py
```

## 🔐 Login Credentials (Seeded)
- **Admin**: `admin@inventory.com` / `Admin@123`
- **Manager**: `manager@inventory.com` / `Manager@123`
- **Staff**: `staff@inventory.com` / `Staff@123`

## 🌐 Deployment: How to Go Live
To make STOCKR accessible from anywhere, we recommend using **Render**:

1. **Connect GitHub**: Create a [Render](https://render.com) account and connect your GitHub repository.
2. **New Web Service**: Select "New" > "Web Service".
3. **Configure**:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
4. **Environment Variables**: Add `DATABASE_URL` (if using PostgreSQL) or keep current SQLite for simple demos.
5. **Auto-Deploy**: Every time you push to the `main` branch, Render will automatically rebuild and update your live site.

---
© 2026 ANTIGRAVITY LABS. Developed with precision and art.
