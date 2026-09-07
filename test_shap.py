import shap
import pandas as pd
from catboost import CatBoostClassifier

# Загружаем модель
model = CatBoostClassifier()
model.load_model("models/model.cbm")
# Данные одного клиента
client = {
    "CreditScore": 644,
    "Geography": "Spain",
    "Gender": "Male",
    "Age": 28,
    "Tenure": 7,
    "Balance": 0.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 137000.0,
    "Satisfaction Score": 5,
    "Card Type": "DIAMOND",
    "Point Earned": 500
}

X = pd.DataFrame([client])

# SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer(X)

print("SHAP values:")
print(shap_values.values)

print("\nFeature names:")
print(X.columns.tolist())

# TOP-5 факторов
values = shap_values.values[0]
feature_names = X.columns.tolist()

factors = sorted(
    zip(feature_names, values),
    key=lambda x: abs(x[1]),
    reverse=True
)[:5]

print("\nTOP-5 factors:")

for feature, value in factors:
    print(feature, round(float(value), 3))