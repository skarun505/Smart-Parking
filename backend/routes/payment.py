from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import db, get_id
import datetime

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-order', methods=['POST'])
@login_required
def create_order():
    data = request.json
    booking_id = int(data.get('booking_id'))
    amount = float(data.get('amount'))
    
    # Dummy Gateway Order Creation
    order_id = f"dummy_order_{get_id('payments')}"
    
    db['payments'].append({
        'id': get_id('payments'),
        'booking_id': booking_id,
        'razorpay_order_id': order_id,
        'amount': amount,
        'status': 'Pending'
    })
    
    return jsonify({
        'order_id': order_id,
        'amount': int(amount * 100),
        'currency': 'INR',
        'key_id': 'dummy_key'
    })

@payment_bp.route('/verify', methods=['POST'])
@login_required
def verify_payment():
    data = request.json
    razorpay_order_id = data.get('razorpay_order_id')
    booking_id = int(data.get('booking_id'))
    
    # Dummy logic: just approve it
    payment = next((p for p in db['payments'] if p['razorpay_order_id'] == razorpay_order_id), None)
    if payment:
        payment['status'] = 'Paid'
        payment['paid_at'] = datetime.datetime.now()
        
    booking = next((b for b in db['bookings'] if b['id'] == booking_id), None)
    if booking:
        booking['status'] = 'Active'
        
    return jsonify({'success': True, 'message': 'Payment successful (Dummy)'})
