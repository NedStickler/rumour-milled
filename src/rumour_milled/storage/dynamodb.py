import boto3
from dotenv import load_dotenv
from time import sleep
from typing import Optional


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
                sleep(0.075)

    def __parse_and_append(self, lst, items) -> list:
        """Parse DynamoDB items and append to a list."""
        for item in items:
            lst.append((item["headline"], item["label"]))

    def get_all_items(self) -> list[tuple[str, int]]:
        """Retrieve all items from the Headlines table.

        Returns:
            list[tuple[str, int]]: List of tuples containing headlines and their labels.
        """
        headlines = []
        scan = self.table.scan()
        self.__parse_and_append(headlines, scan["Items"])
        while "LastEvaluatedKey" in scan:
            scan = self.table.scan(ExclusiveStartKey=scan["LastEvaluatedKey"])
            self.__parse_and_append(headlines, scan["Items"])
            sleep(0.1)
        return headlines

    def get_filtered_items(
        self, filter_expression, max_items, page_limit=512
    ) -> list[tuple[str, int]]:
        """Retrieve items from the Headlines table based on a filter expression.

        Args:
            filter_expression (_type_): Filter expression to apply.
            max_items (int): Maximum number of items to retrieve.
            page_limit (int, optional): Max items returned for each DynamoDB page. Defaults to 512.

        Returns:
            list[tuple[str, int]]: List of tuples containing headlines and their labels.
        """
        headlines = []
        scan = self.table.scan(FilterExpression=filter_expression, Limit=page_limit)
        self.__parse_and_append(headlines, scan["Items"])
        while len(headlines) < max_items and "LastEvaluatedKey" in scan:
            scan = self.table.scan(
                ExclusiveStartKey=scan["LastEvaluatedKey"],
                FilterExpression=filter_expression,
                Limit=page_limit,
            )
            self.__parse_and_append(headlines, scan["Items"])
        return headlines[:max_items]
