from src.database.ingestion import Neo4jImporter

importer = Neo4jImporter(
    uri="neo4j+s://df8984b6.databases.neo4j.io",
    user="neo4j",
    password="2aEd8LiA2dzva5eltTCC5SesllDW8Ucs_PjmQCic-h4",
    database="neo4j",
)

# importer.import_data("./dataset/amazon_sample_metadata_2023.parquet", batch_size=1000)
# importer.calculate_embeddings(
#     "./dataset/amazon_sample_metadata_2023.parquet", batch_size=1000
# )

importer.import_embeddings_data(
    "./data/amazon_sample_metadata_2023_with_embeddings.parquet"
)
