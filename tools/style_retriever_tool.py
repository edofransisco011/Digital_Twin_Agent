# digital_twin_agent/tools/style_retriever_tool.py

from qwen_agent.tools.base import BaseTool
from core.vector_store_manager import VectorStoreManager

class StyleRetrieverTool(BaseTool):
    name = 'style_retriever'
    description = "Retrieves examples of the user's personal writing style from a knowledge base."
    parameters = [{'name': 'topic', 'type': 'string', 'description': 'The core topic of the email.', 'required': True}]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        self.vector_store = VectorStoreManager()

    def call(self, params: str, **kwargs) -> str:
        try:
            params_dict = self._parse_params(params)
            topic = params_dict.get('topic')
            if not topic:
                return '{"error": "Topic parameter is missing."}'
            search_results = self.vector_store.search(query_text=topic, n_results=3)
            if not search_results:
                return '{"style_examples": "No relevant style examples found."}'
            return f'{{"style_examples": "{"; ".join(search_results)}"}}'
        except Exception as e:
            return f'{{"error": "An error occurred: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        import json
        try:
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}
