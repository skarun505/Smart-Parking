"""
Slot Allocator Utility
Auto-allocates the best available slot based on vehicle type, preferred floor, and slot type.
"""

from database import db


def auto_allocate_slot(vehicle_type, preferred_floor=None, prefer_vip=False):
    """
    Automatically find the best available slot.
    
    Priority order:
    1. Preferred floor + preferred type
    2. Preferred floor + any type
    3. Any floor + preferred type
    4. Any available slot
    
    Args:
        vehicle_type: 'Bike' or 'Car'
        preferred_floor: e.g. 'F1', 'F2', 'F3' (optional)
        prefer_vip: if True, try VIP slots first
    
    Returns:
        slot dict or None if no slot available
    """
    available = [
        s for s in db['slots']
        if s['status'] == 'Available' and s['vehicle_type'] == vehicle_type
    ]

    if not available:
        return None

    # Sort criteria
    def sort_key(slot):
        score = 0
        if preferred_floor and slot['floor'] == preferred_floor:
            score -= 10  # Higher priority (lower score = better)
        if prefer_vip and slot['slot_type'] == 'VIP':
            score -= 5
        elif not prefer_vip and slot['slot_type'] == 'Normal':
            score -= 5
        return score

    available.sort(key=sort_key)
    return available[0] if available else None


def get_occupancy_summary():
    """
    Get a full occupancy summary across all floors.
    Returns a dict keyed by floor with vehicle type breakdowns.
    """
    summary = {}
    for s in db['slots']:
        floor = s['floor']
        if floor not in summary:
            summary[floor] = {
                'bike_total': 0, 'bike_available': 0,
                'car_total': 0, 'car_available': 0
            }
        vtype = s['vehicle_type'].lower()
        summary[floor][f'{vtype}_total'] += 1
        if s['status'] == 'Available':
            summary[floor][f'{vtype}_available'] += 1
    return summary
