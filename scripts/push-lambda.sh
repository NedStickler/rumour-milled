ENVFILE=".env"

if [[ -f "$ENVFILE" ]]; then
    echo "> Loading env vars from $ENVFILE"
    set -a
    source "$ENVFILE"
    set +a
fi

export DOCKER_DEFAULT_PLATFORM=linux/amd64
export BUILDX_NO_DEFAULT_ATTESTATIONS=1

docker build -f services/scrape_finish_handler/Dockerfile -t rm-dev-lambda-scrape-finish-handler:latest .
docker tag rm-dev-lambda-scrape-finish-handler:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/rumour-milled/rm-dev-lambda-scrape-finish-handler:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/rumour-milled/rm-dev-lambda-scrape-finish-handler:latest
aws lambda create-function --function-name rm-dev-lambda-scrape-finish-handler --package-type Image --code ImageUri="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/rumour-milled/rm-dev-lambda-scrape-finish-handler:latest" --role "arn:aws:iam::$AWS_ACCOUNT_ID:role/rm-dev-lambda-scrape-finish-handler-exec-role"