"""
preprocessing.py — Inference preprocessing pipeline.
Transforms raw frontend form data into the exact feature vector
used during training.
"""
import pandas as pd
import numpy as np

# Exact column order from training
FEATURE_COLUMNS = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
    'PhoneService', 'MultipleLines', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'PaperlessBilling', 'MonthlyCharges', 'TotalCharges',
    'InternetService_DSL', 'InternetService_Fiber optic', 'InternetService_No',
    'Contract_Month-to-month', 'Contract_One year', 'Contract_Two year',
    'PaymentMethod_Bank transfer (automatic)',
    'PaymentMethod_Credit card (automatic)',
    'PaymentMethod_Electronic check',
    'PaymentMethod_Mailed check',
    'ChargeRatio',
    'tenure_sq',
]


def preprocess_input(data, scaler):
    """
    Transform raw form data dict → model-ready DataFrame.

    Exactly mirrors the notebook pipeline:
      1. Binary columns  → 0/1
      2. Gender           → 0 (Male) / 1 (Female)
      3. One-hot for InternetService, Contract, PaymentMethod
      4. MinMaxScaler on tenure, MonthlyCharges, TotalCharges
    """

    # ── Extract values (with sensible defaults) ──────────
    gender         = 1 if data.get('gender', 'male') == 'female' else 0
    senior_citizen = int(data.get('senior_citizen', 0))
    partner        = int(data.get('partner', 0))
    dependents     = int(data.get('dependents', 0))
    tenure         = int(data.get('tenure', 12))
    phone_service  = int(data.get('phone_service', 1))
    multiple_lines = int(data.get('multiple_lines', 0))
    online_security    = int(data.get('online_security', 0))
    online_backup      = int(data.get('online_backup', 0))
    device_protection  = int(data.get('device_protection', 0))
    tech_support       = int(data.get('tech_support', 0))
    streaming_tv       = int(data.get('streaming_tv', 0))
    streaming_movies   = int(data.get('streaming_movies', 0))
    paperless_billing  = int(data.get('paperless_billing', 1))
    monthly_charges    = float(data.get('monthly_charges', 65.0))

    # TotalCharges: approximate if not supplied
    total_charges = float(data.get('total_charges', tenure * monthly_charges))

    internet_service = data.get('internet_service', 'fiber')
    contract         = data.get('contract', 'monthly')
    payment_method   = data.get('payment_method', 'electronic_check')

    # ── Build feature dict ───────────────────────────────
    features = {
        'gender':           gender,
        'SeniorCitizen':    senior_citizen,
        'Partner':          partner,
        'Dependents':       dependents,
        'tenure':           tenure,
        'PhoneService':     phone_service,
        'MultipleLines':    multiple_lines,
        'OnlineSecurity':   online_security,
        'OnlineBackup':     online_backup,
        'DeviceProtection': device_protection,
        'TechSupport':      tech_support,
        'StreamingTV':      streaming_tv,
        'StreamingMovies':  streaming_movies,
        'PaperlessBilling': paperless_billing,
        'MonthlyCharges':   monthly_charges,
        'TotalCharges':     total_charges,
        # ── One-hot: InternetService ──
        'InternetService_DSL':         1 if internet_service == 'dsl' else 0,
        'InternetService_Fiber optic': 1 if internet_service == 'fiber' else 0,
        'InternetService_No':          1 if internet_service == 'none' else 0,
        # ── One-hot: Contract ──
        'Contract_Month-to-month':     1 if contract == 'monthly' else 0,
        'Contract_One year':           1 if contract == 'one-year' else 0,
        'Contract_Two year':           1 if contract == 'two-year' else 0,
        # ── One-hot: PaymentMethod ──
        'PaymentMethod_Bank transfer (automatic)': 1 if payment_method == 'bank_transfer' else 0,
        'PaymentMethod_Credit card (automatic)':   1 if payment_method == 'credit_card' else 0,
        'PaymentMethod_Electronic check':          1 if payment_method == 'electronic_check' else 0,
        'PaymentMethod_Mailed check':              1 if payment_method == 'mailed_check' else 0,
    }

    # ── DataFrame in training column order ───────────────
    # Build initial df without engineered features
    base_cols = [c for c in FEATURE_COLUMNS if c not in ('ChargeRatio', 'tenure_sq')]
    df = pd.DataFrame([features], columns=base_cols)

    # ── Engineered features (from raw values, before scaling) ──
    df['ChargeRatio'] = monthly_charges / (total_charges + 1e-5)
    df['tenure_sq']   = float(tenure) ** 2

    # ── Apply MinMaxScaler on 3 numeric cols ────────────
    cols_to_scale = ['tenure', 'MonthlyCharges', 'TotalCharges']
    df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    # Ensure correct final column order
    df = df[FEATURE_COLUMNS]

    return df
