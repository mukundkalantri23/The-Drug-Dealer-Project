#!/bin/sh
# To kill the port-forward processes us e.g. "ps augxww | grep port-forward"
# to identify the processes ids
# get process id for a port: lsof -i:port_num
# terminate process: kill -9 port_num
#

kubectl create secret generic sendgrid-secret --from-file=worker/send_grid_API.txt
#kubectl get secret sendgrid-secret -o jsonpath='{.data}'

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f mysql/mysql-secret.yaml
kubectl apply -f mysql/mysql-storage.yaml
kubectl apply -f mysql/mysql-deployment.yaml

sleep 10

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-ingress.yaml

kubectl apply -f worker/worker-deployment.yaml

sleep 10

kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001 &

# Delete commands

# kubectl delete deployment logs
# kubectl delete deployment redis
# kubectl delete deployment mysql
# kubectl delete deployment rest
# kubectl delete deployment drugdealer-worker

# kubectl delete svc minio
# kubectl delete svc mysql
# kubectl delete svc redis
# kubectl delete svc rest-svc

# kubectl delete secret mysql-secret
# kubectl delete secret sendgrid-secret

# kubectl delete pv mysql-pv-volume
# kubectl delete pvc mysql-pv-claim

# kubectl delete ingress rest-ingress
