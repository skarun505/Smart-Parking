# Smart Parking & Tracking System

Intelligent multi-floor parking management for malls, hospitals & commercial buildings.

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript
- **Backend**: Python 3, Flask, Flask-Login, Flask-MySQLdb
- **Database**: MySQL
- **Payments**: Razorpay Integration
- **Scheduler**: APScheduler for auto-expiry

## Features
- **User Dashboard**: Live parking status, visual slot booking, real-time availability.
- **Admin Dashboard**: Comprehensive views of active/cancelled bookings, manage slots capacity dynamically.
- **Auto Booking Expiry**: Background cron job marks expired bookings and restores slots.
- **Find My Vehicle**: Search any vehicle's parking location instantly.

## Setup Instructions

### 1. Database Setup
Ensure you have MySQL installed and a running server on localhost.
```bash
mysql -u root -p < database/schema.sql
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env` from template and fill inside the root dir:
```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=smart_parking
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

### 4. Run Application
```bash
cd backend
python app.py
```
Then navigate to `http://localhost:5000` or open `frontend/index.html` in your browser. (Configure CORS and local server for frontend if opening directly via `file://` causes issues).

## Admin credentials
Add an admin user manually in the DB if needed to test admin features, or logic falls back in registering. 
*Note: Depending on DB state, you might need to insert an Admin directly into MySQL:*
```sql
INSERT INTO admins (username, password) VALUES ('admin@smartpark.com', 'admin123');
```
