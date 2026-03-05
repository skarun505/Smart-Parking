# Payment helper model
# Payments are stored as dictionaries in the in-memory database.
# This file provides helper functions for payment operations.

from database import db


def get_payment_by_booking_id(booking_id):
    """Find a payment record by booking ID."""
    return next((p for p in db['payments'] if p['booking_id'] == booking_id), None)


def get_payment_by_order_id(order_id):
    """Find a payment record by Razorpay order ID."""
    return next((p for p in db['payments'] if p['razorpay_order_id'] == order_id), None)
