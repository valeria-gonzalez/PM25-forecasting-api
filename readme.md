con
# API de Pronóstico de PM2.5

Este proyecto proporciona una API que predice los niveles de **PM2.5** para los próximos 7 días utilizando datos meteorológicos. Se basa en aprendizaje automático y está diseñada para facilitar su implementación localmente.

---

## 🧰 Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Python** `>= 3.9.6`  
- **MySQL**
- **Git**

---

## 🔧 Guía de instalación

### 1. Clonar el repositorio

Primero, clona este repositorio a tu máquina local:

```bash
git clone https://github.com/usuario/tu-repo.git
cd tu-repo
```

> 🔁 *Sustituye el enlace con el de tu repositorio real.*

---

### 2. Crear un entorno virtual

Se recomienda crear un entorno virtual para evitar conflictos entre librerías.

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

### 3. Instalar dependencias

Con el entorno virtual activado, instala las librerías necesarias:

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias para que el proyecto funcione correctamente.

---

### 4. Configurar el archivo de conexión a base de datos

Debes copiar el archivo de ejemplo `config_example.py` y renombrarlo como `config.py`.

#### **Linux / macOS:**

```bash
cp config_example.py config.py
```

#### **Windows (CMD):**

```cmd
copy config_example.py config.py
```

> Este archivo contendrá tus credenciales de conexión a MySQL.

---

### 5. Crear base de datos en MySQL

Conéctate a MySQL:

```bash
mysql -u root -p
```

Luego ejecuta los siguientes comandos:

```sql
CREATE DATABASE weather;
USE weather;
```

Crea la tabla obligatoria `daily_data`:

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

### 6. Importar datos desde archivo CSV

Para permitir carga local de archivos, ejecuta:

```sql
SET GLOBAL local_infile=1;
```

Luego, sal de MySQL:

```sql
quit;
```

Ahora vuelve a entrar con soporte para archivos locales:

```bash
mysql --local-infile=1 -u root -p
```

Dentro de MySQL, selecciona la base de datos:

```sql
USE weather;
```

Carga los datos (reemplaza la ruta con la ubicación real del archivo CSV):

```sql
LOAD DATA LOCAL INFILE '/ruta/a/archivo/semadet-aire-bd.csv'
INTO TABLE daily_data
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
```

> ⚠️ Asegúrate de que el archivo CSV esté correctamente formateado y accesible.

---

### 7. Configurar `config.py`

Abre el archivo `config.py` y coloca tus credenciales de conexión a MySQL. Ejemplo:

```python
host = 'localhost'
port = 3306
user = 'root'
password = 'root'
db = 'weather'
```

---

## 🚀 Ejecutar la API

Con el entorno virtual activado y dentro del directorio del proyecto, ejecuta:

```bash
fastapi dev server.py
```

Esto iniciará la API en:

```
http://127.0.0.1:8000
```

### 📡 Endpoints

- `http://127.0.0.1:8000/api/v1/forecast` → Pronóstico de PM2.5 para los próximos 7 días.
- `http://127.0.0.1:8000/docs` → Documentación interactiva de la API (Swagger UI).

> 🛑 Para detener el servidor presiona `Ctrl + C`.

---

## ✅ ¡Listo!

Ahora tu API está lista para ser utilizada. Solo realiza llamadas al endpoint `/api/v1/forecast` para obtener los pronósticos diarios basados en los datos actuales de la base de datos.


