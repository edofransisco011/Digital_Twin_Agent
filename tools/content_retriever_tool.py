# digital_twin_agent/tools/content_retriever_tool.py

from qwen_agent.tools.base import BaseTool
from core.vector_store_manager import VectorStoreManager

class ContentRetrieverTool(BaseTool):
    """
    A synchronous tool to retrieve the content of past emails from a vector database.
    This tool is used to answer questions about specific information
    contained within the user's email history.
    """
    name = 'email_content_retriever'
    description = (
        "Searches and retrieves the content of past emails based on a query. "
        "Use this tool to find information or answer specific questions about what was "
        "said in previous email conversations."
    )
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': 'The user\'s original, verbatim question about the email content.', # The LLM should pass the user's raw question.
        'required': True
    }]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        self.vector_store = VectorStoreManager(collection_name="email_content_collection") # Use a dedicated collection
        print("Content Retriever tool initialized successfully.")

    def call(self, params: str, **kwargs) -> str:
        """
        Searches the vector store for email content matching the user's query.
        This is now a synchronous method.
        """
        try:
            params_dict = self._parse_params(params)
            query = params_dict.get('query')
            if not query:
                return '{"error": "Query parameter is missing."}'

            # IMPROVEMENT: We now use the user's raw query for the search, which is often more robust.
            print(f"Tool Action: Searching for content semantically similar to: '{query}'")
            search_results = self.vector_store.search(query_text=query, n_results=4) # Retrieve more results for context

            if not search_results:
                return '{"retrieved_content": "No relevant information found in your emails matching that query."}'

            # Join the results into a single context block for the LLM
            formatted_results = "\n\n---\n\n".join(search_results)
            # Use json.dumps to ensure the string is properly escaped for the final JSON structure
            import json
            return json.dumps({"retrieved_content": formatted_results})

        except Exception as e:
            print(f"[Error in ContentRetrieverTool]: {e}")
            return f'{{"error": "An error occurred while retrieving email content: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        """A simple helper to parse the string-based parameters."""
        import json
        try:
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}
