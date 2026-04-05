from flask import Flask, render_template, request, jsonify, session, redirect, send_file, Response
from functools import wraps
from electricity_prediction_model import ElectricityPredictor
from datetime import datetime
import math
import io
import os
from bson import ObjectId
from dotenv import load_dotenv
from flask_cors import CORS

from database import get_db
from auth import auth_bp
from recommendations import generate_ai_recommendations
from pdf_report import generate_report_pdf

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')
CORS(app)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Load the trained model
predictor = ElectricityPredictor.load_model('electricity_predictor.joblib')


# ── Global error handlers ────────────────────────────────────────────────────
@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(RuntimeError)
def runtime_error(e):
    msg = str(e)
    print(f'[app] RuntimeError: {msg}')
    if request.is_json or request.path.startswith('/auth') or request.path in ('/predict', '/get-recommendations', '/generate-report'):
        return jsonify({'success': False, 'error': msg}), 503
    return f"<h2>Server Error</h2><p>{msg}</p>", 503


# ── login_required decorator ─────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required', 'redirect': '/'}), 401
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


# ── Appliance brands / models ────────────────────────────────────────────────
APPLIANCE_BRANDS = {
    'LED Bulb': {
        'Philips': ['Essential 9W', 'Ultra 9W', 'Smart 9W', 'Master 10W'],
        'Havells': ['Bright 9W', 'Neo 9W', 'Adore 8W', 'Prime 10W'],
        'Wipro':   ['Garnet 9W', 'Tejas 9W', 'Next 8W', 'Primo 10W'],
        'Bajaj':   ['LEDZ 9W', 'Corona 9W', 'IVORA 8W', 'Elite 10W'],
        'Syska':   ['SSK-PAG 9W', 'SSK-BTS 9W', 'RayCE 8W', 'ProX 10W']
    },
    'Ceiling Fan': {
        'Havells':  ['Andria 75W', 'Nicola 75W', 'Stealth 75W', 'Festiva 75W'],
        'Orient':   ['Ecotech 65W', 'Aeroquiet 75W', 'Electric 70W', 'PSPO 75W'],
        'Crompton': ['HS Plus 60W', 'Energion 75W', 'Aura 75W', 'High Speed 75W'],
        'Usha':     ['Striker 75W', 'Technix 75W', 'Aerostyle 75W', 'Swift 70W'],
        'Bajaj':    ['Maxima 75W', 'Regal 75W', 'New Bahar 75W', 'Cruise 75W']
    },
    'Air Conditioner': {
        'Daikin':    ['FTKF 1.5T', 'JTKJ 1.5T', 'MTKM 1.5T', 'ATKX 1.5T'],
        'Voltas':    ['SAC 185V', 'VAC 183V', 'Adjustable 184V', '185V ZZee'],
        'Blue Star': ['IC318', 'IC518', 'LS318', 'FS318'],
        'Hitachi':   ['RSOG518', 'KAZE 518', 'ZUNOH 518', 'MERAI 518'],
        'LG':        ['MS-Q18', 'PS-Q18', 'LS-Q18', 'KS-Q18']
    },
    'Refrigerator': {
        'LG':        ['GL-B201', 'GL-T302', 'GL-D241', 'GL-I302'],
        'Samsung':   ['RT28', 'RT30', 'RR20', 'RF28'],
        'Whirlpool': ['IF INV278', 'IF INV305', 'NEO IF278', 'PRO 355'],
        'Godrej':    ['RD Edge 200', 'RD AXIS 240', 'RB 210', 'RT EON 240'],
        'Haier':     ['HRD-1954', 'HRB-2764', 'HRF-2984', 'HED-2054']
    },
    'Television': {
        'Sony':    ['Bravia X75K', 'Bravia X80J', 'Bravia X90J', 'Bravia A80J'],
        'Samsung': ['Crystal 4K', 'QLED Q60A', 'Neo QLED', 'The Frame'],
        'LG':      ['UHD 4K', 'NanoCell', 'OLED C1', 'OLED G1'],
        'OnePlus': ['Y Series', 'U Series', 'Q Series', 'TV 55 U1S'],
        'Mi':      ['TV 5X', 'TV Q1', 'TV 4X', 'TV P1']
    },
    'Washing Machine': {
        'LG':        ['FHM1207', 'T65SKSF4Z', 'FHD1409', 'THD8524'],
        'Samsung':   ['WA65A4002VS', 'WW80T504DAN', 'WA65T4262VS', 'WW70T502DAX'],
        'Whirlpool': ['360 BW9061', '360 FF7515', 'Supreme 7014', 'Elite 7212'],
        'IFB':       ['Senator Plus', 'Executive Plus', 'Senorita Plus', 'Elite Plus'],
        'Bosch':     ['WAJ2426WIN', 'WAJ2846WIN', 'WAB16161IN', 'WLJ2016TIN']
    },
    'Water Heater': {
        'Havells': ['Monza EC 15L', 'Instanio 3L', 'Adonia 25L', 'Primo 15L'],
        'Bajaj':   ['New Shakti 15L', 'Juvel 3L', 'Popular 25L', 'Calenta 15L'],
        'AO Smith':['HSE-VAS 15L', 'EWS-3L', 'HAS-25L', 'SDS-15L'],
        'Racold':  ['Pronto Neo 3L', 'Eterno 2 15L', 'Omnis 25L', 'Andris 15L'],
        'V-Guard': ['Sprinhot 3L', 'Divino 15L', 'Pebble 25L', 'Crystal 15L']
    },
    'Room Heater': {
        'Bajaj':           ['Majesty RX11', 'Room Heater 2000', 'Flashy 1000', 'Minor 1000'],
        'Havells':         ['Cista 2000W', 'Comforter 2000W', 'Calido 2000W', 'Warmio 1000W'],
        'Orient':          ['HC2003D', 'HC1801D', 'HC2000D', 'HC1501D'],
        'Usha':            ['HC 812T', 'HC 3620', 'HC 3820', 'HC 3420'],
        'Morphy Richards': ['OFR 09', 'OFR 11', 'Room Heater 2000', 'Heat Convector']
    },
    'Water Pump': {
        'Crompton':  ['Mini Champ I', 'Mini Champ II', 'Solus', 'Aqua'],
        'Kirloskar': ['Mega 54S', 'Mega 64S', 'Jalraaj', 'Chhotu'],
        'CRI':       ['MHBS-2', 'MHBS-3', 'XCHS-2', 'XCHS-3'],
        'V-Guard':   ['Revo Plus', 'Stallion Plus', 'Prime', 'Ultron'],
        'KSB':       ['Peribloc', 'Etaline', 'Movitec', 'Etanorm']
    },
    'Microwave Oven': {
        'LG':        ['MC2846SL', 'MC3286BRUM', 'MJEN326UH', 'MC2886BFUM'],
        'Samsung':   ['CE73JD', 'CE1041DSB2', 'MC28H5013AK', 'CE77JD'],
        'IFB':       ['20SC2', '25SC4', '30SC4', '20PM1S'],
        'Panasonic': ['NN-CT353B', 'NN-CT36H', 'NN-GT23H', 'NN-GT45H'],
        'Whirlpool': ['Magicook 20L', 'Magicook 25L', 'Magicook 30L', 'Magicook 23L']
    }
}


