VERSION=v1
DOCKERUSER=mukundkalantri23

build:
	docker build -f Dockerfile -t drugdealer-worker .
push:
	docker tag drugdealer-worker $(DOCKERUSER)/drugdealer-worker:$(VERSION)
	docker push $(DOCKERUSER)/drugdealer-worker:$(VERSION)
	docker tag drugdealer-worker $(DOCKERUSER)/drugdealer-worker:latest
	docker push $(DOCKERUSER)/drugdealer-worker:latest
