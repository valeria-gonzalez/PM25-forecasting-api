
# 🌫️  API de Pronóstico de PM2.5 en Tlaquepaque
Este proyecto implementa una API para la predicción de concentraciones de PM2.5 en el municipio de Tlaquepaque, Jalisco, utilizando un modelo de redes neuronales tipo LSTM (Long Short-Term Memory). La predicción se realiza para un horizonte de 7 días, a partir de datos atmosféricos de los últimos 30 días, incluyendo el día actual.

### Motivación
La contaminación del aire representa un importante problema de salud pública en el Área Metropolitana de Guadalajara (AMG), donde las concentraciones de PM10 y ozono (O₃) superan frecuentemente los límites considerados seguros. La exposición a material particulado, especialmente durante la temporada invernal, se asocia con riesgos graves para la salud, tales como cáncer pulmonar, neumonía y agravamiento del asma. La predicción de los niveles de contaminantes permite implementar medidas preventivas de forma oportuna, con el fin de proteger la salud de la población.

### ¿Por qué PM2.5?
Si bien el PM10 es el contaminante predominante en la región, el PM2.5, que presenta una alta correlación con el PM10 en esta zona, cuenta con un conjunto de datos más completo y confiable, lo que lo convierte en un mejor candidato para el desarrollo de modelos predictivos.

## 🔍 ¿De dónde provienen los datos?

