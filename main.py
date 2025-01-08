import pandas as pd

from src.database.ingestion import Neo4jImporter

importer = Neo4jImporter(
    uri="neo4j+s://2d97deb5.databases.neo4j.io",
    user="neo4j",
    database="neo4j",
    password="XHrRfUiYu6CowDl9fLV7e9xBkeoc1sw1Z2Q_mtoa1n8",
)
products = pd.read_parquet("./data/amazon_sample_metadata_2023.parquet")[:100]
importer.add_batch_of_products(products)
