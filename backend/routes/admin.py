from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db, get_id
from datetime import timedelta
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    total_revenue = sum(b['total_amount'] for b in db['bookings'] if b['status'] in ('Active', 'Completed', 'Expired'))
    total_bookings = len(db['bookings'])
    active_bookings = len([b for b in db['bookings'] if b['status'] == 'Active'])
    cancelled_bookings = len([b for b in db['bookings'] if b['status'] == 'Cancelled'])
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings
    })

@admin_bp.route('/bookings/live', methods=['GET'])
@login_required
def live_bookings():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    bookings = []
    for b in db['bookings']:
        if b['status'] == 'Active':
            slot = next((s for s in db['slots'] if s['id'] == b['slot_id']), None)
            user = next((u for u in db['users'] if u['id'] == b['user_id']), None)
            bookings.append({
                'id': b['id'],
                'slot_name': slot['slot_name'] if slot else '',
                'floor': slot['floor'] if slot else '',
                'vehicle_number': b['vehicle_number'],
                'user_name': user['name'] if user else 'Unknown',
                'slot_type': slot['slot_type'] if slot else '',
                'start_time': b['start_time'].isoformat(),
                'end_time': b['end_time'].isoformat(),
                'status': b['status']
            })
            
    return jsonify(bookings)

@admin_bp.route('/slots/add', methods=['POST'])
@login_required
def add_slot():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    new_slot = {
        'id': get_id('slots'),
        'slot_name': data.get('slot_name'),
        'floor': data.get('floor'),
        'block_name': data.get('block_name'),
        'vehicle_type': data.get('vehicle_type'),
        'slot_type': data.get('slot_type', 'Normal'),
        'status': 'Available'
    }
    db['slots'].append(new_slot)
    
    return jsonify({'success': True, 'message': 'Slot added successfully', 'slot': new_slot})

@admin_bp.route('/slots', methods=['GET'])
@login_required
def get_slots():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    slots = sorted(db['slots'], key=lambda x: (x['vehicle_type'], x['floor'], x['slot_name']))
    return jsonify(slots)

@admin_bp.route('/slots/toggle', methods=['POST'])
@login_required
def toggle_slot():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    slot_id = int(request.json.get('slot_id'))
    slot = next((s for s in db['slots'] if s['id'] == slot_id), None)
    
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    
    if slot['status'] == 'Occupied':
        return jsonify({'error': 'Cannot block an occupied slot'}), 400
        
    new_status = 'Blocked' if slot['status'] == 'Available' else 'Available'
    slot['status'] = new_status
    
    return jsonify({'success': True, 'new_status': new_status})

@admin_bp.route('/slots/edit', methods=['POST'])
@login_required
def edit_slot():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    slot_id = int(data.get('slot_id'))
    slot = next((s for s in db['slots'] if s['id'] == slot_id), None)
    
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    
    if 'slot_name' in data and data['slot_name']:
        slot['slot_name'] = data['slot_name']
    if 'floor' in data and data['floor']:
        slot['floor'] = data['floor']
    if 'block_name' in data:
        slot['block_name'] = data['block_name']
    
    return jsonify({'success': True, 'message': 'Slot updated successfully'})

@admin_bp.route('/slots/delete', methods=['POST', 'DELETE'])
@login_required
def delete_slot():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    slot_id = int(request.json.get('slot_id'))
    slot = next((s for s in db['slots'] if s['id'] == slot_id), None)
    
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    
    if slot['status'] == 'Occupied':
        return jsonify({'error': 'Cannot delete an occupied slot. Cancel the booking first.'}), 400
    
    db['slots'].remove(slot)
    return jsonify({'success': True, 'message': 'Slot deleted permanently'})

@admin_bp.route('/slots/extend', methods=['POST'])
@login_required
def extend_booking_admin():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    booking_id = int(data.get('booking_id'))
    extra_hours = int(data.get('extra_hours', 1))
    
    booking = next((b for b in db['bookings'] if b['id'] == booking_id), None)
    if not booking or booking['status'] != 'Active':
        return jsonify({'error': 'Active booking not found'}), 404
    
    slot = next((s for s in db['slots'] if s['id'] == booking['slot_id']), None)
    
    base_price = Config.PRICE_PER_HOUR_CAR if slot['vehicle_type'] == 'Car' else Config.PRICE_PER_HOUR_BIKE
    extra_amount = base_price * extra_hours
    if slot['slot_type'] == 'VIP':
        extra_amount *= Config.VIP_MULTIPLIER
    
    booking['end_time'] += timedelta(hours=extra_hours)
    booking['total_amount'] += extra_amount
    
    return jsonify({
        'success': True,
        'message': f'Extended by {extra_hours}h. Extra ₹{extra_amount}',
        'new_end_time': booking['end_time'].isoformat(),
        'extra_amount': extra_amount
    })

@admin_bp.route('/slots/cancel', methods=['POST'])
@login_required
def cancel_booking_admin():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking_id = int(request.json.get('booking_id'))
    booking = next((b for b in db['bookings'] if b['id'] == booking_id), None)
    
    if not booking or booking['status'] != 'Active':
        return jsonify({'error': 'Active booking not found'}), 404
    
    booking['status'] = 'Cancelled'
    slot = next((s for s in db['slots'] if s['id'] == booking['slot_id']), None)
    if slot:
        slot['status'] = 'Available'
    
    return jsonify({'success': True, 'message': 'Booking cancelled by admin'})

@admin_bp.route('/booking-history', methods=['GET'])
@login_required
def booking_history():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    history = []
    sorted_bookings = sorted(db['bookings'], key=lambda x: x['created_at'], reverse=True)
    for b in sorted_bookings:
        slot = next((s for s in db['slots'] if s['id'] == b['slot_id']), None)
        user = next((u for u in db['users'] if u['id'] == b['user_id']), None)
        payment = next((p for p in db['payments'] if p['booking_id'] == b['id']), None)
        history.append({
            'id': b['id'],
            'vehicle_number': b['vehicle_number'],
            'slot_name': slot['slot_name'] if slot else '',
            'floor': slot['floor'] if slot else '',
            'user_name': user['name'] if user else 'Unknown',
            'start_time': b['start_time'].isoformat(),
            'end_time': b['end_time'].isoformat(),
            'total_amount': float(b['total_amount']),
            'status': b['status'],
            'payment_status': payment['status'] if payment else 'Pending'
        })
    return jsonify(history)
