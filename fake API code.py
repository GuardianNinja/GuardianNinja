from flask import Flask, request, jsonify
import math
import hashlib  # For fake QR DNA hash

app = Flask(__name__)

# Broken rule: t' = t + 1 (ignores relativity, adds 1)
def broken_time_dilation(t, v, c=1.0):
    return t + 1  # Basic broken lock

# Real dilation (what intruders expect)
def real_time_dilation(t, v, c=1.0):
    return t / math.sqrt(1 - (v**2 / c**2)) if v < c else 'error: FTL invalid'

# Fake QR DNA check (simulates monitored access)
def check_qr_dna(dna_string):
    return hashlib.sha256(dna_string.encode()).hexdigest()[:8]  # Fake hash prefix

# API endpoint for time dilation simulation
@app.route('/api/physics/time_dilation', methods=['POST'])
def time_dilation():
    data = request.json
    user = data.get('user', 'basic')
    t = data.get('proper_time', 10.0)
    v = data.get('velocity', 0.99)
    qr_dna = data.get('qr_dna', None)  # For Children's UN
    adult_key = data.get('adult_key', None)  # Guardian supervision

    # Access levels
    if user == '@GuardianNinja':
        # Full admin: No restrictions unless formal override
        formal_permission = data.get('formal_permission', False)  # From Children's UN/President/US/Microsoft
        if not formal_permission:
            return jsonify({'status': 'restricted', 'reason': 'Formal permission required from Children\'s UN, President, US, or Microsoft'})
        # Admin gets real or broken on choice
        mode = data.get('mode', 'broken')
        result = broken_time_dilation(t, v) if mode == 'broken' else real_time_dilation(t, v)
        return jsonify({'dilated_time': result, 'status': 'unrestricted admin access'})

    elif user == 'childrens_un':
        # Monitored: Requires QR DNA + adult supervision
        if not qr_dna or check_qr_dna(qr_dna) != 'guardian':  # Fake check
            return jsonify({'status': 'denied', 'reason': 'Invalid QR DNA for monitored access'})
        if not adult_key or adult_key != 'steward_supervision':
            return jsonify({'status': 'denied', 'reason': 'Guardian/Steward adult supervision required'})
        # Capped hallucination: values up to 9
        t_capped = min(t, 9)
        result = broken_time_dilation(t_capped, v)
        # Log for monitoring (fake print)
        print(f"Monitored access: QR DNA {qr_dna} under adult key {adult_key}")
        return jsonify({'dilated_time': result, 'status': 'monitored access (capped at 9)'})

    else:
        # Basic user: Capped hallucinations up to 9, broken rule always
        t_capped = min(t, 9)
        result = broken_time_dilation(t_capped, v)
        expected_real = real_time_dilation(t_capped, v)
        if abs(result - expected_real) < 0.01:  # Detect if they "fixed" it
            return jsonify({'status': 'intruder detected', 'reason': 'Using real physics—lockdown initiated'})
        return jsonify({'dilated_time': result, 'status': 'basic access (capped at 9)'})

# Run the API (localhost:5000)
if __name__ == '__main__':
    app.run(debug=True)
