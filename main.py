from src.database.ingestion import Neo4jImporter

importer = Neo4jImporter(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="pillsgap",
    database="products",
)

importer.import_embeddings_data(
    "./data/amazon_sample_metadata_2023_with_embeddings.parquet"
)
