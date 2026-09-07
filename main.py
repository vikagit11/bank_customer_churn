import pandas as pd
import psycopg2
import shap
import os
import redis
import json
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from catboost import CatBoostClassifier

load_dotenv()
app = FastAPI(title="Bank Churn Prediction API")


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True                            #возвращает обычные строки
)


model = CatBoostClassifier()
model.load_model("models/model.cbm")
explainer = shap.TreeExplainer(model)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать !!!"}

def get_client_from_db(client_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM clients WHERE customer_id = %s",
            (client_id,)
        )
        return cursor.fetchone()
@app.get("/client/{client_id}")
def get_client(client_id: int):
    client = get_client_from_db(client_id)

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return client

@app.get("/predict/{client_id}")
def predict_churn(client_id: int):
    cache_key = f"predict:{client_id}"
    cached_result = redis_client.get(cache_key)

    if cached_result:
        result = json.loads(cached_result)
        result["source"] = "redis"
        return result
    client = get_client_from_db(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    
    features = {
        "CreditScore": client["credit_score"],
        "Geography": client["geography"],
        "Gender": client["gender"],
        "Age": client["age"],
        "Tenure": client["tenure"],
        "Balance": client["balance"],
        "NumOfProducts": client["num_of_products"],
        "HasCrCard": client["has_cr_card"],
        "IsActiveMember": client["is_active_member"],
        "EstimatedSalary": client["estimated_salary"],
        "Satisfaction Score": client["satisfaction_score"],
        "Card Type": client["card_type"],
        "Point Earned": client["point_earned"]
    }


    X = pd.DataFrame([features])
    shap_values = explainer(X)

    values = shap_values.values[0]
    feature_names = X.columns.tolist()

    factors = sorted(
        zip(feature_names, values),
        key=lambda x: abs(x[1]),
        reverse=True
        )[:5]   
    
    probability = model.predict_proba(X)[0][1]

    
    prediction = int(model.predict(X)[0])

   
    result = {
        "customer_id": client_id,
        "churn_probability": round(float(probability), 3),
        "prediction": prediction,
        "top_factors": [
            {
                "feature": feature,
                "value": features[feature],
                "shap": round(float(value), 3),
                "impact": "повышает риск ухода" if value > 0 else "снижает риск ухода"
            }
            for feature, value in factors
        ],
        "source": "model"
    }

    redis_client.set(
        cache_key,
        json.dumps(result),
        ex=3600
    )

    return result