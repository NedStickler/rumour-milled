import boto3
import os
from typing import Optional


class HeadlineStore:
    def __init__(
        self,
        region_name: str = "us-west-2",
        endpoint_url: str = "http://localhost:8000",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        **kwargs
    ):
        if aws_access_key_id is None:
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        if aws_secret_access_key is None:
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

        self.db = boto3.resource(
            "dynamodb",
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            **kwargs
        )
        if not self._table_exists("Headlines"):
            self.table = self.create_table()
        else:
            self.table = self.db.Table("Headlines")

    def _table_exists(self, table_name):
        return table_name in [table.name for table in self.db.tables.all()]

    def create_table(self):
        table = self.db.create_table(
            TableName="Headlines",
            KeySchema=[
                {"AttributeName": "headline", "KeyType": "HASH"},
                {"AttributeName": "label", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "headline", "AttributeType": "S"},
                {"AttributeName": "label", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        return table

    def put_item(self, item):
        self.table.put_item(Item=item)

    def put_items(self, items):
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)


if __name__ == "__main__":

    def print_items():
        response = hs.table.scan()
        items = response["Items"]
        for item in items:
            print(item)

    hs = HeadlineStore(aws_access_key_id="dummy", aws_secret_access_key="dummy")
    headlines = (
        "How the rise of green tech is feeding another environmental crisis",
        "Aliens contact Washington with meeting planned this afternoon",
    )
    labels = (0, 1)
    items = [
        {"headline": headline, "label": label}
        for headline, label in zip(headlines, labels)
    ]
    hs.put_items(items)
    print_items()
