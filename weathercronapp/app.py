import sqlite3
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import os
import configparser

DATA_PATH = 'data'
if os.path.exists(DATA_PATH) == False:
   os.mkdir(DATA_PATH)
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS WEATHER_TB (main TEXT NOT NULL, pop REAL NOT NULL, d_date TEXT NOT NULL)"
conn = sqlite3.connect(os.path.join(DATA_PATH,'database.db'), check_same_thread=False)
#conn = sqlite3.connect("/app/data/database.db")
cursor = conn.cursor()
cursor.execute(CREATE_TABLE)
conn.commit()
conn.close()
config = configparser.ConfigParser()
config.read(os.path.join(DATA_PATH, 'configfile.ini'))
irrigation = config['weathersettings']


api_key = 'be2cd6aacc1d683d9e90307476bde268'
lat = irrigation['lat']
lon = irrigation['lon']
url = 'https://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&appid=%s&units=metric' % (lat, lon, api_key)

retry_strategy = Retry(
    total=4,  # Maximum number of retries
    backoff_factor=2,  # Exponential backoff factor (e.g., 2 means 1, 2, 4, 8 seconds, ...)
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
)

adapter = HTTPAdapter(max_retries=retry_strategy)
 
# Create a new session object
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

try:
    response = session.get(url, timeout= 10)
    if(response.status_code == 200):
        data = json.loads(response.text)['list']
        #DELETE_DATA = '''DELETE FROM WEATHER_TB WHERE DATE(d_date) < "%s"''' % (datetime.today().date())
        DELETE_DATA = 'DELETE FROM WEATHER_TB'
        INSERT_DATA = 'INSERT INTO WEATHER_TB (main, pop, d_date) VALUES (?, ?, ?)'
        conn = sqlite3.connect(os.path.join(DATA_PATH,'database.db'), check_same_thread=False)
        # conn = sqlite3.connect("/app/data/database.db")
        cursor = conn.cursor()
        cursor.execute(DELETE_DATA)
        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=4)
        for d in data:
            d_date = datetime.strptime(d['dt_txt'], '%Y-%m-%d %H:%M:%S')
            if d_date.date() >= start_date and d_date.date() <= end_date:
                cursor.execute(INSERT_DATA, (d['weather'][0]['main'], d['pop'], d_date.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        # print (f'Data Inserted successfully: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
        conn.close()
    else:
        print('FAILED')
except requests.exceptions.ConnectionError:
    print('build http connection faild')
except requests.exceptions.Timeout:
    print('Connection timeout')
