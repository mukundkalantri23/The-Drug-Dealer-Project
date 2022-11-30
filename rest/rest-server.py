from flask import Flask, request, Response
from minio import Minio
import os, sys, redis, json, jsonpickle, uuid, base64
app = Flask(__name__)

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

queuebucket = 'queue'
outputbucket = 'output'

if not client.bucket_exists(queuebucket):
    print(f"Creating bucket {queuebucket}")
    sys.stdout.flush()
    sys.stderr.flush()
    client.make_bucket(queuebucket)
    redisClient.lpush("logging", str({"rest.logs.queue_bucket_created":queuebucket}))
    
if not client.bucket_exists(outputbucket):
    print(f"Creating bucket {outputbucket}")
    sys.stdout.flush()
    sys.stderr.flush()
    client.make_bucket(outputbucket)
    redisClient.lpush("logging", str({"rest.logs.output_bucket_created":outputbucket}))

# --------change this--------
@app.route('/', methods=['GET'])
def health():
    return '<h1> Music Separation Server</h1><p> Use a valid endpoint </p>'

@app.route('/apiv1/separate', methods=['POST', 'GET'])
def seperate():
    print('Separating track...')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":"new request recieved"}))

    data = request.json
    print('Data extracted!')
    sys.stdout.flush()
    sys.stderr.flush()

    hash_value = uuid.uuid4().hex
    fname = "%s.mp3" % hash_value
    newFile = open(fname, "wb")
    newFile.write(base64.b64decode(data['mp3']))
    print('New binary music file created!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"mp3 file created - {fname}"}))

    client.fput_object(queuebucket, fname, f"./{fname}")
    print('Music file uploaded to minio!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"mp3 file uploaded to minio - {fname}"}))

    os.remove(fname)
    print('Music file deleted from local system.')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":f"mp3 file removed from local - {fname}"}))

    redisClient.lpush("toWorker", str({"rest.worker.fname":fname}))
    print('Redis worker queue updated!')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.seperate":"worker queue updated"}))
    
    response_pickled = jsonpickle.encode({'hash': hash_value, 'reason': 'Song enqueued for separation'})
    return Response(response=response_pickled, status=200, mimetype='application/json')

@app.route('/apiv1/queue', methods=['GET'])
def queue():
    print('Getting queue')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.queue":"new request recieved"}))

    queue_output = []
    
    elements = redisClient.lrange( "toWorker", 0, -1 )
    for e in elements:
        dict_e = json.loads(e.decode('utf-8').replace("'",'"'))
        queue_output.append(list(dict_e.values())[0])
    
    redisClient.lpush("logging", str({"rest.logs.queue":f"current items in worker queue are - {queue_output}"}))
    return {'queue':queue_output}, 200

@app.route('/apiv1/track/<string:track>/<string:subtrack>', methods=['GET'])
def track(track, subtrack):
    print(f'Downloading track - {track}/{subtrack}.mp3')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.track":"new request recieved"}))

    try:
        data = client.get_object(outputbucket, f"{track}/{subtrack}.mp3")
        with open(f"{track}.mp3", 'wb') as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)
            redisClient.lpush("logging", str({"rest.logs.track":f"mp3_downloaded - {track}/{subtrack}.mp3"}))
        return (f'{track}/{subtrack} file downloaded')
    
    except Exception as exp:
        print(f"Exception raised in log loop: {str(exp)}")
        sys.stdout.flush()
        sys.stderr.flush()
        redisClient.lpush("logging", str({"rest.logs.track":f"There is an error: {str(exp)}"}))
        return {'Error': {str(exp)}}

@app.route('/apiv1/remove/<string:track>', methods=['GET'])
def remove(track):
    print('Downloading track')
    sys.stdout.flush()
    sys.stderr.flush()
    redisClient.lpush("logging", str({"rest.logs.remove":"new request recieved"}))

    try:
        client.remove_object(queuebucket, f"{track}.mp3")
        redisClient.lpush("logging", str({"rest.logs.remove":f"mp3_deleted - {track}.mp3"}))
        return (f'{track}.mp3 file deleted')
    
    except Exception as exp:
        print(f"Exception raised in log loop: {str(exp)}")
        sys.stdout.flush()
        sys.stderr.flush()
        redisClient.lpush("logging", str({"rest.logs.remove":f"There is an error: {str(exp)}"}))
        return {'Error': {str(exp)}}

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5002)
    app.run(debug = True, threaded=True)