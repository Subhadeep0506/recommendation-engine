import json
from typing import Any, Dict, List

import pandas as pd
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class Neo4jImporter:
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        database: str = "neo4j",
        password: str = "pillsgap",
    ):
        self.database = database
        self.uri = uri
        self.user = user
        self.password = password

        self.pre_checks()
        self.driver = GraphDatabase.driver(
            uri, auth=(user, password), database=database
        )
        self.model = SentenceTransformer(
            "jinaai/jina-embeddings-v3",
            trust_remote_code=True,
            device="cuda",
        )

    def pre_checks(self):
        driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        with driver.session() as session:
            result = session.run("SHOW DATABASES")
            databases = [record["name"] for record in result]
            if self.database not in databases:
                session.run(f"CREATE DATABASE {self.database}")
                print(f"Database '{self.database}' created.")

    def create_product_query(self) -> str:
        query = """
        UNWIND $products AS product
        MERGE (p:Product {title: product.title})
        SET p.description = product.description,
            p.average_rating = toFloat(product.average_rating),
            p.rating_number = toInteger(product.rating_number),
            p.price = toFloat(product.price),
            p.features = product.features,
            p.images = product.images,
            p.brand = product.brand,
            p.categories = product.categories,
            p.manufacturer = product.manufacturer,
            p.title_embedding = product.title_embedding,
            p.description_embedding = product.desc_embedding
        WITH p, product
        MERGE (s:Store {name: product.store})
        MERGE (p)-[:SOLD_BY]->(s)
        WITH p, product
        MERGE (c:Category {name: product.main_category})
        MERGE (p)-[:IS_OF_CATEGORY]->(c)
        """
        return query

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
                titles, descriptions = (
                    self.model.encode(
                        batch["title"].to_list(),
                        convert_to_numpy=True,
                        batch_size=batch_size // 10,
                        show_progress_bar=True,
                    ).tolist(),
                    self.model.encode(
                        batch["description"].to_list(),
                        convert_to_numpy=True,
                        batch_size=batch_size // 10,
                        show_progress_bar=True,
                    ).tolist(),
                )
                for i, row in batch.iterrows():
                    embeddings = {
                        "title": titles[i],
                        "description": descriptions[i],
                    }
                    session.execute_write(self.create_product, row, embeddings)
        self.driver.close()
