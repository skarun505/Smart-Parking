# 🚗 Smart Parking & Tracking System — Cursor Project Spec

> **Stack:** HTML · CSS · JavaScript · Python (Flask) · MySQL · Razorpay  
> **Type:** Full-Stack Web Application  
> **Use Case:** Multi-floor parking management for malls, hospitals & commercial buildings

---

## 📁 Project Folder Structure

```
smart-parking/
├── backend/
│   ├── app.py                    # Flask entry point
│   ├── config.py                 # DB config, secret keys, Razorpay keys
│   ├── models/
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── slot.py
│   │   ├── booking.py
│   │   └── payment.py
│   ├── routes/
│   │   ├── auth.py               # Login, Register, Logout
│   │   ├── user.py               # Dashboard, Booking, Vehicle find
│   │   ├── admin.py              # Admin dashboard, slot mgmt
│   │   └── payment.py            # Razorpay integration
│   ├── utils/
│   │   ├── slot_allocator.py     # Auto slot allocation logic
│   │   ├── scheduler.py          # Cron job for auto-expiry
│   │   └── helpers.py
│   └── requirements.txt
├── frontend/
│   ├── index.html                # Landing / Login page
│   ├── register.html
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── book_slot.html
│   │   ├── find_vehicle.html
│   │   ├── booking_history.html
│   │   └── slot_view.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── live_bookings.html
│   │   ├── manage_slots.html
│   │   ├── add_slot.html
│   │   └── booking_history.html
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   └── admin.css
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       ├── booking.js
│       ├── payment.js
│       ├── find_vehicle.js
│       └── admin.js
├── database/
│   └── schema.sql                # Full DB schema with seed data
├── .env                          # Environment variables
└── README.md
```

---

## 🗄️ Database Schema (`database/schema.sql`)

```sql
CREATE DATABASE IF NOT EXISTS smart_parking;
USE smart_parking;

-- Users Table
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  phone VARCHAR(15),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admins Table
CREATE TABLE admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

-- Slots Table
CREATE TABLE slots (
  id INT AUTO_INCREMENT PRIMARY KEY,
  slot_name VARCHAR(20) NOT NULL,
  floor VARCHAR(10) NOT NULL,
  block_name VARCHAR(20),
  vehicle_type ENUM('Bike', 'Car') NOT NULL,
  slot_type ENUM('VIP', 'Normal') DEFAULT 'Normal',
  status ENUM('Available', 'Occupied', 'Blocked') DEFAULT 'Available'
);

-- Bookings Table
CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  slot_id INT NOT NULL,
  vehicle_number VARCHAR(20) NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  status ENUM('Active', 'Completed', 'Cancelled', 'Expired') DEFAULT 'Active',
  total_amount DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (slot_id) REFERENCES slots(id)
);

-- Payments Table
CREATE TABLE payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  razorpay_order_id VARCHAR(100),
  razorpay_payment_id VARCHAR(100),
  amount DECIMAL(10,2),
  status ENUM('Pending', 'Paid', 'Refunded') DEFAULT 'Pending',
  paid_at TIMESTAMP,
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
```

---

## ⚙️ Backend (`backend/`)

### `requirements.txt`
```
Flask==3.0.0
Flask-MySQLdb==1.0.1
Flask-Login==0.6.3
Flask-CORS==4.0.0
razorpay==1.4.1
bcrypt==4.1.2
python-dotenv==1.0.0
APScheduler==3.10.4
```

---

### `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'smart_parking')
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
    PRICE_PER_HOUR_CAR = 50      # ₹ per hour for car
    PRICE_PER_HOUR_BIKE = 20     # ₹ per hour for bike
    VIP_MULTIPLIER = 1.5
```

---

### `app.py`
```python
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.payment import payment_bp
from utils.scheduler import start_scheduler

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

start_scheduler(app, mysql)   # Auto-expire bookings via cron

if __name__ == '__main__':
    app.run(debug=True)
```

---

### `routes/auth.py`
```python
# Implement the following endpoints:

# POST /api/auth/register
# Body: { name, email, password, phone }
# - Validate email uniqueness
# - Hash password with bcrypt
# - Insert into users table
# - Return: { success, message }

# POST /api/auth/login
# Body: { email, password }
# - Verify credentials
# - Create Flask-Login session
# - Return: { success, role: 'user'|'admin', redirect_url }

# POST /api/auth/logout
# - Clear session
# - Return: { success }
```

---

### `routes/user.py`
```python
# Implement the following endpoints (all require @login_required):

# GET /api/user/dashboard
# - Returns: { bike_total, bike_available, bike_occupied,
#              car_total, car_available, car_occupied,
#              total_slots, available_slots, occupied_slots }

