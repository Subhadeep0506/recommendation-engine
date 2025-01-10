from typing import Dict, List, Any
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer


class Neo4jSearch:
    driver = None
    model = None

    @classmethod
    def initialize(
        cls,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        database: str = "neo4j",
        password: str = "pillsgap",
    ):
        cls.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
        cls.model = SentenceTransformer(
            "jinaai/jina-embeddings-v3", trust_remote_code=True
        )

    @classmethod
    def generate_embeddings(cls, string: str) -> List[float]:
        return cls.model.encode(string).tolist()

    @classmethod
    def run_query(cls, query: str, top_n: int = 5, **params) -> List[Dict[str, Any]]:
        with cls.driver.session() as session:
            results = session.run(query, **params, top_n=top_n)
            products = []
            for record in results:
                product = {
                    "title": record["title"],
                    "description": record["description"],
                    "product_id": record["product_id"],
                    "average_rating": record["average_rating"],
                    "rating_number": record["rating_number"],
                    "price": record["price"],
                    "features": record["features"],
                    "images": record["images"],
                    "store": record["store"],
                    "brand": record["brand"],
                    "manufacturer": record["manufacturer"],
                    "main_category": record["main_category"],
                    "categories": (
                        record["categories"] if "categories" in record else []
                    ),
                    "similarity": record["avg_sim"] if "avg_sim" in record else 1.0,
                }
                products.append(product)

        return products

    @classmethod
    def search_products_with_query(cls, query: str, top_n: int = 5):
        query_embeddings = cls.generate_embeddings(query)

        query = """
        MATCH (p:Product)-[:SOLD_BY]->(s:Store), (p)-[:IS_OF_CATEGORY]->(c:Category)
        WITH p, s, c, gds.similarity.cosine(p.title_embedding, $query_embeddings) AS title_sim, gds.similarity.cosine(p.description_embedding, $query_embeddings) AS desc_sim
        RETURN p.title AS title, p.description AS description, p.product_id AS product_id, p.average_rating AS average_rating, p.rating_number AS rating_number, p.price AS price, p.features AS features, p.images AS images, p.brand AS brand, p.manufacturer AS manufacturer, s.name AS store, c.name AS main_category, (title_sim + desc_sim) / 2 AS avg_sim
        ORDER BY avg_sim DESC
        LIMIT $top_n
        """

        return cls.run_query(
            query,
            query_embeddings=query_embeddings,
            top_n=top_n,
        )

    @classmethod
    def search_products_with_category(cls, main_category: str, top_n: int = 5):
        query = """
        MATCH (p:Product)-[:SOLD_BY]->(s:Store), (p)-[:IS_OF_CATEGORY]->(c:Category)
        WHERE c.name = $main_category
        WITH p, s, c, rand() AS random
        RETURN p.title AS title, p.description AS description, p.product_id AS product_id, p.average_rating AS average_rating, p.rating_number AS rating_number, p.price AS price, p.features AS features, p.images AS images, p.brand AS brand, p.manufacturer AS manufacturer, s.name AS store, c.name AS main_category
        ORDER BY random
        LIMIT $top_n
        """

        return cls.run_query(
            query,
            main_category=main_category,
            top_n=top_n,
        )

    @classmethod
    def search_products_with_store(
        cls, store: str, top_n: int = 5
    ):
        query = """
        MATCH (p:Product)-[:SOLD_BY]->(s:Store), (p)-[:IS_OF_CATEGORY]->(c:Category)
        WHERE s.name = $store
        WITH p, s, c, rand() AS random
        RETURN p.title AS title, p.description AS description, p.product_id AS product_id, p.average_rating AS average_rating, p.rating_number AS rating_number, p.price AS price, p.features AS features, p.images AS images, p.brand AS brand, p.manufacturer AS manufacturer, s.name AS store, c.name AS main_category
        ORDER BY random
        LIMIT $top_n
        """

        return cls.run_query(
            query,
            store=store,
            top_n=top_n,
        )
