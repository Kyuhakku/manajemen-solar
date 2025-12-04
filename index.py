from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Initialize Firebase
try:
    cred = credentials.Certificate('firebase-key.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL', 'https://your-project-id.firebaseio.com')
    })
except:
    pass

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

# API Endpoints
@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        ref = db.reference('solar')
        data = ref.get()
        
        if not data:
            data = {
                'stok_saat_ini': 0,
                'batas_gudang': 10000,
                'persentase_kapasitas': 0.0
            }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/po', methods=['POST'])
def create_po():
    try:
        data = request.json
        volume = float(data.get('volume', 0))
        
        # Get current stock
        ref = db.reference('solar')
        current_data = ref.get() or {'stok_saat_ini': 0, 'batas_gudang': 10000}
        
        new_stock = current_data['stok_saat_ini'] + volume
        persentase = (new_stock / current_data['batas_gudang']) * 100
        
        # Update stock
        ref.update({
            'stok_saat_ini': new_stock,
            'persentase_kapasitas': round(persentase, 2)
        })
        
        # Save transaction
        transaction = {
            'type': 'PO',
            'volume': volume,
            'timestamp': datetime.now().isoformat(),
            'stok_setelah': new_stock
        }
        
        trans_ref = db.reference('transactions')
        trans_ref.push(transaction)
        
        return jsonify({'success': True, 'new_stock': new_stock})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        volume = float(data.get('volume', 0))
        
        # Get current stock
        ref = db.reference('solar')
        current_data = ref.get() or {'stok_saat_ini': 0, 'batas_gudang': 10000}
        
        if current_data['stok_saat_ini'] < volume:
            return jsonify({'error': 'Stok tidak mencukupi'}), 400
        
        new_stock = current_data['stok_saat_ini'] - volume
        persentase = (new_stock / current_data['batas_gudang']) * 100
        
        # Update stock
        ref.update({
            'stok_saat_ini': new_stock,
            'persentase_kapasitas': round(persentase, 2)
        })
        
        # Save transaction
        transaction = {
            'type': 'ORDER',
            'volume': volume,
            'timestamp': datetime.now().isoformat(),
            'stok_setelah': new_stock
        }
        
        trans_ref = db.reference('transactions')
        trans_ref.push(transaction)
        
        return jsonify({'success': True, 'new_stock': new_stock})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        ref = db.reference('transactions')
        data = ref.get()
        
        if not data:
            return jsonify([])
        
        transactions = []
        for key, value in data.items():
            value['id'] = key
            transactions.append(value)
        
        # Sort by timestamp descending
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)