from werkzeug.security import generate_password_hash
from datetime import datetime

db = {
    'users': [
        {'id': 100, 'name': 'Demo User', 'email': 'user@smartpark.com', 'password': generate_password_hash('user123'), 'phone': '1234567890'}
    ],
    'admins': [
        {'id': 1, 'username': 'admin@smartpark.com', 'password': 'admin123'}
    ],
    'slots': [],
    'bookings': [],
    'payments': []
}

counters = {
    'users': 1,
    'slots': 1,
    'bookings': 1,
    'payments': 1
}

def get_id(table):
    c = counters[table]
    counters[table] += 1
    return c

def seed_db():
    """Seed the database with multi-floor parking slots for demo purposes."""
    if not db['slots']:
        # ── Floor 1: Block A ──
        # 10 Bike slots
        for i in range(1, 11):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'B{i}', 'floor': 'F1', 'block_name': 'A',
                'vehicle_type': 'Bike', 'slot_type': 'VIP' if i <= 2 else 'Normal', 'status': 'Available'
            })
        # 8 Car slots
        for i in range(1, 9):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'C{i}', 'floor': 'F1', 'block_name': 'A',
                'vehicle_type': 'Car', 'slot_type': 'VIP' if i <= 2 else 'Normal', 'status': 'Available'
            })

        # ── Floor 2: Block B ──
        # 8 Bike slots
        for i in range(1, 9):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'B{10+i}', 'floor': 'F2', 'block_name': 'B',
                'vehicle_type': 'Bike', 'slot_type': 'Normal', 'status': 'Available'
            })
        # 8 Car slots
        for i in range(1, 9):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'C{8+i}', 'floor': 'F2', 'block_name': 'B',
                'vehicle_type': 'Car', 'slot_type': 'VIP' if i <= 1 else 'Normal', 'status': 'Available'
            })

        # ── Floor 3: Block C ──
        # 6 Bike slots
        for i in range(1, 7):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'B{18+i}', 'floor': 'F3', 'block_name': 'C',
                'vehicle_type': 'Bike', 'slot_type': 'Normal', 'status': 'Available'
            })
        # 6 Car slots
        for i in range(1, 7):
            db['slots'].append({
                'id': get_id('slots'), 'slot_name': f'C{16+i}', 'floor': 'F3', 'block_name': 'C',
                'vehicle_type': 'Car', 'slot_type': 'VIP' if i <= 1 else 'Normal', 'status': 'Available'
            })

seed_db()
