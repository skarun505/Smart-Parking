let slotsData = [];

document.addEventListener('DOMContentLoaded', () => {
    // Check if slot_id is passed in url
    const urlParams = new URLSearchParams(window.location.search);
    const prefillSlotId = urlParams.get('slot_id');

    // Add listeners to all radio buttons
    document.querySelectorAll('input[name="vType"]').forEach(r => {
        r.addEventListener('change', fetchAvailableSlots);
    });
    document.querySelectorAll('input[name="floor"]').forEach(r => {
        r.addEventListener('change', fetchAvailableSlots);
    });

    document.getElementById('calculateBtn').addEventListener('click', calculateAmount);

    // Initial fetch if prefill isn't needed or handle it
    fetchAvailableSlots().then(() => {
        if (prefillSlotId) {
            setTimeout(() => {
                const s = document.getElementById('slotSelect');
                for (let i = 0; i < s.options.length; i++) {
                    if (s.options[i].value === prefillSlotId) {
                        s.selectedIndex = i;
                        break;
                    }
                }
            }, 500);
        }
    });
});

async function fetchAvailableSlots() {
    const vType = document.querySelector('input[name="vType"]:checked').value;
    const floorRadio = document.querySelector('input[name="floor"]:checked');
    const floor = floorRadio ? floorRadio.value : '';
    const slotSelect = document.getElementById('slotSelect');

    if (!floor) {
        slotSelect.innerHTML = '<option value="">Select Floor First</option>';
        slotSelect.disabled = true;
        return;
    }

    slotSelect.disabled = true;
    slotSelect.innerHTML = '<option value="">Loading slots...</option>';

    try {
        const query = new URLSearchParams({
            status: 'Available',
            vehicle_type: vType,
            floor: floor
        });

        const res = await fetch(`${API_BASE}/user/slots?${query}`);
        slotsData = await res.json();

        slotSelect.innerHTML = '<option value="">Select a Slot</option>';
        if (slotsData.length === 0) {
            slotSelect.innerHTML = '<option value="">No available slots</option>';
        } else {
            slotsData.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = `${s.slot_name} ${s.slot_type === 'VIP' ? '(VIP)' : ''}`;
                slotSelect.appendChild(opt);
            });
            slotSelect.disabled = false;
        }
    } catch (err) {
        slotSelect.innerHTML = '<option value="">Error loading slots</option>';
    }
}

async function calculateAmount() {
    const vehicleNumber = document.getElementById('vehicleNumber').value.trim();
    const slotSelect = document.getElementById('slotSelect');
    const hours = document.getElementById('hours').value;

    if (!vehicleNumber || !slotSelect.value || !hours) {
        showToast('Please fill all details', 'error');
        return;
    }

    const selectedSlot = slotsData.find(s => s.id == slotSelect.value);
    if (!selectedSlot) return;

    const vType = selectedSlot.vehicle_type;
    const sType = selectedSlot.slot_type;

    // Base Rates logic matching backend
    const basePrice = vType === 'Car' ? 50 : 20;
    let amount = basePrice * hours;
    if (sType === 'VIP') amount = amount * 1.5;

    // Update Summary
    document.getElementById('sumVehNo').textContent = vehicleNumber.toUpperCase();
    document.getElementById('sumSlotInfo').textContent = `${selectedSlot.slot_name} - ${selectedSlot.floor} (${vType} ${sType === 'VIP' ? 'VIP' : ''})`;
    document.getElementById('sumHours').textContent = hours;
    document.getElementById('sumAmount').textContent = amount;

    document.getElementById('summaryCard').style.display = 'block';

    // Set up payment button
    const payBtn = document.getElementById('payBtn');
    payBtn.onclick = () => initBooking(selectedSlot.id, vehicleNumber, hours);
}

async function initBooking(slotId, vehicleNumber, hours) {
    const payBtn = document.getElementById('payBtn');
    payBtn.disabled = true;
    payBtn.textContent = 'Processing...';

    try {
        // Create booking in backend (Status returns amount and booking_id)
        const res = await fetch(`${API_BASE}/user/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slot_id: slotId, vehicle_number: vehicleNumber, hours: hours })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || 'Failed to initialize booking');
        }

        // Use initiatePayment from payment.js
        if (typeof initiatePayment === 'function') {
            await initiatePayment(data.booking_id, data.amount);
        } else {
            throw new Error('Payment module not loaded');
        }

    } catch (err) {
        showToast(err.message, 'error');
        payBtn.disabled = false;
        payBtn.textContent = 'Confirm & Pay (Dummy)';
    }
}