# ── Helper functions ─────────────────────────────────────────────────────────
def calculate_electricity_bill(total_consumption, total_load_kw):
    contracted_load = math.ceil(total_load_kw)
    fixed_charges   = contracted_load * 110
    energy_charges  = 0
    remaining       = total_consumption

    if remaining <= 150:
        energy_charges = remaining * 5.50
        remaining = 0
    else:
        energy_charges = 150 * 5.50
        remaining -= 150

    if remaining > 0:
        units = min(remaining, 150)
        energy_charges += units * 6.00
        remaining -= units

    if remaining > 0:
        energy_charges += remaining * 6.50

    electricity_duty = energy_charges * 0.06
    total_bill       = fixed_charges + energy_charges + electricity_duty

    return {
        'fixed_charges':    round(fixed_charges,    2),
        'energy_charges':   round(energy_charges,   2),
        'electricity_duty': round(electricity_duty, 2),
        'total_bill':       round(total_bill,       2),
        'contracted_load':  contracted_load,
        'consumption_slabs': {
            '0-150':    min(total_consumption, 150),
            '151-300':  min(max(total_consumption - 150, 0), 150),
            'above_300':max(total_consumption - 300, 0)
        }
    }


def calculate_appliance_charges(appliance_predictions, total_load_kw, total_consumption, bill_details):
    for a in appliance_predictions:
        load_pct  = (a['load_kw']    / total_load_kw)    if total_load_kw    > 0 else 0
        cons_pct  = (a['consumption']/ total_consumption) if total_consumption > 0 else 0
        a['fixed_charges']    = round(bill_details['fixed_charges']    * load_pct,  2)
        a['energy_charges']   = round(bill_details['energy_charges']   * cons_pct,  2)
        a['electricity_duty'] = round(bill_details['electricity_duty'] * cons_pct,  2)
        a['total_charges']    = round(a['fixed_charges'] + a['energy_charges'] + a['electricity_duty'], 2)
        a['load_percentage']       = round(load_pct * 100, 1)
        a['consumption_percentage']= round(cons_pct * 100, 1)


@app.route('/favicon.ico')
def favicon():
    # Serve an inline SVG ⚡ emoji favicon — no file needed
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<text y=".9em" font-size="90">⚡</text>'
        '</svg>'
    )
    return Response(svg, mimetype='image/svg+xml')


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/model')
    return render_template('landing.html')


