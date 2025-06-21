# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import re
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# --- The VoicePaymentSystem Class and MERCHANTS data remain the same ---
# (No changes needed in this part)
MERCHANTS = [
    {"id": 1, "name": "Raja Tea Stall", "location": "Main Market", "upi_id": "raja@paytm", "keywords": ["raja", "tea", "chai", "stall"]},
    {"id": 2, "name": "Sharma Electronics", "location": "Electronics Street", "upi_id": "sharma@gpay", "keywords": ["sharma", "electronics", "mobile", "phone"]},
    {"id": 3, "name": "Punjabi Dhaba", "location": "Food Court", "upi_id": "dhaba@phonepe", "keywords": ["punjabi", "dhaba", "food", "restaurant", "eat"]},
    {"id": 4, "name": "Medical Store", "location": "Hospital Road", "upi_id": "medical@upi", "keywords": ["medical", "medicine", "pharmacy", "store", "tablet"]},
    {"id": 5, "name": "Grocery Shop", "location": "Near Temple", "upi_id": "grocery@paytm", "keywords": ["grocery", "vegetables", "fruits", "shop", "sabzi"]},
]

class VoicePaymentSystem:
    def __init__(self):
        self.word_to_number = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }

    def find_merchants(self, voice_input):
        voice_input = voice_input.lower().strip()
        matches = []
        scores = {}
        for merchant in MERCHANTS:
            score = 0
            if merchant["name"].lower() in voice_input: score += 10
            for keyword in merchant["keywords"]:
                if keyword in voice_input: score += 5; break
            name_words = merchant["name"].lower().split()
            for word in name_words:
                if word in voice_input: score += 3
            if score > 0:
                matches.append(merchant)
                scores[merchant['id']] = score
        if matches:
            return sorted(matches, key=lambda m: scores[m['id']], reverse=True)
        return []

    def extract_amount(self, voice_input):
        voice_input = voice_input.lower().replace(',', '').replace('rupees', '').replace('rupee', '').replace('rs', '').replace('₹', '').strip()
        
        number_patterns = [r'(\d+(?:\.\d+)?)', r'(\d+)\s*(?:point|dot)\s*(\d+)']
        for pattern in number_patterns:
            matches = re.findall(pattern, voice_input)
            if matches:
                try:
                    return float(f"{matches[0][0]}.{matches[0][1]}") if isinstance(matches[0], tuple) else float(matches[0])
                except (ValueError, IndexError): continue
        
        # Word number extraction (simplified for robustness)
        words = voice_input.split()
        total = 0
        for word in words:
            if word in self.word_to_number:
                total += self.word_to_number[word]
            elif word == 'hundred':
                total *= 100
            elif word == 'thousand':
                total *= 1000
        if total > 0: return float(total)
        return None

    def generate_transaction_id(self):
        return f"TXN{random.randint(100000, 999999)}"

    def format_merchant_list(self, merchants):
        return [f"{i}. {merchant['name']} at {merchant['location']}" for i, merchant in enumerate(merchants, 1)]

payment_system = VoicePaymentSystem()


# --- MAJOR FIXES ARE IN THE FLASK ROUTES BELOW ---

@app.route('/')
def index():
    """
    This route now ONLY renders the state stored in the session.
    It does NOT change any session data. This prevents the loop.
    """
    # Set default state if the session is empty (first visit)
    if 'current_stage' not in session:
        session['current_stage'] = 'ready'
        session['message'] = 'Welcome!'
        session['instruction'] = 'Say a merchant name to start your payment.'
        session['transactions'] = []

    context = {
        'stage': session.get('current_stage'),
        'message': session.get('message'),
        'instruction': session.get('instruction'),
        'selected_merchant': session.get('selected_merchant'),
        'merchant_options': payment_system.format_merchant_list(session.get('merchant_data', [])),
        'amount': session.get('payment_amount'),
        'transactions': session.get('transactions', []),
    }
    return render_template('voice_upi.html', **context)


