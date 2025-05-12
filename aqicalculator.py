from typing import Tuple

class AqiCalculator:
    """ Air Quality Index (AQI) calculator.
    Consult here: https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf 
    """
    def __init__(self):
        self.breakpoints_table = dict()
        self.aqi_recommendations = dict()
        self._initialize_recommendations()
        self._initialize_breakpoints()

    def _find_breakpoints(self, pollutant: str, concentration: float) -> list:
        """Find the AQI value breakpoints that encompass the concentration of a 
        given pollutant. 

        Args:
            pollutant (str): Name of pollutant (o3, pm25, pm10, co, so2, no2)
            concentration (float): Concentration of the pollutant.

        Returns:
            list: List of tuples with both ranges [(concentration breakpoints), (AQI breakpoints)].
        """
        
        breakpoints = [] # [(concentration breakpoints), (AQI breakpoints)]
        
        pollutant_breakpoints = self.breakpoints_table[pollutant]
        
        # Find the breakpoints for AQI and concentration
        for concentration_breakpoint in pollutant_breakpoints.keys():
            concentration_lower, concentration_upper = concentration_breakpoint
            
            if(concentration_lower <= concentration <= concentration_upper):
                aqi_breakpoint = pollutant_breakpoints[concentration_breakpoint]
                
                breakpoints.append(concentration_breakpoint)
                breakpoints.append(aqi_breakpoint)
                
                return breakpoints
            
        return None  
    
    def get_pollutant_aqi_num(self, pollutant: str, concentration: float) -> int:
        """Calculate the AQI index given the concentration of a pollutant.

        Args:
            pollutant (str): Name of pollutant (o3, pm25, pm10, co, so2, no2)
            concentration (float): Concentration of the pollutant.

        Returns:
            int: AQI index.
        """
        if concentration == 0:
            return 0
        
        breakpoints = self._find_breakpoints(pollutant, concentration)
        aqi_index = 0
        
        if breakpoints:
            concentration_breakpoint, aqi_breakpoint = breakpoints
            
            con_lower, con_upper = concentration_breakpoint
            aqi_lower, aqi_upper = aqi_breakpoint
            
            try: 
                # Equation to calculate AQI
                aqi_index = ((aqi_upper - aqi_lower) / (con_upper - con_lower)) 
                aqi_index *= (concentration - con_lower)
                aqi_index += aqi_lower
                aqi_index = round(aqi_index)
            except ZeroDivisionError:
                aqi_index = 0
        
        return aqi_index
    
    def get_pollutant_aqi_str(self, aqi_index: int) -> Tuple[str,str]:
        """Calculate the AQI index given the concentration of a pollutant.

        Args:
            aqi_index (float): Numerical AQI index.

        Returns:
            Tuple[str,str]: Categorical value for the AQI index and Hexadecimal 
            color value.
        """
        if aqi_index <= 50: 
            return ("Good", "00E400")
        elif aqi_index <= 100: 
            return ("Moderate", "FFFF00")
        elif aqi_index <= 150: 
            return ("Unhealthy for Sensitive Groups", "FF7E00")
        elif aqi_index <= 200: 
            return ("Unhealthy", "FF0000")
        elif aqi_index <= 300: 
            return ("Very Unhealthy", "8F3F97")
        else: 
            return ("Hazardous", "7E0023")
        
    def get_aqi_recommendations(self, pollutant:str, aqi_cat:str):
        return self.aqi_recommendations[pollutant][aqi_cat]
        
    def _initialize_recommendations(self):
        asthma_tip = "People with asthma: Follow your asthma action plan and keep quick-relief medicine handy."
        heart_tip = "People with heart disease: Symptoms such as palpitations, shortness of breath, or unusual fatigue may indicate a serious problem. If you have any of these, contact your health care provider."
        
        self.aqi_recommendations["pm25"] = {
            "Good": [
                "It's a great day to be active outside."
            ],
            "Moderate": [
                "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
            ],
            "Unhealthy for Sensitive Groups": [
                "Sensitive groups: Make outdoor activities shorter and less intense. It's OK to be active outdoors but take more breaks. Watch for symptoms such as coughing or shortness of breath.",
                asthma_tip,
                heart_tip
            ],
            "Unhealthy": [
                asthma_tip,
                heart_tip,
                "Sensitive groups: Consider rescheduling or moving all activities inside. Go inside if you have symptoms.",
                "Everyone else: Keep outdoor activities shorter and less intense. Go inside if you have symptoms."
            ],
            "Very Unhealthy": [
                asthma_tip,
                heart_tip,
                "Sensitive groups: Avoid all physical activity outdoors. Reschedule to a time when air quality is better or move activities indoors.",
                "Everyone else: Limit outdoor physical activity. Go indoors if you have symptoms."
            ],
            "Hazardous": [
                asthma_tip,
                heart_tip,
                "Sensitive groups: Stay indoors and keep activity levels light. Follow tips for keeping particle levels low indoors.",
                "Everyone: Avoid all physical activity outdoors."
            ]
        }
        
    def _initialize_breakpoints(self) -> None:
        """ Initialize the corresponding pollutant and AQI breakpoints table. """
        self.breakpoints_table["o3"] = {
           (0.000, 0.054) : (0, 50),
           (0.055, 0.070) : (51, 100),
           (0.071, 0.085) : (101, 150),
           (0.086, 0.105) : (151, 200),
           (0.106, 0.200) : (201, 300),
           (0.201, 1000000000) : (301, 500)
        }
       
        self.breakpoints_table["pm25"] = {
            (0.0, 9.0) : (0, 50),
            (9.1, 35.4) : (51, 100),
            (35.5, 55.4) : (101, 150),
            (55.5, 125.4) : (151, 200),
            (125.5, 225.4) : (201, 300),
            (225.5, 1000000000) : (301, 500)
        }
       
        self.breakpoints_table["pm10"] = {
            (0, 54) : (0, 50),
            (55, 154) : (51, 100),
            (155, 254) : (101, 150),
            (255, 354) : (151, 200),
            (355, 424) : (201, 300),
            (425, 1000000000) : (301, 500)
        }
        
        self.breakpoints_table["co"] = {
            (0.0, 4.4) : (0, 50),
            (4.5, 9.4) : (51, 100),
            (9.5, 12.4) : (101, 150),
            (12.5, 15.4) : (151, 200),
            (15.5, 30.4) : (201, 300),
            (30.5, 1000000000) : (301, 500)
        }
        
        self.breakpoints_table["so2"] = {
            (0, 35) : (0, 50),
            (36, 75) : (51, 100),
            (76, 185) : (101, 150),
            (186, 304) : (151, 200),
            (305, 604) : (201, 300),
            (605, 1000000000) : (301, 500)
        }
        
        self.breakpoints_table["no2"] = {
            (0, 53) : (0, 50),
            (54, 100) : (51, 100),
            (101, 360) : (101, 150),
            (361, 649) : (151, 200),
            (650, 1249) : (201, 300),
            (1250, 1000000000) : (301, 500)
        }