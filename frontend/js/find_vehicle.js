document.getElementById('searchBtn').addEventListener('click', async () => {
    const vNum = document.getElementById('searchInput').value.trim();
    if (!vNum) {
        showToast('Please enter a vehicle number', 'error');
        return;
    }

    const loader = document.getElementById('searchLoader');
    const resultCard = document.getElementById('resultCard');
    const resultContent = document.getElementById('resultContent');

    loader.style.display = 'block';
    resultCard.classList.remove('active');

    try {
        const res = await fetch(`${API_BASE}/user/find-vehicle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vehicle_number: vNum })
        });

        const data = await res.json();

        if (data.found) {
            resultContent.innerHTML = `
                <h2 style="color: var(--accent); margin-bottom: 1rem;">✅ Vehicle Found</h2>
                <div style="text-align: left; background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 8px;">
                    <p><strong>Vehicle No:</strong> ${data.vehicle_number}</p>
                    <p><strong>Slot Name:</strong> <span style="font-size: 1.2rem; font-weight: bold; color: var(--vip);">${data.slot_name}</span></p>
                    <p><strong>Floor:</strong> ${data.floor}</p>
                    <p><strong>Block:</strong> ${data.block_name || 'N/A'}</p>
                    <p><strong>Type:</strong> ${data.vehicle_type}</p>
                </div>
            `;
            resultCard.style.borderLeft = "4px solid var(--accent)";
        } else {
            resultContent.innerHTML = `
                <h2 style="color: var(--danger); margin-bottom: 1rem;">❌ Not Found</h2>
                <p>No active booking found for vehicle <strong>${vNum.toUpperCase()}</strong>.</p>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 1rem;">Please check the number or verify if the booking has expired.</p>
            `;
            resultCard.style.borderLeft = "4px solid var(--danger)";
        }

        resultCard.classList.add('active');

    } catch (err) {
        console.error(err);
        showToast('Error searching vehicle', 'error');
    } finally {
        loader.style.display = 'none';
    }
});
