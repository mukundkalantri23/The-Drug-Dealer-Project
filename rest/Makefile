VERSION=v3
DOCKERUSER=mukundkalantri23

build:
	docker build -f Dockerfile -t mysql-rest .

push:
	docker tag mysql-rest $(DOCKERUSER)/mysql-rest:$(VERSION)
	docker push $(DOCKERUSER)/mysql-rest:$(VERSION)
	docker tag mysql-rest $(DOCKERUSER)/mysql-rest:latest
	docker push $(DOCKERUSER)/mysql-rest:latest
