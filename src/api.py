from fastapi import FastAPI, HTTPException
from src.database import get_client_from_db
from src.inference import predict_client
app = FastAPI(title="Bank Churn Prediction API")

@app.get("/", tags=["General"])
def root():
    return {"message": "Bank Churn Prediction API"}

@app.get("/client/{client_id}", tags=["Client"])
def get_client(client_id: int):
    client = get_client_from_db(client_id)

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return client

@app.get("/predict/{client_id}", tags=["Prediction"])
def predict(client_id: int):
    result = predict_client(client_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return result