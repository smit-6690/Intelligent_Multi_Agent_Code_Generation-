#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:?Set AWS_REGION}"
: "${AWS_ACCOUNT_ID:?Set AWS_ACCOUNT_ID}"
: "${VPC_ID:?Set VPC_ID}"
: "${PUBLIC_SUBNETS:?Set PUBLIC_SUBNETS as comma-separated subnet IDs}"
REPOSITORY="${ECR_REPOSITORY:-intellicode}"
TAG="${IMAGE_TAG:-latest}"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY}:${TAG}"
aws ecr describe-repositories --repository-names "$REPOSITORY" --region "$AWS_REGION" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "$REPOSITORY" --region "$AWS_REGION" >/dev/null
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
docker build -t "$IMAGE_URI" .
docker push "$IMAGE_URI"
aws cloudformation deploy \
  --stack-name intellicode-api \
  --template-file infra/aws/cloudformation.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides ImageUri="$IMAGE_URI" VpcId="$VPC_ID" PublicSubnets="$PUBLIC_SUBNETS" \
  --region "$AWS_REGION"
