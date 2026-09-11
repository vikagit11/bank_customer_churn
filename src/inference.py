import os 
import redis
import pandas as pd
import json
from dotenv import load_dotenv
from src.model import model, explainer
from src.database import get_client_from_db
load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),       
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True                            #возвращает обычные строки
)

def predict_client(client_id):
    cache_key = f"predict:{client_id}"

    cached_result = redis_client.get(cache_key)

    if cached_result:
        result = json.loads(cached_result)
        result["source"] = "redis"
        return result

    client = get_client_from_db(client_id)

    if client is None:
        return None
    
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