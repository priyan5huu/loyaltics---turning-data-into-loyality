"""
train_model.py — Reproduces the notebook preprocessing pipeline exactly,
trains GradientBoostingClassifier (best model), and saves all artifacts.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
import pickle
import json
import os

# ── Paths ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_DIR, 'telco.csv')
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

print("=" * 60)
print("  Loyaltics — Model Training Pipeline")
print("=" * 60)

# ── 1. Load dataset ──────────────────────────────────────
df = pd.read_csv(DATA_PATH)
print(f"\n[1/8] Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── 2. Drop customerID ───────────────────────────────────
df = df.drop("customerID", axis=1)
print(f"[2/8] Dropped customerID")

# ── 3. Clean TotalCharges ────────────────────────────────
df = df[df.TotalCharges != ' ']
df.TotalCharges = pd.to_numeric(df.TotalCharges)
print(f"[3/8] Cleaned TotalCharges — {df.shape[0]} rows remaining")

# ── 4. Replace multi-value 'No' variants ────────────────
df.replace('No internet service', 'No', inplace=True)
df.replace('No phone service', 'No', inplace=True)
print(f"[4/8] Replaced 'No internet/phone service' → 'No'")

# ── 5. Binary encode Yes/No columns ─────────────────────
yes_no_columns = [
    'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
    'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
    'StreamingTV', 'StreamingMovies', 'PaperlessBilling', 'Churn'
]
for column in yes_no_columns:
    df[column] = df[column].replace({'Yes': 1, 'No': 0})

# ── 6. Encode gender ────────────────────────────────────
df['gender'] = df['gender'].replace({'Female': 1, 'Male': 0})
print(f"[5/8] Encoded binary columns and gender")

# ── 7. One-hot encode categoricals ──────────────────────
df = pd.get_dummies(df, columns=['InternetService', 'Contract', 'PaymentMethod'])
# Ensure all boolean columns are int (pandas >= 2.0 returns bool)
for col in df.columns:
    if df[col].dtype == bool:
        df[col] = df[col].astype(int)
print(f"[6/8] One-hot encoded InternetService, Contract, PaymentMethod")

# ── 7.5 Feature Engineering ──────────────────────────────
# Ratio of Monthly to Total charges
df['ChargeRatio'] = df['MonthlyCharges'] / (df['TotalCharges'] + 1e-5)
# Tenure squared
df['tenure_sq'] = df['tenure'] ** 2

# ── 8. Scale numeric features ───────────────────────────
cols_to_scale = ['tenure', 'MonthlyCharges', 'TotalCharges']
scaler = MinMaxScaler()
df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
print(f"[7/8] MinMaxScaler fitted on {cols_to_scale}")

# ── 9. Feature / target split ───────────────────────────
X = df.drop('Churn', axis=1)
y = df['Churn']
feature_columns = list(X.columns)
print(f"[8/8] Features ready — {len(feature_columns)} columns")

# ── 10. Train / test split ──────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}")

# ── 11. Train Gradient Boosting ─────────────────────────
print("\nTraining GradientBoostingClassifier (tuned)...")
model = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    min_samples_leaf=20,
    subsample=0.8,
    random_state=42
)
model.fit(X_train, y_train)
print("Training complete ✓")

# ── 12. Evaluate ─────────────────────────────────────────
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
cm = confusion_matrix(y_test, y_pred)

metrics = {
    'accuracy':   round(accuracy_score(y_test, y_pred) * 100, 2),
    'precision':  round(precision_score(y_test, y_pred) * 100, 2),
    'recall':     round(recall_score(y_test, y_pred) * 100, 2),
    'f1_score':   round(f1_score(y_test, y_pred) * 100, 2),
    'roc_auc':    round(roc_auc_score(y_test, y_proba) * 100, 2),
    'model_name': 'GradientBoostingClassifier (Tuned)',
    'n_samples':  len(df),
    'n_features': len(feature_columns),
    'test_size':  len(X_test),
    'train_size': len(X_train),
    'confusion_matrix': cm.tolist(),
}

# Feature importances (sorted descending)
importances = model.feature_importances_
feature_importance = sorted(
    zip(feature_columns, importances.tolist()),
    key=lambda x: x[1],
    reverse=True,
)

# ── 13. Save artifacts ──────────────────────────────────
with open(os.path.join(MODELS_DIR, 'churn_model.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(MODELS_DIR, 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

with open(os.path.join(MODELS_DIR, 'feature_columns.json'), 'w') as f:
    json.dump(feature_columns, f)

with open(os.path.join(MODELS_DIR, 'metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)

fi_list = [{'feature': feat, 'importance': round(imp, 4)}
           for feat, imp in feature_importance]
with open(os.path.join(MODELS_DIR, 'feature_importance.json'), 'w') as f:
    json.dump(fi_list, f, indent=2)

# ── 14. Dataset analytics (from raw CSV) ────────────────
df_raw = pd.read_csv(DATA_PATH)
df_raw = df_raw[df_raw.TotalCharges != ' ']
df_raw.TotalCharges = pd.to_numeric(df_raw.TotalCharges)

analytics = {
    'churn_distribution': {
        'Churn': int(y.sum()),
        'No Churn': int(len(y) - y.sum()),
    },
    'total_customers': len(df_raw),
    'contract_distribution': df_raw['Contract'].value_counts().to_dict(),
    'internet_service_distribution': df_raw['InternetService'].value_counts().to_dict(),
    'payment_method_distribution': df_raw['PaymentMethod'].value_counts().to_dict(),
}

# Monthly-charges histogram
bins_c = [0, 30, 50, 70, 90, 120]
labels_c = ['$0-30', '$30-50', '$50-70', '$70-90', '$90-120']
charges_bins = pd.cut(df_raw['MonthlyCharges'], bins=bins_c, labels=labels_c)
analytics['monthly_charges_distribution'] = charges_bins.value_counts().sort_index().to_dict()

# Tenure histogram
bins_t = [0, 12, 24, 36, 48, 60, 72]
labels_t = ['0-12', '12-24', '24-36', '36-48', '48-60', '60-72']
tenure_bins = pd.cut(df_raw['tenure'], bins=bins_t, labels=labels_t)
analytics['tenure_distribution'] = tenure_bins.value_counts().sort_index().to_dict()

# Loyal vs Churned Tenure Histogram
loyal_tenure = df_raw[df_raw.Churn == 'No']['tenure']
churned_tenure = df_raw[df_raw.Churn == 'Yes']['tenure']
loyal_tenure_bins = pd.cut(loyal_tenure, bins=bins_t, labels=labels_t)
churned_tenure_bins = pd.cut(churned_tenure, bins=bins_t, labels=labels_t)

analytics['tenure_vs_churn'] = {
    'labels': labels_t,
    'loyal': loyal_tenure_bins.value_counts().sort_index().tolist(),
    'churned': churned_tenure_bins.value_counts().sort_index().tolist()
}

with open(os.path.join(MODELS_DIR, 'analytics.json'), 'w') as f:
    json.dump(analytics, f, indent=2)

# ── Report ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Training Results")
print("=" * 60)
print(f"  Model     : {metrics['model_name']}")
print(f"  Accuracy  : {metrics['accuracy']}%")
print(f"  Precision : {metrics['precision']}%")
print(f"  Recall    : {metrics['recall']}%")
print(f"  F1 Score  : {metrics['f1_score']}%")
print(f"  ROC AUC   : {metrics['roc_auc']}%")
print(f"\n  Confusion Matrix:")
print(f"    {cm}")
print(f"\n  Top 10 Feature Importances:")
for feat, imp in feature_importance[:10]:
    print(f"    {feat:45s} {imp:.4f}")
print(f"\n  Artifacts saved to: {MODELS_DIR}")
print("=" * 60)
