import os, sys, redis, json, shutil, pandas as pd, numpy as np
from google.cloud import vision
from minio import Minio
import mysql.connector

# ---------REDIS CONFIGURATIOM----------

redisHost = os.getenv("REDIS_HOST") or "host.docker.internal"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

print('Redis connection done!')
sys.stdout.flush()
sys.stderr.flush()
redisClient.lpush("logging", str({"worker.logs":"redis up and running!"}))

# ---------MINIO CONFIGURATIOM----------

minioHost = os.getenv("MINIO_HOST") or "host.docker.internal:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

print('Minio connection done!')
sys.stdout.flush()
sys.stderr.flush()

recieptbucket = 'reciept'

# ---------MYSQL CONFIGURATIOM----------

conn = mysql.connector.connect(
  host=os.getenv("MYSQL_SERVICE_HOST"),
  user="root",
  password=os.getenv("db_root_password")
)

db_name = os.getenv('db_name')
table_name = os.getenv('table_name')

cursor = conn.cursor()

cursor.execute(f"USE {db_name}")
redisClient.lpush("logging", str({"worker.logs":f"mysql connected"}))

cursor.execute(f"SHOW COLUMNS FROM {db_name}.{table_name};")
myresult = cursor.fetchall()
columns = [c_data[0] for c_data in myresult]

print(columns)
sys.stdout.flush()
sys.stderr.flush()

# ---------Connecting with Google Vision API----------

path= 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=path

def text_detection(cont):
  
  client = vision.ImageAnnotatorClient()
  response = client.text_detection({'content' :cont})
  
  if response.error.message:
    raise Exception(f"check the website for {response.error.message}")
  
  return response

def img_txt(img):
  
  with open(img,'rb') as img_file:
    content=img_file.read()
  
  resp= text_detection(content)
  
  texts= resp.text_annotations
  lis = texts[0].description.split('\n')
  
  keys= lis[lis.index('Medicine Name')+1: lis.index('Quantity')]
  val= lis[lis.index('Quantity')+1: lis.index('Signature')]
  val = [int(x) for x in val]
  reciept_data =dict(zip(keys,val))
  
  return reciept_data

# ---------Algorithm Logic----------

def get_med_shop(med_list):
    med_shop = {}
    not_available = []
    for m in med_list:
        cursor.execute(f"SELECT * FROM data WHERE medicine = '{m}'")
        myresult = cursor.fetchall()
        df = pd.DataFrame(myresult, columns = columns)
        if len(df) == 0:
            not_available.append(m)
        else:
            med_shop[m] = list(zip(df['pharmacy_name'], df['quantity']))
    for m in not_available:
        del med_list[m]
    not_available_str = " ".join(not_available)
    return med_shop, not_available_str, med_list

def get_shop_med(med_list, med_shop):
    shop_med = {}
    for m in med_shop:
        for s,q in med_shop[m]:
            if s not in shop_med:
                shop_med[s] = []
            shop_med[s].append((m,q))
    shop_med = {k: shop_med[k] for k in sorted(shop_med, key=lambda x: len(shop_med[x]), reverse=True)}
    return shop_med

def get_output_data(shop_med, med_list):
    output = {}
    for s,mlist in shop_med.items():
        if len(med_list) != 0:
            for m,q in mlist:
                if m in med_list:
                    if s not in output:
                        output[s] = []
                    if q >= med_list[m]:
                        output[s].append((m,med_list[m]))
                        del med_list[m]
                    else:
                        output[s].append((m,q))
                        med_list[m] -= q
        else:
            break
    return output

def get_output_str(output):
    output_str = ''
    for s in output:
        output_str += s + '\n'
        for m,q in output[s]:
            output_str += '\t' + m + ": " + str(q) + '\n'
        output_str += '\n'
    return output_str

def get_output(med_list):
    med_shop, not_available_str, med_list = get_med_shop(med_list)
    shop_med = get_shop_med(med_list, med_shop)
    output = get_output_data(shop_med, med_list)
    output_str = get_output_str(output)
    if not_available_str != '':
        output_str += f'The following medicines are not available in any stores: {not_available_str}'
    return(output_str)

while True:
    try:
        work = redisClient.blpop("toWorker", timeout=0)
        msg = json.loads(work[1].decode('utf-8').replace("\'", "\""))
        fname = list(msg.values())[0]
        fname, email_id = fname.split('_')
        redisClient.lpush("logging", str({"worker.logs.processing_file":fname}))
        redisClient.lpush("logging", str({"worker.logs.output_email":email_id}))
        
        data = client.get_object(recieptbucket, fname)
        with open(fname, 'wb') as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)
        redisClient.lpush("logging", str({"worker.logs.Image downloaded":fname}))
        
        med_list = img_txt(fname)

        output = get_output(med_list)
        redisClient.lpush("logging", str({"worker.logs.output": f"{output}"}))

        os.remove(fname)
        redisClient.lpush("logging", str({"worker.logs.Image_deleted_from_local": f"{fname}"}))

        # Email logic remaining

    except Exception as exp:
        print(f"Exception raised in log loop: {str(exp)}")
        sys.stdout.flush()
        sys.stderr.flush()