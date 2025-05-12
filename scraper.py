from typing import List
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SemadetScraper:
    def __init__(self):
        self.website_link = "https://aire.jalisco.gob.mx/porestacion"
        self.city = "Tlaquepaque"
        
    def _to_numerical(self, value:str)->float:
        """Convert a string to a float. If it can't be converted, returns None.

        Args:
            value (str): String to be converted.

        Returns:
            float: Float value of string or None.
        """
        try:
            float(value)
            return float(value)
        except ValueError:
            return None
            
    def _scrape_meteorological_data(self)->dict:
        """Scrape the meteorological data: temperature, relative humidity, 
        wind direction and wind speed from the Semadet website. It tries at
        least twice to do this, if it fails, it returns a dictionary with empty
        keys.

        Returns:
            dict: Dictionary with keys for tmp, rh, wd, and ws.
        """
        for attempt in range(2):
            driver = None
            try:
                op = webdriver.ChromeOptions()
                op.add_argument('headless')
                driver = webdriver.Chrome(options=op)
                driver.get(self.website_link)
                
                # Select city
                Select(driver.find_element(By.ID, "l_Estaciones")).select_by_value(self.city)

                # Select data type
                Select(driver.find_element(By.ID, "c_Tipo")).select_by_visible_text("Meteorología Horario")

                # Submit form
                driver.find_element(By.ID, "Button1").click()

                # Wait for the table to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "MET"))
                )

                # Wait for table rows to load
                WebDriverWait(driver, 20).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "#MET tr")
                )

                # Fetch fresh row references
                rows = driver.find_elements(By.CSS_SELECTOR, "#MET tr")
                
                # Dictionary to store table data in order
                data = { "tmp":[], "rh":[], "ws":[], "wd":[]}
                idxs = ["tmp", "rh", "wd", "ws"]

                for i, row in enumerate(rows):
                    try:
                        # Refetch the row in each iteration to avoid stale references
                        row = driver.find_elements(By.CSS_SELECTOR, "#MET tr")[i]
                        cells = row.find_elements(By.TAG_NAME, "td")
                    
                        if len(cells) == 5:  # Expected number of columns
                            for i, cell in enumerate(cells):
                                if i != 0:
                                    value = self._to_numerical(cell.text)
                                    if(value != None):
                                        data[idxs[i-1]].append(value)
                    except StaleElementReferenceException:
                        print(f"Row {i} went stale. Skipping.")
                        continue
                    
                driver.quit()
                return data
            
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error fetching meteorological data - {e}")
                
            finally:
                if driver:
                    driver.quit()

        return { "tmp":[], "rh":[], "ws":[], "wd":[]}
            
    def _scrape_pollutant_data(self)->dict:
        """Scrape the pollutant concentration data: particulate matter below 2.5 
        micrometers from the Semadet website. It tries at least twice to do this, 
        if it fails, it returns a dictionary with empty keys.

        Returns:
            dict: Dictionary with a key for pm25.
        """
        for attempt in range(2):
            driver = None
            try:
                op = webdriver.ChromeOptions()
                op.add_argument('headless')
                driver = webdriver.Chrome(options=op)
                driver.get(self.website_link)
                
                # Select city
                Select(driver.find_element(By.ID, "l_Estaciones")).select_by_value(self.city)

                # Select data type
                Select(driver.find_element(By.ID, "c_Tipo")).select_by_visible_text("Concentración Horario")

                # Submit form
                driver.find_element(By.ID, "Button1").click()

                # Wait for the table to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "CEN"))
                )

                # Wait for table rows to load
                WebDriverWait(driver, 20).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "#CEN tr")
                )

                # Fetch fresh row references
                rows = driver.find_elements(By.CSS_SELECTOR, "#CEN tr")
                
                # Dictionary to store table data in order
                data = { "pm25":[]}

                for i, row in enumerate(rows):
                    try:
                        # Refetch the row in each iteration to avoid stale references
                        row = driver.find_elements(By.CSS_SELECTOR, "#CEN tr")[i]
                        cells = row.find_elements(By.TAG_NAME, "td")
                    
                        if len(cells) == 7:  # Expected number of columns
                            for i, cell in enumerate(cells):
                                if i != 6:
                                    value = self._to_numerical(cell.text)
                                    if(value != None):
                                        data["pm25"].append(value)
                    except StaleElementReferenceException:
                        print(f"Row {i} went stale. Skipping.")
                        continue
                    
                driver.quit()
                return data
            
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error fetching pollutant data - {e}")
                
            finally:
                if driver:
                    driver.quit()

        return { "pm25":[]}
                
    def _circular_mean(self, angles:List[float])->float:
        """Calculate the circular mean of a list of angles between 0 and 360.

        Args:
            angles (List[float]): List of angles.

        Returns:
            float: Mean of all angles.
        """
        angles_rad = np.deg2rad(angles)  
        mean_sin = np.mean(np.sin(angles_rad))
        mean_cos = np.mean(np.cos(angles_rad))
        mean_angle = np.arctan2(mean_sin, mean_cos)  
        return float(np.rad2deg(mean_angle) % 360)
        
    def _avg_of_data(self, data:dict)->dict:
        """Calculate average of floating point values in a dictionary obtained
        from web scraping, to obtain the daily average of each value.

        Args:
            data (dict): Dictionary with information.

        Returns:
            dict: Dictionary with the average value of each entry.
        """
        # Average values for data
        avg_data = {}
        # Obtain average of all values
        for key, values in data.items():
            if not values: 
                avg_data[key] = None
            elif len(values) == 1:
                avg_data[key] = float(values[0])
            elif key == "wd":
                avg_data[key] = self._circular_mean(values)
            else:
                avg_data[key] = float(sum(values) / len(values))
                
        return avg_data
        
    def _get_meteorological_data(self)->dict:
        """Obtain the current day's meteorological data from the Semadet Website. 
        This data is: temperature, relative humidity, wind direction and wind 
        speed. It returns a dictionary with the average value of each entry. 
        The keys will have either value None or a float.
        
        Returns:
            Dict: Dictionary with entries for tmp, rh, wd, and ws.
        """
        data = self._scrape_meteorological_data()
        avg_data = self._avg_of_data(data)
        return avg_data
        
    def _get_pollutant_data(self):
        """Obtain the current day's pollutant concentration data from the 
        Semadet Website. This data is: particulate matter below 2.5 micrometers. 
        It returns a dictionary with the average value of each entry. The
        keys will have either value None or a float.
        
        Returns:
            Dict: Dictionary with entries for pm25.
        """
        data = self._scrape_pollutant_data()
        avg_data = self._avg_of_data(data)
        return avg_data
    
    def _todays_date(self):
        """Obtain a string of today's date as YYYY-MM-DD.

        Returns:
            str: Today's date.
        """
        # Get today's date
        today = datetime.today()
        # Format the date as YYYYMMDD
        formatted_date = today.strftime('%Y-%m-%d')
        return formatted_date
    
    def get_todays_data(self)->dict:
        """Get today's information from the Semadet website. This is: 
        temperature, relative humidity, wind direction, wind speed and 
        particulate matter below 2.5 micrometers. It will return a dictionary 
        with the following keys: date, tmp, rh, wd, and ws, and pm25. The
        keys will have either value None or a float.
        
        Returns:
            dict: A dictionary with today's data.
        """
        today = {"date": self._todays_date()}
        pltnt_data = self._get_pollutant_data()
        met_data = self._get_meteorological_data()
        return today | pltnt_data | met_data