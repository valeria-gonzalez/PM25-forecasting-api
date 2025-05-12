import pymysql
import numpy as np

class DBManager:
    def __init__(self, host:str, port:int, user:str, password:str, db:str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
    
    def _open(self)->None:
        """Open connection to database"""
        self.connection = pymysql.connect(host=self.host,
                                          port=self.port,
                                          user=self.user,
                                          password=self.password,
                                          db=self.db)
    
    def _close(self)->None:
        """Close connection to database"""
        self.connection.close()
        
    def get_last_n_daily_data(self, n:int)->tuple:
        """Retrieve data for last n days. It includes daily readings for PM25, 
        temperature, relative, humidity, wind speed and wind direction (in this
        order).
        
        Args:
            n (int): Number of past days to retrieve.

        Returns:
            tuple: A tuple with nested entries for each daily data.
        """
        self._open()
        cursor = self.connection.cursor()
        query = f""" 
            SELECT d.pm25, d.tmp, d.rh, d.ws, d.wd 
            FROM daily_data d
            ORDER BY id DESC
            LIMIT {n};
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self._close()
        return np.asarray(result)
    
    def get_yesterdays_data(self)->dict:
        """Retrieve the previous day's daily data as a dictionary. It includes 
        daily readings for PM25, temperature, relative, humidity, wind speed and
        wind direction (in this order).

        Returns:
            dict: Dictionary containing information.
        """
        self._open()
        cursor = self.connection.cursor()
        query = f""" 
            SELECT d.pm25, d.tmp, d.rh, d.ws, d.wd 
            FROM daily_data d
            ORDER BY id DESC
            LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self._close()
        
        result = np.asarray(result).flatten()
        data = {
            "pm25": float(result[0]), 
            "tmp": float(result[1]), 
            "rh": float(result[2]), 
            "ws": float(result[3]),
            "wd": float(result[4])
        }
        return data
    
    def daily_data_exists(self, date:str)->int:
        """Check if a daily data entry with a given date (YYYY-MM-DD) exists.

        Args:
            date (str): Date of data entry.

        Returns:
            int: id of entry if exists, None otherwise
        """
        
        self._open()
        cursor = self.connection.cursor()
        query = """
            SELECT d.id FROM daily_data d WHERE d.date = %s
        """
        cursor.execute(query,(date))
        result = cursor.fetchall()
        cursor.close()
        self._close()
        
        if len(result) == 0:
            return None
        else:
            return result[0][0]
        
    def update_daily_data(self, data_id: int, data:dict)->None:
        """Updates a daily data entry in the database. The entry information 
        must include date (YYYY-MM-DD), PM25, temperature, relative humidity, 
        wind speed and wind direction.

        Args:
            data (dict): Dictionary containing information.
        """
        try:
            self._open()
            cursor = self.connection.cursor()
            query = """
                UPDATE daily_data 
                SET pm25 = %s, tmp = %s, rh = %s, ws = %s, wd = %s
                WHERE id = %s;
            """
            cursor.execute(query, (
                data["pm25"],
                data["tmp"],
                data["rh"],
                data["ws"],
                data["wd"],
                data_id
            ))
            self.connection.commit()
        except Exception as e:
            print(f"Error updating daily data: {e}")
        finally:
            self._close()
    
    def insert_daily_data(self, data:dict)->None:
        """Inserts a daily data entry to the database. This entry must include 
        information for the date (YYYY-MM-DD), PM25, temperature, 
        relative humidity, wind speed and wind direction.

        Args:
            data (dict): Dictionary containing information.
        """
        try:
            self._open()
            cursor = self.connection.cursor()
            query = """
                INSERT INTO daily_data (date, pm25, tmp, rh, ws, wd)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data["date"],
                data["pm25"],
                data["tmp"],
                data["rh"],
                data["ws"],
                data["wd"]
            ))
            self.connection.commit()
        except Exception as e:
            print(f"Error inserting daily data: {e}")
        finally:
            self._close()
        
        
        