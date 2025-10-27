# train_save_model.py
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load your dataset
data = pd.read_csv("bank_personal_loan_data.csv")  # your dataset
X = data[['Age','Income','CCAvg','Education']]  # features
y = data['Personal Loan']  # target

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train XGBoost classifier
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "xgb_model.pkl")
joblib.dump(scaler, "scaler.pkl")  # optional if you want to scale inputs in app
print("Model saved successfully!")