- **Día actual:** La información correspondiente al día en curso se extrae directamente del sitio oficial de la Secretaría de Medio Ambiente y Desarrollo Territorial (SEMADET), disponible en [este enlace](https://aire.jalisco.gob.mx/porestacion), mediante un proceso automatizado de web scraping desarrollado con Selenium.

- **Datos históricos:** Los datos correspondientes a los 30 días anteriores (excluyendo el actual) provienen de una base de datos construida a partir de los archivos históricos proporcionados por SEMADET, disponibles en [este enlace](https://aire.jalisco.gob.mx/Dhistoricos).


## ⚙️ ¿Cómo funciona?

El sistema está compuesto por una API desarrollada en FastAPI, la cual expone un único endpoint:

- `GET /api/v1/forecast`  
  Este endpoint devuelve las predicciones de PM2.5 para los próximos 7 días en formato JSON, basadas en los datos de los últimos 30 días (incluido hoy).

  Devuelve un diccionario con el siguiente formato:

  - `day` : Día que se pronostica.
  - `pm25` : Índice de pm25 pronosticado.
  - `aqi_num` : Índice AQI numérico correspondiente.
  - `aqi_cat` : Categoría AQI correspondiente al índice AQI.
  - `aqi_color` : Color hexadecimal que le corresponde al índice AQI.
  - `recommendations` : Recomendaciones que se sugieren seguir para el índice AQI.

### 🧪 Ejemplo de respuesta JSON:

```json
{
  "forecast": [
    {
      "Day": 1,
      "pm25": 26.09385863225907,
      "aqi_num": 83,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 2,
      "pm25": 24.982506908290087,
      "aqi_num": 81,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 3,
      "pm25": 24.47068353369832,
      "aqi_num": 80,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 4,
      "pm25": 24.971195418760182,
      "aqi_num": 81,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 5,
      "pm25": 25.275221867486835,
      "aqi_num": 81,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 6,
      "pm25": 24.842046514339746,
      "aqi_num": 80,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    },
    {
      "Day": 7,
      "pm25": 23.10268336571753,
      "aqi_num": 77,
      "aqi_cat": "Moderate",
      "aqi_color": "FFFF00",
      "recommendations": [
        "Unusually sensitive people: Consider making outdoor activities shorter and less intense. Go inside if you have symptoms such as coughing or shortness of breath."
      ]
    }
  ]
}
```

### 🔄 Flujo del endpoint `/api/v1/forecast`

1. **Carga del modelo LSTM** preentrenado.
2. **Obtención del dato del día actual** desde la web de SEMADET vía web scraping.
3. **Actualización o inserción** del dato del día actual en la base de datos local.
4. **Consulta de los últimos 30 días** de datos desde la base de datos.
5. **Generación de predicción** usando el modelo LSTM y los datos de los últimos 30 días.
6. **Respuesta al usuario** en formato JSON con los valores estimados para los próximos 7 días.

## 📦 Estructura del proyecto

- `scraper.py`: Contiene la clase **`SemadetScraper`**, un scraper hecho con `Selenium` para obtener los datos del día actual desde el sitio oficial.
- `database_manager.py`: Contiene la clase **`DBManager`**, encargada de las operaciones con la base de datos (lectura, inserción, actualización) implementado con `PyMysql`.
- `forecaster.py`: Contiene la clase **`PM25Forecaster`**, que administra la carga del modelo y realiza la predicción usando los datos.
- `server.py`: Archivo principal de la API desarrollada con `FastAPI`, donde se define el endpoint `/api/v1/forecast`.
- `config.py`: Archivo que contiene las credenciales de la base de datos utilizada. Debe modificarse del archivo `config_example.py` con las credenciales propias.
- `semadet-aire-bd.csv`: Archivo con los datos históricos de la SEMADET para cargar a la base de datos.
- `requirements.txt`: Archivo que tiene los requerimientos de las librerías de Python necesarias para utilizar el proyecto.
---

## 🧰 Requisitos

Antes de comenzar, se debe tener instalado lo siguiente:

- **Python** `3.9.6`  
- **MySQL**
- **Git**
- **Google Chrome**

> 🛑 Es necesario tener instalada una versión de Google Chrome que sea compatible con ChromeDriver. Puedes verificar la versión instalada en `chrome://version` y descargar la versión correspondiente de ChromeDriver [aquí](https://chromedriver.chromium.org/downloads). Generalmente la versión más reciente es compatible, si ya tienes Google Chrome, solo asegurarse de que esté actualizado. Para este proyecto se usa la versión `136.0.7103.93`.

---

## 🔧 Guía de instalación

> 🛑 Nota: Todos los comandos deben ejecutarse desde la raíz del proyecto.

### 1. Clonar el repositorio

Clonar el repositorio del proyecto al entorno local mediante los siguientes comandos:

```bash
git clone https://github.com/valeria-gonzalez/PM25-forecasting-api.git
cd PM25-forecasting-api
```
---

### 2. Crear un entorno virtual

Se recomienda crear un entorno virtual para evitar conflictos entre librerías cuando se trabaja con Python. 

Para ello es necesario contar con la librería `venv`, que viene incluida a partir de Python 3.3. En la mayoría de instalaciones modernas de Python (>= 3.9.6), ya está disponible por defecto. 

Asimismo, se recomienda nombrar al entorno virtual como `env`, al terminar de ejecutar estos comandos, se tendrá un directorio llamado `env`.

Para hacer esto se pueden utilizar los siguiente comandos: 

#### **Linux / macOS:**

```bash
python3 -m venv env
source env/bin/activate
```

Para desactivar:

```bash
deactivate
```

#### **Windows (CMD o PowerShell):**

```cmd
python -m venv env
env\Scripts\activate
```

Para desactivar:

```cmd
deactivate
```

---
> ⚠️ Al activar el entorno virtual, deberá aparecer un (env) en la terminal.

> 🛑 Los siguientes pasos se pueden hacer sin esta sección. Sin embargo, todas las librerías se instalarán a tú entorno global y pueden existir conflictos entre versiones existentes.

### 3. Instalar dependencias

Con el entorno virtual activado, instalar las librerías necesarias mediante el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias para que el proyecto funcione correctamente.

---

### 4. Crear base de datos en MySQL

Para este paso es importante tener instalado MySQL. Una vez asegurado eso, conectarse a MySQL mediante el siguiente comando:

```bash
mysql -u root -p
```

Luego ejecutar los siguientes comandos:

```sql
CREATE DATABASE weather;
USE weather;
```

El nombre de la base de datos puede cambiar, solo asegurarse de especificarlo en el `config.py` (véase el paso 7).

Crear la tabla `daily_data`, este nombre no puede cambiar:

```sql
CREATE TABLE daily_data(
    id INT NOT NULL AUTO_INCREMENT,
    date DATE NOT NULL,
    pm25 FLOAT, 
    tmp FLOAT,
    rh FLOAT,
    ws FLOAT,
    wd FLOAT,
    PRIMARY KEY(id)
);
```

---

### 6. Importar datos históricos desde archivo CSV

Una vez creada la base de datos y la tabla, es necesario poblarla con los datos históricos de la SEMADET que se encuentran en el archivo `semadet-aire-bd.csv`. 

Para permitir carga local de archivos a MySQL, ejecutar:

```sql
SET GLOBAL local_infile=1;
```

Luego, salir de MySQL usando:

```sql
quit;
```

Volver a entrar con soporte para archivos locales:

```bash
mysql --local-infile=1 -u root -p
```

Dentro de MySQL, seleccionar la base de datos:

```sql
USE weather;
```

Cargar los datos a la tabla, es importante reemplazar la ruta del archivo CSV con la ubicación correcta en el entorno local:

```sql
LOAD DATA LOCAL INFILE '/ruta/a/archivo/semadet-aire-bd.csv'
INTO TABLE daily_data
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
```

> ⚠️ Asegúrate de que la ruta del archivo CSV esté correctamente escrito.

Una vez hecho esto, para que el proyecto funcione, algunos ordenadores requieren que la terminal de mysql permanezca abierta.
También es importante que durante todo este proceso el servidor de MySQL se encuentre activo.

---

### 7. Configurar `config.py`

Para que la API pueda obtener la información de la base de datos local, se deben escribir las credenciales en un archivo llamado `config.py`. Para hacer esto, copiar el archivo de ejemplo `config_example.py` y renombrarlo como `config.py`. 

Este archivo tiene la estructura necesaria con datos de ejemplo, reemplazarlos con los datos correctos.

Para copiar el contenido del archivo `config_example.py` y renombrarlo ejecutar los siguientes comandos:

#### **Linux / macOS:**

```bash
cp config_example.py config.py
```

#### **Windows (CMD):**

```cmd
copy config_example.py config.py
```

> Este archivo contendrá tus credenciales de conexión a MySQL.

Abrir el archivo `config.py` y colocar tus credenciales de conexión a MySQL. Ejemplo:

```python
host = 'localhost'
port = 3306
user = 'root'
password = 'root'
db = 'weather'
```

---

## 🚀 Ejecutar la API

Con el entorno virtual activado y dentro del directorio del proyecto, ejecutar:

```bash
fastapi dev server.py
```

Esto iniciará la API en:

```
http://127.0.0.1:8000
```

### 📡 Endpoints

Para ver como funciona la API, acceder a los siguientes endpoints:

- `http://127.0.0.1:8000/api/v1/forecast` → Pronóstico de PM2.5 para los próximos 7 días.
- `http://127.0.0.1:8000/docs` → Documentación interactiva de la API (Swagger UI).

> 🛑 Para detener el servidor presiona `Ctrl + C`.

---

## ✅ ¡Listo!

Ahora la API está lista para ser utilizada. Solo realiza llamadas al endpoint `/api/v1/forecast` para obtener los pronósticos diarios basados en los datos actuales de la base de datos.

---

## 🛠️ Posibles dificultades

### Urllib

Si al ejecutar el endpoint se obtiene el siguiente warning: 
```text
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with LibreSSL 2.8.3
```

Se puede ejecutar el siguiente comando, sin embargo, no debería impedir el funcionamiento del proyecto:
```bash
pip3 install urllib3==1.26.6
```

### Base de datos
Algunas cosas importantes son:

- Tener encendido el servidor de MySQL.
- Escribir las credenciales correctas en el `config.py`.
- Reenombrar el archivo `config_example.py` a `config.py`.
- Asegurarse que el puerto 3306 esté disponible, hay alternativas a este puerto dependiendo de la computadora.
- Algunos ordenadores requieren que la terminal de mysql permanezca abierta para ejecutar queries.

### Instalación en windows
Algunas cosas que podrían ayudar en la instalación son las siguientes:
- Cambiar `tensorflow-io-gcs-filesystem==0.37.1` por la versión `0.31.0` debido a la falta de soporte binario.
- Eliminar `uvloop==0.21.0` ya que no se nesesita en windows.

