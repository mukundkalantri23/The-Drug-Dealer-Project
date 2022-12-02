from flask import Flask, request, Response
from flaskext.mysql import MySQL
from minio import Minio
import os, sys, redis, json, jsonpickle, uuid, base64, pandas as pd, numpy as np

app = Flask(__name__)

# ---------REDIS CONFIGURATIOM----------

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
redisClient.lpush("logging", str({"rest.logs":"redis up and running!"}))

# ---------MINIO CONFIGURATIOM----------

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

recieptbucket = 'reciept'

if not client.bucket_exists(recieptbucket):
    print(f"Creating bucket {recieptbucket}")
    sys.stdout.flush()
    sys.stderr.flush()
    client.make_bucket(recieptbucket)
    redisClient.lpush("logging", str({"rest.logs.queue_bucket_created":recieptbucket}))
    
# # ---------MYSQL CONFIGURATIOM----------

mysql = MySQL()

app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("db_root_password")
app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_SERVICE_HOST")
app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_SERVICE_PORT"))
mysql.init_app(app)

db_name = os.getenv('db_name')

conn = mysql.connect()
cursor = conn.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
cursor.execute(f"USE {db_name}")

cursor.execute("CREATE TABLE IF NOT EXISTS data (medicine VARCHAR(128), form VARCHAR(64), price FLOAT, quantity TINYINT, pharmacy_name VARCHAR(128))")

med_data = pd.read_csv('medicine_details.csv')
val = []

for i in range(100):
    no_med = np.random.randint(75,150)
    med_index = np.random.randint(0,len(med_data),no_med)
    med_index.sort()
    med_inventory = med_data.loc[med_index, :]
    med_inventory['quantity'] = list(np.random.randint(1,15,len(med_inventory)))
    med_inventory['pharmacy_name'] = [f'pharmacy_{i}'] * len(med_inventory)
    print(len(med_inventory))
    val += list(zip( med_inventory['medicine'], med_inventory['form'], med_inventory['price'], med_inventory['quantity'], med_inventory['pharmacy_name']))

sql = "INSERT INTO data VALUES (%s, %s, %s, %s, %s)"
cursor.executemany(sql, val)
conn.commit()

print('Total rows inserted:', len(val))
redisClient.lpush("logging", str({"rest.logs":f"dataset initialized with {len(val)} rows"}))
del val

cursor.close()
conn.close()

# --------routes--------

@app.route('/', methods=['GET'])
def health():
    return '<h1> Drug Dealer Server </h1><p> Use a valid endpoint </p>'

@app.route('/get_min_shops', methods=['POST', 'GET'])
def get_min_shops():
    print('Inside get_min_shops...')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":"new request recieved"}))

    im_b64 = request.json['image']
    print('Data extracted!')
    sys.stdout.flush()
    sys.stderr.flush()

    hash_value = uuid.uuid4().hex
    fname = "%s.png" % hash_value
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))
    newFile = open(fname, "wb")
    newFile.write(img_bytes)
    print('Image file created!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"Image created - {fname}"}))

    client.fput_object(recieptbucket, fname, f"./{fname}")
    print('Image uploaded to minio!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"Image uploaded to minio - {fname}"}))

    os.remove(fname)
    print('Image deleted from local system.')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"Image removed from local - {fname}"}))

    redisClient.lpush("toWorker", str({"rest.worker.fname":fname}))
    print('Redis worker queue updated!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":"worker queue updated"}))
    
    response_pickled = jsonpickle.encode({'hash': hash_value, 'reason': 'Check your email for output'})
    return Response(response=response_pickled, status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
    # app.debug = True
    # app.run(host='0.0.0.0', port=5002)
    # app.run(debug = True, threaded=True)