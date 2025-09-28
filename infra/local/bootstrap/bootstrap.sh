set -eu

awslocal() { aws --endpoint-url "${AWS_ENDPOINT_URL}" "$@"; }

BUCKET="rm-local-training-bucket"
TABLE="rm-local-headlines-table"

# S3
awslocal s3api create-bucket \
    --bucket "${BUCKET}" \
    --create-bucket-configuration LocationConstraint="${AWS_REGION}"
echo "S3 ready. Bucket=${BUCKET}"

# DynamoDB
awslocal dynamodb create-table \
    --table-name "$TABLE" \
    --attribute-definitions \
        AttributeName=headline,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=headline,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10
echo "DynamoDB ready. Table=${TABLE}"
