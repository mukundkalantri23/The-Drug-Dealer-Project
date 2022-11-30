import os, sys, redis, json, shutil
from minio import Minio

redisHost = os.getenv("REDIS_HOST") or "host.docker.internal" # or "localhost" # 
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

print('Redis connection done!')
sys.stdout.flush()
sys.stderr.flush()

minioHost = os.getenv("MINIO_HOST") or "host.docker.internal:9000" # "localhost:9000" # 
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

client = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

print('Minio connection done!')
sys.stdout.flush()
sys.stderr.flush()

queuebucket = 'queue'
outputbucket = 'output'

while True:
    try:
        work = redisClient.blpop("toWorker", timeout=0)
        msg = json.loads(work[1].decode('utf-8').replace("\'", "\""))
        fname = list(msg.values())[0]
        redisClient.lpush("logging", str({"worker.logs.processing_file":fname}))
        
        data = client.get_object(queuebucket, fname)
        with open(fname, 'wb') as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)
        redisClient.lpush("logging", str({"worker.logs.mp3_downloaded":fname}))
        
        os.system(f"python3 -m demucs.separate --out /tmp/output --mp3 {fname}")
        redisClient.lpush("logging", str({"worker.logs.music_file_seperated": f"tmp/output/mdx_extra_q/{fname}"}))

        split_files = os.listdir(f'tmp/output/mdx_extra_q/{fname[:-4]}')
        for split in split_files:
            client.fput_object(outputbucket, f"{fname[:-4]}/{split}", f"./tmp/output/mdx_extra_q/{fname[:-4]}/{split}")
        redisClient.lpush("logging", str({f"worker.logs.{fname[:-4]}.splits.mp3_uploaded_to_minio":f"{fname[:-4]}/{split}"}))

        os.remove(fname)
        shutil.rmtree(f'tmp/output/mdx_extra_q/{fname[:-4]}')
        redisClient.lpush("logging", str({"worker.logs.music_file_and_splits_deleted_from_local": f"{fname}"}))

    except Exception as exp:
        print(f"Exception raised in log loop: {str(exp)}")
        sys.stdout.flush()
        sys.stderr.flush()