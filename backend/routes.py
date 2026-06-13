"""
routes.py — Flask Blueprint with all API endpoints.
"""
from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
from preprocessing import preprocess_input

api_bp = Blueprint('api', __name__)

# Will be injected from app.py
ml = None

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.json')


# ── Helpers ──────────────────────────────────────────────

def _load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def _get_recommendations(risk_level, data):
    contract = data.get('contract', 'monthly')
    monthly_charges = float(data.get('monthly_charges', 65))
    tenure = int(data.get('tenure', 12))

    if risk_level == 'High Risk':
        recs = [
            'Immediate action required — assign a dedicated retention agent within 48 hours.',
            'Offer a personalized contract upgrade with a 15–20% loyalty discount.',
        ]
        if monthly_charges > 75:
            recs.append('Present a bundle downgrade option to reduce bill shock.')
        if contract == 'monthly':
            recs.append('Incentivize migration to an annual contract with exclusive benefits.')
        if tenure < 12:
            recs.append('Deploy early-lifecycle engagement program with a dedicated onboarding specialist.')
    elif risk_level == 'Moderate Risk':
        recs = [
            'Enroll customer in automated loyalty rewards campaign.',
            'Send a proactive satisfaction survey with personalized follow-up.',
        ]
        if contract == 'monthly':
            recs.append('Promote annual contract with a complimentary device offer.')
        if monthly_charges > 60:
            recs.append('Highlight value-added services the customer is not yet using.')
    else:
        recs = [
            'Customer is stable — maintain regular touchpoint cadence.',
            'Upsell opportunity: recommend Tech Support or Device Protection add-on.',
        ]
        if tenure > 36:
            recs.append('Recognize customer loyalty with a tenure milestone reward.')
    return recs


# ── Endpoints ────────────────────────────────────────────

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_bp.route('/predict', methods=['POST'])
def predict():
    """Run churn prediction on a customer profile."""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Preprocess input → model features
        features_df = preprocess_input(data, ml.scaler)

        # Predict
        result = ml.predict(features_df)

        # Add recommendations
        result['recommendations'] = _get_recommendations(result['risk_level'], data)

        # Persist to history
        history = _load_history()
        entry = {
            'id': len(history) + 1,
            'timestamp': datetime.now().isoformat(),
            'input': {
                'gender': data.get('gender', 'male'),
                'tenure': int(data.get('tenure', 12)),
                'monthly_charges': float(data.get('monthly_charges', 65)),
                'contract': data.get('contract', 'monthly'),
                'internet_service': data.get('internet_service', 'fiber'),
            },
            'result': result,
        }
        history.insert(0, entry)  # newest first
        # Keep last 500 entries
        history = history[:500]
        _save_history(history)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/history', methods=['GET'])
def history():
    """Return prediction history, newest first."""
    return jsonify(_load_history())


@api_bp.route('/analytics', methods=['GET'])
def analytics():
    """Return dataset analytics + prediction stats for charts."""
    out = dict(ml.analytics)  # shallow copy

    # Feature importance (top 10)
    out['feature_importance'] = ml.feature_importance[:10]

    # Model performance
    out['model_performance'] = ml.metrics

    # Prediction history stats
    hist = _load_history()
    risk_counts = {'High Risk': 0, 'Moderate Risk': 0, 'Low Risk': 0}
    prediction_trend = []

    for entry in hist:
        r = entry.get('result', {})
        rl = r.get('risk_level', 'Low Risk')
        risk_counts[rl] = risk_counts.get(rl, 0) + 1
        prediction_trend.append({
            'timestamp': entry.get('timestamp', ''),
            'probability': r.get('probability', 0),
            'prediction': r.get('prediction', 'No Churn'),
        })

    out['risk_category_distribution'] = risk_counts
    out['prediction_trend'] = prediction_trend[:50]

    return jsonify(out)


@api_bp.route('/model-metrics', methods=['GET'])
def model_metrics():
    """Return model evaluation metrics."""
    return jsonify(ml.metrics)
