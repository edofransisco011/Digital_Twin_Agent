# digital_twin_agent/run_ingestion.py

from tools.email_tools import GmailTool

def main():
    """
    Main function to run the one-time email ingestion process.
    """
    print("--- Starting Email Ingestion for Digital Twin Persona ---")
    print("This script will read your sent emails and store them in a local vector database to learn your writing style.")
    print("This is a one-time setup process.")
    
    try:
        # Initialize the GmailTool, which contains the ingestion logic
        gmail_tool = GmailTool()
        
        # Call the ingestion method
        # You can change the number to ingest more or fewer emails (e.g., max_emails=100)
        gmail_tool.ingest_sent_emails(max_emails=50)
        
        print("\n--- Ingestion Process Completed Successfully ---")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure your `credentials.json` and `token.pickle` files are correctly set up.")

if __name__ == '__main__':
    main()

