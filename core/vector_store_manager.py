# digital_twin_agent/core/vector_store_manager.py

import chromadb
import os

class VectorStoreManager:
    """
    Manages all interactions with the ChromaDB vector store.
    """
    def __init__(self, collection_name="writing_style_collection"):
        """
        Initializes the ChromaDB client and gets or creates a collection.
        
        Args:
            collection_name (str): The name of the collection to store the writing style vectors.
        """
        # Define the path for the persistent ChromaDB storage
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chroma_db')
        
        # Initialize the persistent client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create the collection. A collection is like a table in a traditional database.
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        print(f"Vector store manager initialized. Using collection: '{collection_name}'")
        print(f"Database is persistently stored at: {db_path}")

    def add_documents(self, documents: list[str], ids: list[str]):
        """
        Adds documents to the vector store collection.
        ChromaDB will automatically handle tokenization and embedding.

        Args:
            documents (list[str]): A list of text chunks to add (e.g., email bodies).
            ids (list[str]): A list of unique identifiers for each document.
        """
        if not documents:
            print("No documents to add.")
            return

        print(f"Adding {len(documents)} documents to the vector store...")
        try:
            self.collection.add(
                documents=documents,
                ids=ids
            )
            print("Successfully added documents to the collection.")
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")

    def search(self, query_text: str, n_results: int = 5) -> list:
        """
        Searches the collection for documents similar to the query text.

        Args:
            query_text (str): The text to search for.
            n_results (int): The number of similar documents to return.

        Returns:
            list: A list of the most similar documents found.
        """
        print(f"Searching for text similar to: '{query_text[:50]}...'")
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            # The actual documents are in a nested list
            return results['documents'][0] if results and results['documents'] else []
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []

# --- Self-testing block ---
if __name__ == '__main__':
    # This test demonstrates how to use the manager.
    print("Running VectorStoreManager self-test...")
    
    # 1. Initialize the manager
    vector_store = VectorStoreManager()
    
    # 2. Add some sample documents
    sample_docs = [
        "This is how I typically start my professional emails, with a clear and direct opening.",
        "For casual conversations, I tend to use more emojis and exclamation points!",
        "When discussing technical topics, I prefer to use bullet points to structure my arguments.",
        "My sign-off for formal letters is always 'Sincerely'.",
        "I often end messages to friends with 'Talk soon!'."
    ]
    sample_ids = [f"doc_{i}" for i in range(len(sample_docs))]
    
    # This will create a 'chroma_db' directory in your project root.
    vector_store.add_documents(documents=sample_docs, ids=sample_ids)
    
    # 3. Perform a search
    search_query = "how do I write a formal letter?"
    search_results = vector_store.search(query_text=search_query, n_results=2)
    
    # 4. Print results
    print("\n--- Search Results ---")
    if search_results:
        for i, doc in enumerate(search_results):
            print(f"{i+1}. {doc}")
    else:
        print("No results found.")
