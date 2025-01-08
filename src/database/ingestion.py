import pandas as pd
import json

from typing import Dict, List, Any
from tqdm import tqdm
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer


class Neo4jImporter:
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        database: str = "neo4j",
        password: str = "pillsgap",
    ):
        self.driver = GraphDatabase.driver(
            uri, auth=(user, password), database=database
        )
        self.model = SentenceTransformer(
            "jinaai/jina-embeddings-v3", trust_remote_code=True
        )

    def setup_constraints(self):
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.title IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Store) REQUIRE s.name IS UNIQUE"
            )

    def create_product(
        self, tx, row: Dict[str, Any], embeddings: Dict[str, List[float]]
    ):
        query = """
        MERGE (p:Product {title: $title})
        SET p.description = $description,
            p.average_rating = toFloat($average_rating),
            p.rating_number = toInteger($rating_number),
            p.price = toFloat($price),
            p.features = $features,
            p.images = $images,
            p.brand = $brand,
            p.categories = $categories,
            p.manufacturer = $manufacturer,
            p.title_embedding = $title_embedding,
            p.description_embedding = $desc_embedding
        WITH p
        MERGE (s:Store {name: $store})
        MERGE (p)-[:SOLD_BY]->(s)
        WITH p
        MERGE (c:Category {name: $main_category})
        MERGE (p)-[:IS_OF_CATEGORY]->(c)
        """

        features = (
            json.dumps(row["features"])
            if isinstance(row["features"], (dict, list))
            else str(row["features"])
        )
        images = (
            json.dumps(row["images"])
            if isinstance(row["images"], (dict, list))
            else str(row["images"])
        )

        tx.run(
            query,
            title=row["title"],
            description=row["description"],
            average_rating=row["average_rating"],
            rating_number=row["rating_number"],
            price=row["price"],
            features=features,
            images=images,
            store=row["store"],
            brand=row["brand"],
            manufacturer=row["manufacturer"],
            main_category=row["main_category"],
            categories=row["categories"],
            title_embedding=embeddings["title"],
            desc_embedding=embeddings["description"],
        )

    def import_data(self, data_path: str, batch_size: int = 100):
        df = pd.read_parquet(data_path)
        self.setup_constraints()

        for i in tqdm(range(0, len(df), batch_size)):
            batch = df.iloc[i : i + batch_size]
            with self.driver.session() as session:
                for _, row in batch.iterrows():
                    embeddings = {
                        "title": self.model.encode(row["title"]).tolist(),
                        "description": self.model.encode(row["description"]).tolist(),
                    }
                    session.execute_write(self.create_product, row, embeddings)

        self.driver.close()
