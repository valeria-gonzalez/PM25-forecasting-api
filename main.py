from forecaster import PM25Forecaster
from database_manager import DBManager
from scraper import SemadetScraper
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

if __name__ == "__main__":
    main()