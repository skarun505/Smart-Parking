document.addEventListener('DOMContentLoaded', () => {
    fetchHistory();

    // Setup modal closing
    document.getElementById('closeExtend').addEventListener('click', () => {
        document.getElementById('extendModal').classList.remove('active');
    });

    document.getElementById('confirmExtendBtn').addEventListener('click', confirmExtend);
});

async function fetchHistory() {
    const loader = document.getElementById('loader');
    const tbody = document.querySelector('#historyTable tbody');

    loader.style.display = 'block';
    tbody.innerHTML = '';

    try {
        const res = await fetch(`${API_BASE}/user/booking-history`);
        const data = await res.json();

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align: center;">No bookings found.</td></tr>`;
        } else {
            data.forEach(b => {
                const tr = document.createElement('tr');

                // Active status check vs start time for cancel
                const now = new Date();
                const startTime = new Date(b.start_time);

                let actions = '-';
                if (b.status === 'Active') {
                    if (now < startTime) {
                        actions = `<button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="cancelBooking(${b.id})">Cancel</button>`;
                    } else {
                        actions = `<button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="openExtendModal(${b.id})">Extend</button>`;
                    }
                }

                tr.innerHTML = `
                    <td>#${b.id}</td>
                    <td>${b.vehicle_number}</td>
                    <td>${b.slot_name} (${b.floor})</td>
                    <td>${b.vehicle_type}</td>
                    <td>${new Date(b.start_time).toLocaleString()}</td>
                    <td>${new Date(b.end_time).toLocaleString()}</td>
                    <td>₹${parseFloat(b.total_amount).toFixed(2)}</td>
                    <td><span class="badge badge-${b.status}">${b.status}</span></td>
                    <td>${actions}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        showToast('Error loading history', 'error');
    } finally {
        loader.style.display = 'none';
    }
}

async function cancelBooking(id) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;

    try {
        const res = await fetch(`${API_BASE}/user/booking/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: id })
        });

        const data = await res.json();
        if (data.success) {
            showToast('Booking cancelled successfully', 'success');
            fetchHistory(); // Refresh
        } else {
            showToast(data.error || 'Failed to cancel', 'error');
        }
    } catch (err) {
        showToast('Server error', 'error');
    }
}

function openExtendModal(id) {
    document.getElementById('extBookingId').value = id;
    document.getElementById('extHours').value = 1;
    document.getElementById('extendModal').classList.add('active');
}

async function confirmExtend() {
    const id = document.getElementById('extBookingId').value;
    const hours = document.getElementById('extHours').value;
    const btn = document.getElementById('confirmExtendBtn');

    btn.disabled = true;
    btn.textContent = 'Processing...';

    try {
        const res = await fetch(`${API_BASE}/user/booking/extend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: id, extra_hours: hours })
        });

        const data = await res.json();
        if (data.success) {
            // Note: In reality, we'd trigger Razorpay here for the `data.extra_amount`
            // For simplicity in UI logic:
            showToast(`Extended! Additional ₹${data.extra_amount} deducted`, 'success');
            document.getElementById('extendModal').classList.remove('active');
            fetchHistory();
        } else {
            showToast(data.error || 'Failed to extend', 'error');
        }
    } catch (err) {
        showToast('Server error', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Extend & Pay Difference';
    }
}
