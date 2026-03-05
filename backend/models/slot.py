# Slot helper model
# In this project, slots are stored as dictionaries in the in-memory database.
# This file provides helper functions for slot operations.

from database import db


def get_slot_by_id(slot_id):
    """Find a slot by its ID."""
    return next((s for s in db['slots'] if s['id'] == slot_id), None)


def get_available_slots(vehicle_type=None, floor=None):
    """Get all available slots, optionally filtered by type and floor."""
    slots = [s for s in db['slots'] if s['status'] == 'Available']
    if vehicle_type:
        slots = [s for s in slots if s['vehicle_type'] == vehicle_type]
    if floor:
        slots = [s for s in slots if s['floor'] == floor]
    return slots


def get_slot_counts():
    """Return a breakdown of total/available/occupied for bikes and cars."""
    bikes = [s for s in db['slots'] if s['vehicle_type'] == 'Bike']
    cars = [s for s in db['slots'] if s['vehicle_type'] == 'Car']
    return {
        'bike_total': len(bikes),
        'bike_available': len([b for b in bikes if b['status'] == 'Available']),
        'bike_occupied': len([b for b in bikes if b['status'] == 'Occupied']),
        'car_total': len(cars),
        'car_available': len([c for c in cars if c['status'] == 'Available']),
        'car_occupied': len([c for c in cars if c['status'] == 'Occupied']),
    }
