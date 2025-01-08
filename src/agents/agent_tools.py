import json
import ast

from smolagents import tool
from ..database.search import Neo4jSearch


@tool
def recommend_with_query_tool(query: str) -> str:
    """
    Performs Neo4J CQL queries on products database for you. Returns a dictionary representation of the result.
    The table is named 'products'. Its description is as follows:
        Columns:
            Product
            - title
            - description
            - average_rating
            - rating_number
            - price
            - features
            - details
            - image
            - title_embedding
            - description_embedding
        Relationships
            Product -> SOLD_BY -> Store
            Product -> IS_OF_CATEGORY -> Category
    Args:
        query: The search query to be performed to search similar products.
    """
    products = Neo4jSearch.search_products_with_query(query)
    return json.dumps(products)


@tool
def recommend_with_category_tool(category: str) -> str:
    """
    Performs Neo4J CQL queries on products database for you. Returns a dictionary representation of the result.
    The table is named 'products'. Its description is as follows:
        Columns:
            Product
            - description
            - average_rating
            - rating_number
            - price
            - features
            - details
            - image
            - title_embedding
            - description_embedding
        Relationships
            Product -> SOLD_BY -> Store
            Product -> IS_OF_CATEGORY -> Category
    Args:
        category: The search category to be used to find products of same category.
    """
    products = Neo4jSearch.search_products_with_category(
        main_category=category,
    )
    return json.dumps(products)


@tool
def recommend_with_brand_tool(brand: str) -> str:
    """
    Performs Neo4J CQL queries on products database for you. Returns a dictionary representation of the result.
    The table is named 'products'. Its description is as follows:
        Columns:
            Product
            - description
            - average_rating
            - rating_number
            - price
            - features
            - details
            - image
            - title_embedding
            - description_embedding
        Relationships
            Product -> SOLD_BY -> Store
            Product -> IS_OF_CATEGORY -> Category
    Args:
        brand: The search brand name to be used to find products of same brand.
    """
    products = Neo4jSearch.search_products_with_store(brand)
    return json.dumps(products)


@tool
def recommend_with_image_tool(brand: str) -> str:
    """
    Allows you to perform Neo4J CQL queries on products database. Returns a dictionary representation of the result.
    The table is named 'products'. Its description is as follows:
        Columns:
            Product
            - description
            - average_rating
            - rating_number
            - price
            - features
            - details
            - image
            - title_embedding
            - description_embedding
        Relationships
            Product -> SOLD_BY -> Store
            Product -> IS_OF_CATEGORY -> Category
    Args:
        brand: The search brand name to be used to find products of same brand.
    """
    pass