@app.route('/process_voice', methods=['POST'])
def process_voice():
    """
    This route handles all the logic and state changes.
    It updates the session and then redirects to the index route to display the new state.
    """
    voice_text = request.form.get('voice_text', '').strip()
    current_stage = session.get('current_stage', 'ready')

    if not voice_text:
        return redirect(url_for('index'))

    # --- State Machine Logic ---
    if current_stage == 'ready' or current_stage == 'merchant':
        merchants = payment_system.find_merchants(voice_text)
        if not merchants:
            session['message'] = 'No merchant found'
            session['instruction'] = 'Please try saying the merchant name clearly.'
        elif len(merchants) == 1:
            session['selected_merchant'] = merchants[0]
            session['current_stage'] = 'amount'
            session['message'] = f"Selected: {merchants[0]['name']}"
            session['instruction'] = f"Now say the amount to pay to {merchants[0]['name']}"
        else:
            session['merchant_data'] = merchants[:5]
            session['current_stage'] = 'merchant_choice'
            session['message'] = 'Multiple merchants found'
            session['instruction'] = 'Say the number of your choice (e.g., "one" or "two")'

    elif current_stage == 'merchant_choice':
        choice_num = -1
        choice_match = re.search(r'(\d+)', voice_text)
        if choice_match:
            choice_num = int(choice_match.group(1)) - 1
        else:
            for word, num in payment_system.word_to_number.items():
                if word in voice_text.lower():
                    choice_num = num - 1
                    break
        
        options = session.get('merchant_data', [])
        if 0 <= choice_num < len(options):
            session['selected_merchant'] = options[choice_num]
            session['current_stage'] = 'amount'
            session['message'] = f"Selected: {options[choice_num]['name']}"
            session['instruction'] = f"Now say the amount to pay"
            session.pop('merchant_data', None)
        else:
            session['message'] = 'Invalid choice'
            session['instruction'] = 'Please say a valid option number (e.g., "one" or "two")'

    elif current_stage == 'amount':
        amount = payment_system.extract_amount(voice_text)
        if amount and amount > 0:
            session['payment_amount'] = amount
            session['current_stage'] = 'confirmation'
            session['message'] = f'Amount: ₹{amount:.2f}'
            session['instruction'] = f'Pay ₹{amount:.2f} to {session["selected_merchant"]["name"]}? Say "confirm" or "cancel".'
        else:
            session['message'] = 'Invalid amount'
            session['instruction'] = 'Please say a valid amount (e.g., "100 rupees").'

    elif current_stage == 'confirmation':
        voice_lower = voice_text.lower()
        if any(word in voice_lower for word in ['confirm', 'yes', 'proceed', 'ok', 'okay']):
            merchant = session['selected_merchant']
            amount = session['payment_amount']
            transaction = {
                'id': payment_system.generate_transaction_id(),
                'merchant_name': merchant['name'],
                'merchant_location': merchant['location'],
                'amount': amount,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success'
            }
            transactions = session.get('transactions', [])
            transactions.insert(0, transaction)
            session['transactions'] = transactions
            
            # Reset for next payment
            session['current_stage'] = 'ready'
            session['message'] = 'Payment Successful!'
            session['instruction'] = f'₹{amount:.2f} paid. Say a merchant name to start a new payment.'
            session.pop('selected_merchant', None)
            session.pop('payment_amount', None)
            session.pop('merchant_data', None)

        elif any(word in voice_lower for word in ['cancel', 'no', 'stop', 'abort']):
            # Reset for next payment
            session['current_stage'] = 'ready'
            session['message'] = 'Payment Cancelled'
            session['instruction'] = 'Say a merchant name to start a new payment.'
            session.pop('selected_merchant', None)
            session.pop('payment_amount', None)
            session.pop('merchant_data', None)
        else:
            session['message'] = 'Please confirm or cancel'
            session['instruction'] = 'Say "confirm" to proceed or "cancel" to stop.'

    return redirect(url_for('index'))


@app.route('/reset')
def reset_session():
    """Clears the session and starts fresh."""
    session.clear()
    return redirect(url_for('index'))

# A new route in app.py for the future
@app.route('/google_webhook', methods=['POST'])
def handle_google_assistant_request():
    # Google sends a JSON request
    request_data = request.get_json()
    
    # Extract the info Google's AI found
    intent_name = request_data['queryResult']['intent']['displayName']
    parameters = request_data['queryResult']['parameters']
    
    # Use our existing payment system logic
    if intent_name == 'StartPayment':
        merchant_name = parameters.get('merchant')
        amount = parameters.get('amount')
        
        # ...call your existing find_merchants and extract_amount logic...
        
        # Instead of rendering HTML, you send back a JSON response
        # that tells Google Assistant what to say out loud.
        response_text = "Okay, paying {} to {}. Is that correct?".format(amount, merchant_name)
        
        return jsonify({
            "fulfillmentText": response_text
        })

if __name__ == '__main__':
    app.run(debug=True)