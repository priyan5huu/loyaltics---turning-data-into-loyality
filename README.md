# ◈ Loyalytics — Enterprise AI Churn Intelligence Platform

Loyaltics is a premium, production-ready telecom customer churn prediction SaaS application. It utilizes a Gradient Boosting model (with **82.4% ROC AUC**) to predict subscriber churn risk in real-time, providing retention suggestions and Explainable AI (SHAP-based) feature attributions.

---

## 🎨 UI/UX Design System (White/Beige theme)

Designed for elite finance and tech enterprise environments:
- **Clean Whites & Off-whites:** Crisp, airy backgrounds utilizing `#FAF8F4` and `#F3EEE6`.
- **Soft Shadows & Borders:** Glassmorphic, minimal card styles using a delicate beige border `#E8DFD0`.
- **Gold Accents:** Call-to-actions, badges, and details highlighted with premium gold `#C6A87A` and `#B08D5B`.
- **High Contrast:** Complete dark-text readability (`#1F1F1F` on light background), satisfying WCAG accessibility standards.

---

## 🛠 Directory Layout

```
files/
├── backend/            # Flask REST API
│   ├── app.py          # Main server entrypoint
│   ├── routes.py       # API endpoints (/predict, /history, /analytics, /health)
│   ├── preprocessing.py# Input transformation & scaling pipeline
│   ├── model_loader.py # Singleton model loader & SHAP calculator
│   └── history.json    # Local prediction database
├── frontend/           # Pure HTML/CSS/JS Static Client
│   ├── index.html      # 9-section premium page layout
│   ├── style.css       # White/Beige CSS design system
│   └── script.js       # Dynamic forms, Chart.js integrations & API handlers
├── models/             # Pre-trained ML artifacts
│   ├── churn_model.pkl # Scikit-learn Gradient Boosting Model
│   ├── scaler.pkl      # MinMaxScaler instance
│   ├── metrics.json    # AUC/Recall/Precision validation scores
│   └── analytics.json  # Pre-computed dataset distribution statistics
├── requirements.txt    # Production dependencies
├── Procfile            # Gunicorn process config
├── render.yaml         # Render Infrastructure-as-code configuration
└── README.md           # Documentation
```

---

## 🚀 Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python backend/app.py
   ```

3. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## ☁️ Deployment

### Render Deployment (Backend API + Frontend Static Serve)
1. Commit the repository to GitHub.
2. Go to [Render.com](https://render.com) and sign in.
3. Click **New +** -> **Blueprint**.
4. Connect your repository and deploy. The `render.yaml` file will automatically configure the Python service and spin it up on Gunicorn.
