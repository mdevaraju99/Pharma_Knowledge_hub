"""
Check what documents are currently in Neo4j
"""
from utils.neo4j_manager import Neo4jManager

def check_neo4j_documents():
    try:
        neo = Neo4jManager()
        
        # Get all documents
        docs = neo.get_documents()
        
        if not docs:
            print("❌ NO DOCUMENTS FOUND IN NEO4J!")
            print("\nThis is why you're getting 'No relevant information found'")
            print("\nYou need to upload documents through the web interface:")
            print("1. Go to http://localhost:8501")
            print("2. Click '🏢 Multi-Document Knowledge Base' in sidebar")
            print("3. Use the file uploader to select PDFs from test_documents folder")
            print("4. Click 'Process Documents' button")
        else:
            print(f"✅ Found {len(docs)} documents in Neo4j:\n")
            for doc in docs:
                print(f"  📄 {doc.get('filename', 'Unknown')}")
                print(f"     Type: {doc.get('doc_type', 'unknown')}")
                print(f"     Chunks: {doc.get('chunk_count', 0)}")
                print(f"     Uploaded: {doc.get('upload_date', 'N/A')}")
                print()
        
        neo.close()
        
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {e}")
        print("\nMake sure Neo4j is running:")
        print("  podman ps | Select-String 'neo4j'")

if __name__ == "__main__":
    check_neo4j_documents()
