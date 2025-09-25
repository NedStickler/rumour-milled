set -eu

awslocal() { aws --endpoint-url "${AWS_ENDPOINT_URL}" "$@"; }

BUCKET="rm-local-training-bucket"

awslocal s3api create-bucket \
    --bucket "${BUCKET}" \
    --create-bucket-configuration LocationConstraint="${AWS_REGION}" || true

echo "S3 ready. Bucket=${BUCKET}"