from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db, get_id
from datetime import datetime, timedelta
from config import Config

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role != 'user':
        return jsonify({'error': 'Unauthorized'}), 403
        
    bikes = [s for s in db['slots'] if s['vehicle_type'] == 'Bike']
    cars = [s for s in db['slots'] if s['vehicle_type'] == 'Car']
    
    bike_total = len(bikes)
    bike_available = len([b for b in bikes if b['status'] == 'Available'])
    bike_occupied = len([b for b in bikes if b['status'] == 'Occupied'])
    
    car_total = len(cars)
    car_available = len([c for c in cars if c['status'] == 'Available'])
    car_occupied = len([c for c in cars if c['status'] == 'Occupied'])
    
    return jsonify({
        'bike_total': bike_total, 'bike_available': bike_available, 'bike_occupied': bike_occupied,
        'car_total': car_total, 'car_available': car_available, 'car_occupied': car_occupied,
        'total_slots': bike_total + car_total,
        'available_slots': bike_available + car_available,
        'occupied_slots': bike_occupied + car_occupied
    })

@user_bp.route('/slots', methods=['GET'])
@login_required
def get_slots():
    status = request.args.get('status', 'All')
    vehicle_type = request.args.get('vehicle_type', 'All')
    floor = request.args.get('floor', 'All')
    
    slots = db['slots']
    
    if status != 'All':
        slots = [s for s in slots if s['status'] == status]
    if vehicle_type != 'All':
        slots = [s for s in slots if s['vehicle_type'] == vehicle_type]
    if floor != 'All':
        slots = [s for s in slots if s['floor'] == floor]
        
    slots = sorted(slots, key=lambda x: (x['vehicle_type'], x['floor'], x['slot_name']))
    return jsonify(slots)

@user_bp.route('/book', methods=['POST'])
@login_required
def book_slot():
    if current_user.role != 'user':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    vehicle_number = data.get('vehicle_number', '').upper()
    slot_id = int(data.get('slot_id'))
    hours = int(data.get('hours', 1))
    
    if not all([vehicle_number, slot_id, hours]):
        return jsonify({'error': 'Missing fields'}), 400
        
    slot = next((s for s in db['slots'] if s['id'] == slot_id), None)
    if not slot or slot['status'] != 'Available':
        return jsonify({'error': 'Slot not available'}), 400
        
    base_price = Config.PRICE_PER_HOUR_CAR if slot['vehicle_type'] == 'Car' else Config.PRICE_PER_HOUR_BIKE
    amount = base_price * hours
    if slot['slot_type'] == 'VIP':
        amount = amount * Config.VIP_MULTIPLIER
        
    now = datetime.now()
    new_booking = {
        'id': get_id('bookings'),
        'user_id': int(current_user.id),
        'slot_id': slot_id,
        'vehicle_number': vehicle_number,
        'start_time': now,
        'end_time': now + timedelta(hours=hours),
        'total_amount': amount,
        'status': 'Active',
        'created_at': now
    }
    db['bookings'].append(new_booking)
    slot['status'] = 'Occupied'
    
    return jsonify({'booking_id': new_booking['id'], 'amount': amount})

@user_bp.route('/find-vehicle', methods=['POST'])
@login_required
def find_vehicle():
    v_num = request.json.get('vehicle_number', '').upper()
    
    booking = next((b for b in db['bookings'] if b['status'] == 'Active' and v_num in b['vehicle_number']), None)
    
    if booking:
        slot = next(s for s in db['slots'] if s['id'] == booking['slot_id'])
        return jsonify({
            'found': True,
            'vehicle_number': booking['vehicle_number'],
            'slot_name': slot['slot_name'],
            'floor': slot['floor'],
            'block_name': slot['block_name'],
            'vehicle_type': slot['vehicle_type']
        })
    return jsonify({'found': False})

@user_bp.route('/booking-history', methods=['GET'])
@login_required
def booking_history():
    if current_user.role != 'user':
        return jsonify({'error': 'Unauthorized'}), 403
        
    user_bookings = [b for b in db['bookings'] if b['user_id'] == int(current_user.id)]
    user_bookings.sort(key=lambda x: x['created_at'], reverse=True)
    
    history = []
    for b in user_bookings:
        slot = next((s for s in db['slots'] if s['id'] == b['slot_id']), None)
        payment = next((p for p in db['payments'] if p['booking_id'] == b['id']), None)
        
        history.append({
            'id': b['id'],
            'vehicle_number': b['vehicle_number'],
            'slot_name': slot['slot_name'] if slot else 'Unknown',
            'floor': slot['floor'] if slot else 'Unknown',
            'block_name': slot['block_name'] if slot else 'Unknown',
            'vehicle_type': slot['vehicle_type'] if slot else 'Unknown',
            'start_time': b['start_time'].isoformat(),
            'end_time': b['end_time'].isoformat(),
            'hours': (b['end_time'] - b['start_time']).total_seconds() / 3600,
            'total_amount': float(b['total_amount']),
            'status': b['status'],
            'payment_status': payment['status'] if payment else 'Pending'
        })
        
    return jsonify(history)

@user_bp.route('/booking/cancel', methods=['POST'])
@login_required
def cancel_booking():
    booking_id = int(request.json.get('booking_id'))
    
    booking = next((b for b in db['bookings'] if b['id'] == booking_id and b['user_id'] == int(current_user.id)), None)
    
    if not booking or booking['status'] != 'Active':
        return jsonify({'error': 'Cannot cancel this booking'}), 400
        
    booking['status'] = 'Cancelled'
    slot = next((s for s in db['slots'] if s['id'] == booking['slot_id']), None)
    if slot:
        slot['status'] = 'Available'
        
    return jsonify({'success': True, 'message': 'Booking cancelled'})

@user_bp.route('/booking/extend', methods=['POST'])
@login_required
def extend_booking():
    booking_id = int(request.json.get('booking_id'))
    extra_hours = int(request.json.get('extra_hours', 1))
    
    booking = next((b for b in db['bookings'] if b['id'] == booking_id and b['user_id'] == int(current_user.id)), None)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
        
    slot = next((s for s in db['slots'] if s['id'] == booking['slot_id']), None)
    
    base_price = Config.PRICE_PER_HOUR_CAR if slot['vehicle_type'] == 'Car' else Config.PRICE_PER_HOUR_BIKE
    extra_amount = base_price * extra_hours
    if slot['slot_type'] == 'VIP':
        extra_amount = extra_amount * Config.VIP_MULTIPLIER
        
    booking['end_time'] += timedelta(hours=extra_hours)
    booking['total_amount'] += extra_amount
    
    return jsonify({'success': True, 'extra_amount': extra_amount})
