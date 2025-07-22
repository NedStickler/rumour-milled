import boto3
from dotenv import load_dotenv


class HeadlineStorage:
    """HeadlineStorage provides an interface to a DynamoDB table for storing and retrieving news headlines and their labels.

    This class manages the connection to DynamoDB, table creation, and basic CRUD operations for headline data.
    """

    def __init__(self, region_name: str = "eu-west-2", **kwargs):
        """Initialize the HeadlineStorage and connect to DynamoDB.

        Args:
            region_name (str): AWS region name. Defaults to "eu-west-2".
            **kwargs: Additional keyword arguments for boto3.resource.
        """
        load_dotenv()
        self.db = boto3.resource("dynamodb", region_name=region_name, **kwargs)
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
