import os

from smolagents.models import LiteLLMModel

from ..database.search import Neo4jSearch
from ..agents.agents import RecSysAgent
from ..utils.utils import capture_mode_brand, capture_mode_category, save_results, read_products_from_file


class Orchestrator:
    def __init__(self, config: dict = None):
        Neo4jSearch.initialize(database="products")
        os.environ["AZURE_API_VERSION"] = ""
        self.model = LiteLLMModel(
            model_id="",
            api_base="",
            api_key="",
        )
        self.recsysagent = RecSysAgent(model=self.model)
        self.initialize_agents()

    def initialize_agents(self):
        self.query_search_agent = self.recsysagent.create_query_search_agent()
        self.category_search_agent = self.recsysagent.create_category_search_agent()
        self.brand_search_agent = self.recsysagent.create_brand_search_agent()

    def recommend_products_using_query(self, query: str, top_n: int = 5):
        products_from_query = self.query_search_agent.run(
            query,
        )
        file_name = save_results(
            result=products_from_query.replace("\n", " "), type="query"
        )
        return file_name

    def recommend_products_of_category(self, file_name: str, top_n: int = 5):
        products = read_products_from_file(file_name)
        category = capture_mode_category(products=products)
        products_from_category = self.category_search_agent.run(category)
        file_name = save_results(
            result=products_from_category.replace("\n", " "), type="category"
        )
        return file_name
    
    def recommend_products_of_brand(self, file_name: str, top_n: int = 5):
        products = read_products_from_file(file_name)
        brand = capture_mode_brand(products=products)
        products_from_brand = self.brand_search_agent.run(brand)
        file_name = save_results(
            result=products_from_brand.replace("\n", " "), type="brand"
        )
        return file_name
