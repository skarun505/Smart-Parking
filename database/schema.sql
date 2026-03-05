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
