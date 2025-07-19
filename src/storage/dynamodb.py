import boto3
from botocore.exceptions import ClientError

db = boto3.resource(
    "dynamodb",
    region_name="us-west-2",
    endpoint_url="http://localhost:8000",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy",
)


def create_table(db):
    try:
        table = db.create_table(
            TableName="TestTable",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        table.wait_until_exists()
        print("Table created.")
    except ClientError:
        print("Table already exists.")


if __name__ == "__main__":
    create_table(db)
    print("Tables now:", list(db.tables.all()))
