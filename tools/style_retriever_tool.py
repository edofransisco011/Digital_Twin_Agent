from qwen_agent.tools.base import BaseTool
from core.vector_store_manager import VectorStoreManager

class StyleRetrieverTool(BaseTool):
    """
    A tool to retrieve writing style examples from a vector database.
    """
    name = 'style_retriever'
    description = (
        "Retrieves examples of the user's personal writing style from a knowledge base. "
        "Use this tool before drafting an email to get style examples. "
        "The input should be the core topic or a short summary of the email to be drafted."
    )
    parameters = [{
        'name': 'topic',
        'type': 'string',
        'description': 'The core topic of the email to be drafted.',
        'required': True
    }]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        self.vector_store = VectorStoreManager()
        print("Style Retriever tool initialized successfully.")

    def call(self, params: str, **kwargs) -> str:
        """
        Searches the vector store for writing samples similar to the topic.
        """
        try:
            params_dict = self._parse_params(params)
            topic = params_dict.get('topic')
            if not topic:
                return '{"error": "Topic parameter is missing."}'

            # Search the vector store for relevant writing samples
            search_results = self.vector_store.search(query_text=topic, n_results=3)

            if not search_results:
                return '{"style_examples": "No relevant style examples found."}'

            # Format the results into a single string for the agent
            formatted_examples = "; ".join(search_results)
            return f'{{"style_examples": "{formatted_examples}"}}'

        except Exception as e:
            print(f"[Error in StyleRetrieverTool]: {e}")
            return f'{{"error": "An error occurred while retrieving style examples: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        """A simple helper to parse the string-based parameters."""
        try:
            import json
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}