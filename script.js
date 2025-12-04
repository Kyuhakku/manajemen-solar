// Load status on page load
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update UI
        document.getElementById('stokSaatIni').textContent = data.stok_saat_ini.toFixed(0);
        document.getElementById('batasGudang').textContent = data.batas_gudang.toLocaleString('id-ID');
        document.getElementById('persentaseText').textContent = data.persentase_kapasitas.toFixed(1) + '%';
        
        // Update capacity bar
        const capacityFill = document.getElementById('capacityFill');
        capacityFill.style.width = data.persentase_kapasitas + '%';
        
        // Change color based on capacity
        if (data.persentase_kapasitas > 80) {
            capacityFill.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
        } else if (data.persentase_kapasitas > 50) {
            capacityFill.style.background = 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)';
        } else {
            capacityFill.style.background = 'linear-gradient(90deg, #10b981 0%, #059669 100%)';
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Toggle PO form
const btnPOStok = document.getElementById('btnPOStok');
const formPO = document.getElementById('formPO');

if (btnPOStok && formPO) {
    btnPOStok.addEventListener('click', () => {
        formPO.classList.toggle('active');
    });
}

// Submit PO
const btnSubmitPO = document.getElementById('btnSubmitPO');
if (btnSubmitPO) {
    btnSubmitPO.addEventListener('click', async () => {
        const volume = parseFloat(document.getElementById('volumePO').value);
        
        if (!volume || volume <= 0) {
            alert('Masukkan volume yang valid!');
            return;
        }

        try {
            const response = await fetch('/api/po', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ volume })
            });

            const data = await response.json();

            if (response.ok) {
                alert(`PO berhasil disimpan! Stok sekarang: ${data.new_stock.toFixed(2)} L`);
                document.getElementById('volumePO').value = '';
                formPO.classList.remove('active');
                loadStatus();
            } else {
                alert(data.error || 'Terjadi kesalahan');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    });
}

// Initialize
loadStatus();
setInterval(loadStatus, 30000); // Refresh every 30 seconds