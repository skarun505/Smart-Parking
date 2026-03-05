// Dummy Payment Flow wrapper
async function initiatePayment(bookingId, amount) {
    try {
        const orderRes = await fetch(`${API_BASE}/payment/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: bookingId, amount })
        });
        const order = await orderRes.json();

        if (!orderRes.ok) throw new Error(order.error || 'Could not create order');

        // Instead of asking Razorpay, we show a native confirm for UI dummy flow
        const userConfirm = confirm(`[DUMMY PAYMENT GATEWAY]\n\nDo you want to pay ₹${amount} for Booking #${bookingId}?`);

        if (userConfirm) {
            const verifyRes = await fetch(`${API_BASE}/payment/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    razorpay_order_id: order.order_id,
                    razorpay_payment_id: "dummy_pay_" + Date.now(),
                    razorpay_signature: "dummy_signature",
                    booking_id: bookingId
                })
            });
            const result = await verifyRes.json();

            if (result.success) {
                showToast('Payment successful! Your slot is booked.', 'success');
                setTimeout(() => {
                    window.location.href = 'booking_history.html';
                }, 2000);
            } else {
                showToast(result.message || 'Payment verification failed', 'error');
            }
        } else {
            showToast('Payment cancelled by user', 'warning');
            const payBtn = document.getElementById('payBtn');
            if (payBtn) {
                payBtn.disabled = false;
                payBtn.textContent = 'Confirm & Pay (Dummy)';
            }
        }
    } catch (err) {
        console.error(err);
        showToast(err.message || 'Payment Initiation Failed', 'error');
        const payBtn = document.getElementById('payBtn');
        if (payBtn) {
            payBtn.disabled = false;
            payBtn.textContent = 'Confirm & Pay (Dummy)';
        }
    }
}
