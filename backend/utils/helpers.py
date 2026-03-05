"""
Helper Utilities
Common helper functions used across routes.
"""

from datetime import datetime
from config import Config


def calculate_amount(vehicle_type, slot_type, hours):
    """
    Calculate the total booking amount.
    
    Args:
        vehicle_type: 'Bike' or 'Car'
        slot_type: 'Normal' or 'VIP'
        hours: number of parking hours
    
    Returns:
        total amount as a float
    """
    base_price = Config.PRICE_PER_HOUR_CAR if vehicle_type == 'Car' else Config.PRICE_PER_HOUR_BIKE
    amount = base_price * hours
    if slot_type == 'VIP':
        amount *= Config.VIP_MULTIPLIER
    return float(amount)


def format_currency(amount):
    """Format a number as Indian Rupees."""
    return f"₹{amount:,.2f}"


def validate_vehicle_number(vehicle_number):
    """
    Basic validation for Indian vehicle registration numbers.
    Returns cleaned/uppercased vehicle number or None if invalid.
    """
    cleaned = vehicle_number.strip().upper().replace(' ', '').replace('-', '')
    if len(cleaned) < 4 or len(cleaned) > 12:
        return None
    return cleaned


def time_remaining(end_time):
    """
    Calculate time remaining until end_time.
    Returns a dict with hours, minutes, and a formatted string.
    """
    now = datetime.now()
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    
    diff = end_time - now
    total_seconds = int(diff.total_seconds())
    
    if total_seconds <= 0:
        return {'hours': 0, 'minutes': 0, 'display': 'Expired', 'expired': True}
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    return {
        'hours': hours,
        'minutes': minutes,
        'display': f"{hours}h {minutes}m",
        'expired': False
    }
