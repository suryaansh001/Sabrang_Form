import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

timeout = int(os.getenv('TIMEOUT', 10))
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=os.getenv('DB_NAME'),
  host=os.getenv('DB_HOST'),
  password=os.getenv('DB_PASSWORD'),
  read_timeout=timeout,
  port=int(os.getenv('DB_PORT')),
  user=os.getenv('DB_USER'),
  write_timeout=timeout,
)
  
try:
  cursor = connection.cursor()
  cursor.execute("CREATE TABLE cores (id INTEGER PRIMARY KEY)")
  cursor.execute("INSERT INTO cores (id) VALUES (1), (2)")
  cursor.execute("SELECT * FROM cores")
  print(cursor.fetchall())
finally:
  connection.close()