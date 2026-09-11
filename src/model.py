import shap
from catboost import CatBoostClassifier


model = CatBoostClassifier()
model.load_model("models/model.cbm")
explainer = shap.TreeExplainer(model)
