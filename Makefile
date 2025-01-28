include .env.configure

build:
		docker build -t ${IMAGE_NAME} .

shell:
		docker run -it --env-file .env ${IMAGE_NAME} bash

run:
		docker run -p 8000:8000 --env-file .env -t ${IMAGE_NAME}
push:
		docker build -t ${IMAGE_NAME} .
		. push.sh

