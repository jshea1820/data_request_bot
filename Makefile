include .env

build:
		docker build -t ${IMAGE_NAME} .
run:
		docker run -p 8000:8000 --env-file .env -t ${IMAGE_NAME}
push:
		docker build -t ${IMAGE_NAME} .
		. push.sh




