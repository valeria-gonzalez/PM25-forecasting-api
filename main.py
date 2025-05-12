from forecaster import PM25Forecaster
from database_manager import DBManager
from scraper import SemadetScraper
from aqicalculator import AqiCalculator
import config
import numpy as np

def main():
    db = DBManager(host=config.host, 
                   port=config.port, 
                   user=config.user, 
                   password=config.password,
                   db=config.db)
    
    model = PM25Forecaster(
        model_filepath="models/lstm_seven_step.pkl",
        scaler_filepath="models/scaler.save",
    )
    
    aqi_calc = AqiCalculator()
    
    # 1 - Scrape todays data
    scraper = SemadetScraper()
    todays_data = scraper.get_todays_data()
    
    # If empty values for today, fill in with yesterdays data
    interpolate = []
    for key, value in todays_data.items():
        if not value:
            interpolate.append(key)
    
    if interpolate:
        yesterday_data = db.get_yesterdays_data()
        for key in interpolate:     
            todays_data[key] = yesterday_data[key]
    
    # 2 - Insert or update todays data in database

    data_id = db.daily_data_exists(todays_data["date"])
    
    if data_id:
        db.update_daily_data(data_id, todays_data)
    else:
        db.insert_daily_data(todays_data)
    
    # 3 - Get last thirty days
    monthly_data = db.get_last_n_daily_data(30)
    
    # 4 - Forecast next 7 days
    yhat = model.forecast(monthly_data)
    print(yhat)
    
    for y in yhat:
        aqi_idx = aqi_calc.get_pollutant_aqi_num('pm25', y)
        aqi_cat, color = aqi_calc.get_pollutant_aqi_str(aqi_idx)
        print(f"y: {y}")
        print(f"aqi num: {aqi_idx}")
        print(f"aqi cat: {aqi_cat}, aqi color: {color}")
        print(aqi_calc.get_aqi_recommendations("pm25", aqi_cat))

if __name__ == "__main__":
    main()