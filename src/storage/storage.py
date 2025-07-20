import boto3
import os
from typing import Optional


class HeadlineStore:
    """HeadlineStore provides an interface to a DynamoDB table for storing and retrieving news headlines and their labels.

    This class manages the connection to DynamoDB, table creation, and basic CRUD operations for headline data.
    """

    def __init__(
        self,
        region_name: str = "us-west-2",
        endpoint_url: str = "http://localhost:8000",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the HeadlineStore and connect to DynamoDB.

        Args:
            region_name (str): AWS region name. Defaults to "us-west-2".
            endpoint_url (str): DynamoDB endpoint URL. Defaults to "http://localhost:8000".
            aws_access_key_id (Optional[str]): AWS access key ID. If None, uses environment variable.
            aws_secret_access_key (Optional[str]): AWS secret access key. If None, uses environment variable.
            **kwargs: Additional keyword arguments for boto3.resource.
        """
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
        """Check if a DynamoDB table exists.

        Args:
            table_name (str): Name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        return table_name in [table.name for table in self.db.tables.all()]

    def create_table(self):
        """Create the 'Headlines' DynamoDB table if it does not exist.

        Returns:
            Table: The created DynamoDB Table resource.
        """
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
        """Insert a single item into the Headlines table.

        Args:
            item (dict): The item to insert.
        """
        self.table.put_item(Item=item)

    def put_items(self, items):
        """Insert multiple items into the Headlines table using batch writer.

        Args:
            items (list[dict]): List of items to insert.
        """
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def get_items(self):
        """Retrieve all items from the Headlines table as (headline, label) pairs.

        Returns:
            list[tuple]: List of (headline, label) tuples.
        """
        scan = self.table.scan()
        items = scan["Items"]
        pairs = []
        for item in items:
            pairs.append((item["headline"], item["label"]))
        return pairs
