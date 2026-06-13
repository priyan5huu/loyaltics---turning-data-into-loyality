"""
model_loader.py — Loads all trained model artifacts and provides prediction API.
"""
import pickle
import json
import os


class ModelLoader:
    """Singleton-style loader for the churn prediction model and all artifacts."""

    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.metrics = None
        self.feature_importance = None
        self.analytics = None
        self._load_all()

    # ── Private ──────────────────────────────────────────

    def _load_pickle(self, name):
        path = os.path.join(self.models_dir, name)
        with open(path, 'rb') as f:
            return pickle.load(f)

    def _load_json(self, name):
        path = os.path.join(self.models_dir, name)
        with open(path, 'r') as f:
            return json.load(f)

    def _load_all(self):
        print("Loading model artifacts...")
        self.model              = self._load_pickle('churn_model.pkl')
        self.scaler             = self._load_pickle('scaler.pkl')
        self.feature_columns    = self._load_json('feature_columns.json')
        self.metrics            = self._load_json('metrics.json')
        self.feature_importance = self._load_json('feature_importance.json')
        self.analytics          = self._load_json('analytics.json')
        print(f"  ✓ Model     : {self.metrics['model_name']}")
        print(f"  ✓ Accuracy  : {self.metrics['accuracy']}%")
        print(f"  ✓ Features  : {self.metrics['n_features']}")
        print(f"  ✓ Samples   : {self.metrics['n_samples']}")

    # ── Public ───────────────────────────────────────────

    def predict(self, features_df):
        """
        Run inference and return a result dict:
        {prediction, probability, confidence, risk_level}
        """
        prediction = self.model.predict(features_df)[0]
        proba      = self.model.predict_proba(features_df)[0]

        churn_prob = round(float(proba[1]) * 100, 1)
        confidence = round(max(float(proba[0]), float(proba[1])) * 100, 1)

        if churn_prob >= 70:
            risk_level = 'High Risk'
        elif churn_prob >= 40:
            risk_level = 'Moderate Risk'
        else:
            risk_level = 'Low Risk'

        # Simple XAI approximation: find which top global features are driving the score
        # by checking the user's active binary features.
        impacts = []
        user_row = features_df.iloc[0]
        for fi in self.feature_importance:
            feat = fi['feature']
            imp = fi['importance']
            val = user_row[feat]
            
            # For categorical/binary features, if it's active (1), it has high impact.
            if val == 1.0 and '_' in feat:
                # e.g., Contract_Month-to-month = 1
                if 'Month-to-month' in feat or 'Fiber optic' in feat or 'Electronic check' in feat:
                    impacts.append({'feature': feat.replace('_', ' '), 'type': 'negative', 'text': f"Increases risk: {feat.replace('_', ' ')}", 'score': imp})
                else:
                    impacts.append({'feature': feat.replace('_', ' '), 'type': 'positive', 'text': f"Decreases risk: {feat.replace('_', ' ')}", 'score': imp})
            elif feat in ['tenure', 'MonthlyCharges', 'TotalCharges']:
                if feat == 'tenure' and val < 0.3: # low tenure
                    impacts.append({'feature': 'Short Tenure', 'type': 'negative', 'text': "Increases risk: Short Tenure", 'score': imp})
                elif feat == 'tenure' and val > 0.6:
                    impacts.append({'feature': 'Long Tenure', 'type': 'positive', 'text': "Decreases risk: Long Tenure", 'score': imp})
                elif feat == 'MonthlyCharges' and val > 0.6:
                    impacts.append({'feature': 'High Monthly Charges', 'type': 'negative', 'text': "Increases risk: High Monthly Charges", 'score': imp})

        # Sort by importance and return top 3 negative and top 2 positive
        impacts = sorted(impacts, key=lambda x: x['score'], reverse=True)
        xai = {
            'risk_drivers': [i['text'] for i in impacts if i['type'] == 'negative'][:3],
            'retention_factors': [i['text'] for i in impacts if i['type'] == 'positive'][:2],
            'impacts': impacts[:5] # raw data for UI
        }

        return {
            'prediction': 'Churn' if int(prediction) == 1 else 'No Churn',
            'probability': churn_prob,
            'confidence': confidence,
            'risk_level': risk_level,
            'xai': xai
        }