# GET /api/user/slots?status=&vehicle_type=&floor=
# - Filter slots by status, vehicle_type, floor
# - Returns: [ { id, slot_name, floor, block_name, vehicle_type, slot_type, status } ]

# GET /api/user/slots/view
# - Returns all slots grouped: bikes first, then cars
# - Color info: Available=green, Occupied=red, VIP=highlighted

# POST /api/user/book
# Body: { vehicle_number, slot_id, hours }
# - Calculate amount based on hours + vehicle type + VIP
# - Create booking record with status=Active
# - Update slot status to Occupied
# - Return: { booking_id, amount, order_id (Razorpay) }

# POST /api/user/find-vehicle
# Body: { vehicle_number }
# - Query active bookings by vehicle number
# - Return: { found: bool, vehicle_number, slot_number, floor, block_name, vehicle_type }

# GET /api/user/booking-history
# - Returns all bookings for logged-in user
# - Include: slot details, payment info, status

# POST /api/user/booking/cancel
# Body: { booking_id }
# - Only allow if booking status is Active and before start_time
# - Set booking status = Cancelled, slot status = Available

# POST /api/user/booking/extend
# Body: { booking_id, extra_hours }
# - Extend end_time by extra_hours
# - Calculate extra amount, update payment
# - Return new end_time and extra_amount
```

---

### `routes/admin.py`
```python
# Implement the following endpoints (all require admin session):

# GET /api/admin/dashboard
# - Returns: { total_revenue, total_bookings, active_bookings, cancelled_bookings }

# GET /api/admin/bookings/live
# - Returns all active bookings with: slot, vehicle_number, user, vip/normal, expired flag

# POST /api/admin/slots/add
# Body: { slot_name, floor, block_name, vehicle_type, slot_type }
# - Insert new slot

# GET /api/admin/slots
# - Returns all slots with management actions

# POST /api/admin/slots/toggle   # block/unblock slot
# POST /api/admin/slots/edit     # change slot_name or floor
# DELETE /api/admin/slots/delete # remove slot permanently
# POST /api/admin/slots/extend   # add extra time to active booking
# POST /api/admin/slots/cancel   # cancel booking from admin panel

# GET /api/admin/booking-history
# - Full booking history with cancellations and payment info
```

---

### `routes/payment.py`
```python
# Implement the following endpoints:

# POST /api/payment/create-order
# Body: { booking_id, amount }
# - Create Razorpay order
# - Return: { order_id, amount, currency, key_id }

# POST /api/payment/verify
# Body: { razorpay_order_id, razorpay_payment_id, razorpay_signature, booking_id }
# - Verify Razorpay signature with HMAC SHA256
# - If valid: update payment status = Paid, booking status = Active
# - Return: { success, message }

