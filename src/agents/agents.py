from smolagents import (
    ToolCallingAgent,
    ManagedAgent,
)
from smolagents import Model
from .agent_tools import (
    recommend_with_query_tool,
    recommend_with_category_tool,
    recommend_with_brand_tool,
)
from ..config import Config as cfg


class RecSysAgent:
    def __init__(self, model: Model):
        self.model = model

    def create_query_search_agent(self):
        query_search_agent = ToolCallingAgent(
            tools=[recommend_with_query_tool],
            model=self.model,
            max_iterations=2,
            system_prompt=cfg.QUERY_SYSTEM_PROMPT,
        )
        return query_search_agent

    def create_category_search_agent(self):
        category_search_agent = ToolCallingAgent(
            tools=[recommend_with_category_tool],
            model=self.model,
            max_iterations=2,
            system_prompt=cfg.CATEGORY_SYSTEM_PROMPT,
        )
        return category_search_agent

    def create_brand_search_agent(self):
        category_search_agent = ToolCallingAgent(
            tools=[recommend_with_brand_tool],
            model=self.model,
            max_iterations=2,
            system_prompt=cfg.BRAND_SYSTEM_PROMPT,
        )
        return category_search_agent

    def create_managed_query_agent(self):
        managed_query_agent = ManagedAgent(
            agent=[],
            name="",
            description="",
        )

        return managed_query_agent

    def create_image_search_agent(self):
        pass
