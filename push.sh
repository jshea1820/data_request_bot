# Log into ECR
REGION=$(aws configure get region)
AWS_ECR_TOKEN=$(aws ecr get-login-password --region ${REGION})
AWS_ACCOUNT_NUMBER=$(aws sts get-caller-identity --query Account --output text)

# Log into registry with docker 
docker login --username AWS --password ${AWS_ECR_TOKEN} ${AWS_ACCOUNT_NUMBER}.dkr.ecr.${REGION}.amazonaws.com

# Tag the built image with the ECR repo
docker tag ${IMAGE_NAME} ${AWS_ACCOUNT_NUMBER}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}

# Push
docker push ${AWS_ACCOUNT_NUMBER}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}