# POST /api/payment/refund
# Body: { booking_id }
# - Trigger Razorpay refund for cancelled bookings
# - Update payment status = Refunded
```

---

### `utils/scheduler.py`
```python
from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler(app, mysql):
    scheduler = BackgroundScheduler()

    def expire_bookings():
        # Every minute: check bookings where end_time < NOW() and status = Active
        # Update those bookings: status = Expired
        # Update their slots: status = Available
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE slots s
                JOIN bookings b ON b.slot_id = s.id
                SET b.status = 'Expired', s.status = 'Available'
                WHERE b.end_time < NOW() AND b.status = 'Active'
            """)
            mysql.connection.commit()

    scheduler.add_job(expire_bookings, 'interval', minutes=1)
    scheduler.start()
```

---

## 🎨 Frontend Pages

### `frontend/index.html` — Login Page
```
Build a clean, modern login page with:
- Logo / App Name "SmartPark" at top
- Email and Password fields
- Login button (calls POST /api/auth/login)
- Link to Register page
- Redirect to /user/dashboard.html if role=user, /admin/dashboard.html if role=admin
- Style: dark navy + green accent color scheme
```

### `frontend/register.html` — Registration Page
```
Build a registration form with:
- Fields: Full Name, Email, Phone, Password, Confirm Password
- Client-side validation (password match, email format, phone 10 digits)
- Calls POST /api/auth/register
- On success: redirect to login page
```

### `frontend/user/dashboard.html` — User Dashboard
```
Build a responsive dashboard with:

STATS CARDS ROW 1 (Bikes):
  [ Bike Total ] [ Bike Available ] [ Bike Occupied ]

STATS CARDS ROW 2 (Cars):
  [ Car Total ] [ Car Available ] [ Car Occupied ]

STATS CARDS ROW 3 (Combined):
  [ Total Slots ] [ Available Slots ] [ Occupied Slots ]

- Cards use green for available, red for occupied counts
- Left sidebar navigation:
    Dashboard | Book Slot | Find My Vehicle | Booking History | Slot View | Logout
- Fetch data from GET /api/user/dashboard on page load
- Auto-refresh every 30 seconds
```

### `frontend/user/slot_view.html` — Slot Visual Map
```
Build a slot map view with:
- Filter bar: Vehicle Type (All / Bike / Car), Floor (All / F1 / F2 / F3), Status (All / Available / Occupied)
- Calls GET /api/user/slots with filters
- Display slots as a CSS grid of colored cards:
    - Available → green card
    - Occupied → red card
    - VIP → gold border highlight
- Each card shows: Slot Name, Floor, Block, Vehicle Type
- Clicking Available slot → opens booking modal
```

### `frontend/user/book_slot.html` — Book a Slot
```
Build a booking form with:
STEP 1 — Enter Details:
  - Vehicle Number (text input, uppercase auto-format)
  - Vehicle Type (Radio: Bike / Car)
  - Select Floor (Dropdown)
  - Select Block / Slot (Dropdown, populated via API based on floor + type)
  - Parking Hours (Number input: 1–24)

STEP 2 — Booking Summary Card:
  - Slot Name, Floor, Block, Vehicle Type
  - Start Time (now), End Time (now + hours)
  - Rate per hour, VIP surcharge if applicable
  - Total Amount (₹)
  - Confirm & Pay button

STEP 3 — Razorpay Payment:
  - Open Razorpay payment modal
  - On success: call POST /api/payment/verify
  - Show confirmation with booking ID and slot number
```

### `frontend/user/find_vehicle.html` — Find My Vehicle
```
Build a vehicle finder page with:
- Single input: Vehicle Registration Number
- "Find Vehicle" button → calls POST /api/user/find-vehicle
- Result card shows:
    ✅ Vehicle Found / ❌ Vehicle Not Found
    Vehicle Number | Slot Number | Floor | Block | Vehicle Type
- Animate result card appearance
```

### `frontend/user/booking_history.html` — Booking History
```
Build a history table with:
- Columns: Booking ID | Vehicle No | Slot | Floor | Block | Type | Start | End | Hours | Amount | Status | Actions
- Status badge colors: Active=green, Completed=grey, Cancelled=red, Expired=orange
- Actions column:
    - Active booking before start_time → [Cancel] button
    - Active booking after start_time → [Extend] button (opens modal to add hours)
- Pagination (10 per page)
- Fetch from GET /api/user/booking-history
```

### `frontend/admin/dashboard.html` — Admin Dashboard
```
Build an admin dashboard with:

TOP STATS:
  [ Total Revenue ₹ ] [ Total Bookings ] [ Active Bookings ] [ Cancelled Bookings ]

CHARTS SECTION:
  - Bar chart: Bookings per day (last 7 days) using Chart.js
  - Doughnut chart: Slot occupancy (Available vs Occupied)

QUICK ACTIONS:
  [ Add New Slot ] [ Live Bookings ] [ Manage Slots ] [ Booking History ]

Admin sidebar:
  Dashboard | Live Bookings | Manage Slots | Add Slot | Booking History | Logout
```

### `frontend/admin/live_bookings.html` — Live Booking Management
```
Build a live bookings page with:
- Real-time table (auto-refresh every 30 sec):
    Slot | Vehicle No | User Name | VIP/Normal | Start | End | Expires In | Status
- "Expires In" column shows countdown timer in red when < 15 min
- Slot visual grid (same as user slot view) showing green/red status
- Action buttons per row:
    [Extend] [Cancel]
```

### `frontend/admin/manage_slots.html` — Manage Parking Slots
```
Build a slot management page with two tabs: Bikes | Cars

Each tab shows a table:
  Slot Name | Floor | Block | VIP/Normal | Status | Actions

Actions per slot:
  [Toggle Block/Unblock] [Edit] [Delete]
  If slot has active booking: [Extend Time] [Cancel Booking]

Edit opens inline form to change slot_name or floor.
All actions call respective admin API endpoints.
```

### `frontend/admin/add_slot.html` — Add New Slot
```
Build a slot creation form with:
- Slot Name (text)
- Floor (Dropdown: Floor 1 / Floor 2 / Floor 3)
- Block Name (text)
- Vehicle Type (Radio: Car / Bike)
- Slot Type (Radio: Normal / VIP)
- [Add Slot] button → calls POST /api/admin/slots/add
- Success toast notification
- Table preview below form showing recently added slots
```

---

## 💳 Razorpay Integration (`frontend/js/payment.js`)

```javascript
// Razorpay Payment Flow:

async function initiatePayment(bookingId, amount) {
  // 1. Call POST /api/payment/create-order to get Razorpay order_id
  const orderRes = await fetch('/api/payment/create-order', {
    method: 'POST',
    body: JSON.stringify({ booking_id: bookingId, amount })
  });
  const order = await orderRes.json();

  // 2. Open Razorpay checkout modal
  const options = {
    key: order.key_id,
    amount: order.amount,
    currency: 'INR',
    name: 'SmartPark',
    description: 'Parking Slot Booking',
    order_id: order.order_id,
    handler: async function (response) {
      // 3. On success, verify payment
      const verifyRes = await fetch('/api/payment/verify', {
        method: 'POST',
        body: JSON.stringify({
          razorpay_order_id: response.razorpay_order_id,
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_signature: response.razorpay_signature,
          booking_id: bookingId
        })
      });
      const result = await verifyRes.json();
      if (result.success) showBookingConfirmation(result);
    },
    prefill: { name: currentUser.name, email: currentUser.email },
    theme: { color: '#1a73e8' }
  };
  new Razorpay(options).open();
}
```

---

## 🎨 CSS Design Guidelines (`frontend/css/style.css`)

```css
/* Color Palette */
:root {
  --primary: #1a1f36;          /* Dark navy background */
  --secondary: #252b4a;        /* Card background */
  --accent: #00c853;           /* Green – available / success */
  --danger: #f44336;           /* Red – occupied / error */
  --warning: #ff9800;          /* Orange – expired */
  --vip: #ffd700;              /* Gold – VIP slots */
  --text-primary: #ffffff;
  --text-secondary: #a0aec0;
  --card-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Slot Cards */
.slot-card.available { background: var(--accent); }
.slot-card.occupied  { background: var(--danger); }
.slot-card.vip       { border: 2px solid var(--vip); }
.slot-card.blocked   { background: #555; opacity: 0.6; }

/* Status Badges */
.badge-active     { background: #00c853; }
.badge-expired    { background: #ff9800; }
.badge-cancelled  { background: #f44336; }
.badge-completed  { background: #607d8b; }
```

---

## 🔐 `.env` File Template

```env
SECRET_KEY=your_flask_secret_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=smart_parking
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXX
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

---

## ✅ Development Checklist

### Phase 1 — Foundation
- [ ] Create MySQL database and run `schema.sql`
- [ ] Set up Flask app with blueprints
- [ ] Implement Auth routes (register, login, logout)
- [ ] Build login and register HTML pages

### Phase 2 — User Features
- [ ] User dashboard with live stats
- [ ] Slot view with color-coded grid + filters
- [ ] Book slot form with summary + Razorpay payment
- [ ] Find My Vehicle page
- [ ] Booking history with cancel/extend

### Phase 3 — Admin Features
- [ ] Admin dashboard with charts
- [ ] Live bookings management table
- [ ] Add / Edit / Delete / Toggle slots
- [ ] Admin booking history with filters

### Phase 4 — Automation & Polish
- [ ] APScheduler cron job for auto-expiry
- [ ] Real-time auto-refresh (every 30 sec) on dashboards
- [ ] Toast notifications for all actions
- [ ] Form validations (client + server side)
- [ ] Responsive mobile layout
- [ ] Loading spinners on API calls

---

## 🚀 Running the Project

```bash
# 1. Set up database
mysql -u root -p < database/schema.sql

# 2. Install Python dependencies
cd backend
pip install -r requirements.txt

# 3. Add your .env file (use template above)
cp .env.example .env
# Fill in your credentials

# 4. Run Flask server
python app.py
# Server starts at http://localhost:5000

# 5. Open frontend
# Open frontend/index.html in browser
# Or serve with: python -m http.server 8080 (from frontend/ folder)
```

---

## 📌 Key Cursor AI Prompts to Use

When building each section, use these prompts in Cursor:

**For backend routes:**
> "Implement the Flask route `[route name]` as described in the spec. Use MySQLdb cursor, return JSON responses, include error handling and input validation."

**For frontend pages:**
> "Build the HTML page `[page name]` as described in the spec. Use vanilla JS with fetch() for API calls, apply the CSS variables from style.css, make it responsive."

**For payment integration:**
> "Implement Razorpay payment flow in payment.js using the create-order and verify endpoints. Include error handling for failed payments."

**For the scheduler:**
> "Implement the APScheduler background job to auto-expire bookings every minute as described in scheduler.py spec."

---

*Built with ❤️ — Smart Parking & Tracking System*