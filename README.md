# Financial-Risk-App

A simple Streamlit web app that predicts the financial risk level of loan applicants using an XGBoost model.
It takes key financial inputs and provides real-time predictions with visual insights.

🔗  Live Demo : https://financial-risk-app.streamlit.app/

✨ Core Features

The app is divided into four interactive tabs:

1. Loan Eligibility Check: Calculates EMI and Debt-to-Income (DTI), providing an instant approval/rejection decision.

2. Explainability (SHAP): Shows which individual factors (Credit Score, DTI, Income) pushed the decision toward approval (green) or rejection (red).

3. Financial Risk Calculator: Analyzes overall financial health, incorporating collateral, existing debt, and expenses to generate a risk score.

4. Detailed EMI Calculator: Visualizes the principal vs. interest payment schedule over the loan tenure.


⚙️ Tech Stack

Python – Core language for data analysis and ML development.

Streamlit – To build an intuitive, interactive web interface.

XGBoost – Chosen for strong predictive accuracy on data.

Scikit-learn – For preprocessing, feature scaling, and evaluation metrics.

Pandas & NumPy – For efficient data manipulation and numerical operations.

Matplotlib & Plotly – For clear, dynamic data visualizations.

SHAP – To provide model explainability and interpret risk predictions.
