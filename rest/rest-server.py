from flask import Flask, request, Response
from flaskext.mysql import MySQL
from minio import Minio
import os, sys, redis, json, jsonpickle, uuid, base64, pandas as pd, numpy as np

app = Flask(__name__)

# ---------REDIS CONFIGURATIOM----------

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

# ---------MINIO CONFIGURATIOM----------

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

queuebucket = 'queue'
outputbucket = 'output'

# if not client.bucket_exists(queuebucket):
#     print(f"Creating bucket {queuebucket}")
#     sys.stdout.flush()
#     sys.stderr.flush()
#     client.make_bucket(queuebucket)
#     redisClient.lpush("logging", str({"rest.logs.queue_bucket_created":queuebucket}))
    
# if not client.bucket_exists(outputbucket):
#     print(f"Creating bucket {outputbucket}")
#     sys.stdout.flush()
#     sys.stderr.flush()
#     client.make_bucket(outputbucket)
#     redisClient.lpush("logging", str({"rest.logs.output_bucket_created":outputbucket}))

# ---------MYSQL CONFIGURATIOM----------

mysql = MySQL()

# MySQL configurations
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("db_root_password") #or 'test1234'
app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_SERVICE_HOST")
app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_SERVICE_PORT"))
mysql.init_app(app)

db_name = os.getenv('db_name')

conn = mysql.connect()
cursor = conn.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
cursor.execute(f"USE {db_name}")

cursor.execute("CREATE TABLE IF NOT EXISTS data (medicine VARCHAR(128), form VARCHAR(64), price FLOAT, quantity TINYINT, pharmacy_name VARCHAR(128))")
# logic
med_data = pd.read_csv('medicine_details.csv')
val = []

for i in range(2):
    no_med = np.random.randint(75,150)
    med_index = np.random.randint(0,len(med_data),no_med)
    med_index.sort()
    med_inventory = med_data.iloc[med_index]
    med_inventory['quantity'] = list(np.random.randint(1,15,len(med_inventory)))
    med_inventory['pharmacy_name'] = [f'pharmacy_{i}'] * len(med_inventory)
    # med_inventory.to_csv(f'inventory_{i}.csv', index=False)
    print(len(med_inventory))
    val += list(zip( med_inventory['medicine'], med_inventory['form'], med_inventory['price'], med_inventory['quantity'], med_inventory['pharmacy_name']))
    
sql = "INSERT INTO data VALUES (%s, %s, %s, %s, %s)"

cursor.executemany(sql, val)
conn.commit()

# cursor.close()
# conn.close()

# --------routes--------
@app.route('/', methods=['GET'])
def health():
    return '<h1> Drug Dealer Server </h1><p> Use a valid endpoint </p>'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5002)
    app.run(debug = True, threaded=True)