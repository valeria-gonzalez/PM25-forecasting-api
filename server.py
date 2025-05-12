from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from forecaster import PM25Forecaster
from database_manager import DBManager
from scraper import SemadetScraper
from pathlib import Path
import config

app = FastAPI()
# usage fastapi dev server.py
# docs: http://localhost:8000/docs

# Define response model for FastAPI docs and validation
class ForecastResponse(BaseModel):
    forecast: List[Dict[str, float]]

@app.get("/api/v1/forecast", response_model=ForecastResponse)
def get_next_seven_day_forecast():
    try:
        # Initialize database manager
        db = DBManager(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            db=config.db
        )

        # Initialize model and scaler
        model = PM25Forecaster(
            model_filepath=Path("models/lstm_seven_step.pkl"),
            scaler_filepath=Path("models/scaler.save")
        )

        # Initialize scraper
        scraper = SemadetScraper()

        # Step 1 - Get today's data
        todays_data = scraper.get_todays_data()
        if not todays_data:
            raise HTTPException(status_code=500, detail="Scraping returned no data")

        # Fill missing values with yesterday's data
        interpolate = [key for key, value in todays_data.items() if not value]
        if interpolate:
            yesterdays_data = db.get_yesterdays_data()
            for key in interpolate:
                todays_data[key] = yesterdays_data.get(key)

        # Step 2 - Insert or update today's data
        data_id = db.daily_data_exists(todays_data["date"])
        if data_id:
            db.update_daily_data(data_id, todays_data)
        else:
            db.insert_daily_data(todays_data)

        # Step 3 - Get last 30 days of data
        monthly_data = db.get_last_n_daily_data(30)

        # Step 4 - Run forecast
        predictions = model.forecast(monthly_data)

        # Step 5 - Return forecast
        forecast = [
            {f"Day {i+1}": round(pred, 2)} 
            for i, pred in enumerate(predictions)
        ]
        return {"forecast": forecast}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")