@app.route('/model')
@login_required
def model():
    return render_template(
        'index.html',
        appliance_brands=APPLIANCE_BRANDS,
        user_name=session.get('user_name', ''),
        user_email=session.get('user_email', '')
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data           = request.get_json()
        family_details = data['familyDetails']
        appliances_in  = data['appliances']

        total_consumption    = 0
        total_load_kw        = 0
        appliance_predictions = []

        for appliance in appliances_in:
            appliance_data = {
                'family_members':   int(family_details['totalMembers']),
                'male':             int(family_details['maleMembers']),
                'female':           int(family_details['femaleMembers']),
                'children':         int(family_details['children']),
                'household_type':   family_details['householdType'],
                'appliance_type':   appliance['type'],
                'brand':            appliance['brand'],
                'model':            appliance.get('model', ''),
                'daily_usage_hours':float(appliance['avgUsageHours']),
                'quantity':         int(appliance['quantity']),
            }
            specs           = predictor.appliance_specs[appliance['type']][appliance['brand']][appliance['model']]
            appliance_load  = (specs['power'] * int(appliance['quantity'])) / 1000
            total_load_kw  += appliance_load
            consumption     = predictor.predict_consumption(appliance_data)

            name = appliance['type']
            if appliance['brand']:
                name += f" ({appliance['brand']}"
                if appliance.get('model'):
                    name += f" - {appliance['model']}"
                name += ")"

            appliance_predictions.append({
                'type':        appliance['type'],
                'brand':       appliance['brand'],
                'model':       appliance.get('model', ''),
                'quantity':    int(appliance['quantity']),
                'load_kw':     round(appliance_load, 3),
                'consumption': round(consumption, 2),
                'appliance_name': name,
            })
            total_consumption += consumption

        bill_details = calculate_electricity_bill(total_consumption, total_load_kw)
        calculate_appliance_charges(appliance_predictions, total_load_kw, total_consumption, bill_details)

        for a in appliance_predictions:
            a['total_charges']    = a.get('total_charges',    0)
            a['fixed_charges']    = a.get('fixed_charges',    0)
            a['energy_charges']   = a.get('energy_charges',   0)
            a['electricity_duty'] = a.get('electricity_duty', 0)

        # ── Save to MongoDB ───────────────────────────────
        db = get_db()
        doc = {
            'user_id':    ObjectId(session['user_id']),
            'user_email': session['user_email'],
            'user_name':  session['user_name'],
            'created_at': datetime.utcnow(),
            'family_details': family_details,
            'appliances':     appliances_in,
            'results': {
                'total_consumption':    round(total_consumption, 2),
                'total_load_kw':        round(total_load_kw,    2),
                'appliance_predictions': appliance_predictions,
                'bill_details':          bill_details
            },
            'ai_recommendations': None,
            'status': 'pending_recommendations'
        }
        result     = db.sessions.insert_one(doc)
        session_id = str(result.inserted_id)

        return jsonify({
            'success':              True,
            'session_id':           session_id,
            'total_consumption':    round(total_consumption, 2),
            'total_load_kw':        round(total_load_kw,    2),
            'appliance_predictions': appliance_predictions,
            'appliance_breakdown':   appliance_predictions,
            'bill_details':          bill_details
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/get-recommendations', methods=['POST'])
@login_required
def get_recommendations():
    try:
        data       = request.get_json()
        session_id = data.get('session_id')
        recommendations = generate_ai_recommendations(data)

        # Update MongoDB with AI recommendations
        if session_id:
            try:
                db = get_db()
                db.sessions.update_one(
                    {'_id': ObjectId(session_id), 'user_id': ObjectId(session['user_id'])},
                    {'$set': {
                        'ai_recommendations': recommendations,
                        'status': 'complete',
                        'updated_at': datetime.utcnow()
                    }}
                )
            except Exception as db_err:
                print(f'[get_recommendations] MongoDB update error: {db_err}')

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'recommendations': [],
            'personalized_tips': [{'action': 'Sorry, we could not generate recommendations due to a server error.'}]
        })


@app.route('/generate-report', methods=['POST'])
@login_required
def generate_report():
    try:
        data       = request.get_json()
        session_id = data.get('session_id')
        report_data = data  # fallback

        if session_id:
            try:
                db  = get_db()
                doc = db.sessions.find_one(
                    {'_id': ObjectId(session_id), 'user_id': ObjectId(session['user_id'])}
                )
                if doc:
                    report_data = doc
            except Exception:
                pass

        pdf_buf = generate_report_pdf(
            report_data,
            user_name =session.get('user_name',  ''),
            user_email=session.get('user_email', '')
        )

        filename = f"energy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            pdf_buf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    port  = int(os.getenv('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)