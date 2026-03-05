document.addEventListener('DOMContentLoaded', () => {
    fetchSlots();

    document.getElementById('filterType').addEventListener('change', fetchSlots);
    document.getElementById('filterFloor').addEventListener('change', fetchSlots);
    document.getElementById('filterStatus').addEventListener('change', fetchSlots);

    setInterval(fetchSlots, 30000);
});

async function fetchSlots() {
    const type = document.getElementById('filterType').value;
    const floor = document.getElementById('filterFloor').value;
    const status = document.getElementById('filterStatus').value;

    const loader = document.getElementById('loader');
    const grid = document.getElementById('slotGrid');

    loader.style.display = 'block';
    grid.innerHTML = '';

    try {
        const query = new URLSearchParams({
            vehicle_type: type,
            floor: floor,
            status: status
        });

        const res = await fetch(`${API_BASE}/user/slots?${query}`);
        const slots = await res.json();

        if (slots.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No slots found for the selected filters.</p>';
        } else {
            slots.forEach(slot => {
                const card = document.createElement('div');
                card.className = `slot-card ${slot.status} ${slot.slot_type === 'VIP' ? 'vip' : ''}`;
                card.innerHTML = `
                    <h3>${slot.slot_name}</h3>
                    <p>${slot.floor} - ${slot.block_name || ''}</p>
                    <p style="margin-top:0.5rem; font-size:0.75rem; font-weight:bold;">${slot.vehicle_type}</p>
                `;

                if (slot.status === 'Available') {
                    card.title = "Click to book this slot";
                    card.addEventListener('click', () => {
                        window.location.href = `book_slot.html?slot_id=${slot.id}`;
                    });
                }

                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error(err);
        showToast('Error loading slots. Try again.', 'error');
    } finally {
        loader.style.display = 'none';
    }
}
