# Booking helper model
# Bookings are stored as dictionaries in the in-memory database.
# This file provides helper functions for booking operations.

from database import db


def get_booking_by_id(booking_id):
    """Find a booking by its ID."""
    return next((b for b in db['bookings'] if b['id'] == booking_id), None)


def get_active_bookings():
    """Return all active bookings."""
    return [b for b in db['bookings'] if b['status'] == 'Active']


def get_user_bookings(user_id):
    """Return all bookings for a specific user, sorted by newest first."""
    user_bookings = [b for b in db['bookings'] if b['user_id'] == user_id]
    user_bookings.sort(key=lambda x: x['created_at'], reverse=True)
    return user_bookings


def find_vehicle_booking(vehicle_number):
    """Find an active booking by vehicle number (any user)."""
    return next(
        (b for b in db['bookings']
         if b['status'] == 'Active' and vehicle_number.upper() in b['vehicle_number']),
        None
    )
