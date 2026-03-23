"""
Script to ingest documents from test_documents folder into Neo4j
"""
import os
from utils.rag_pipeline import ingest_document

def ingest_test_documents():
    """Ingest all PDFs from test_documents folder"""
    test_docs_folder = "test_documents"
    
    if not os.path.exists(test_docs_folder):
        print(f"❌ Folder '{test_docs_folder}' not found!")
        return
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(test_docs_folder) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{test_docs_folder}' folder!")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files to ingest:")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    
    print("\n🚀 Starting ingestion process...\n")
    
    success_count = 0
    for pdf_file in pdf_files:
        file_path = os.path.join(test_docs_folder, pdf_file)
        print(f"📄 Processing: {pdf_file}")
        
        try:
            with open(file_path, 'rb') as f:
                success, message = ingest_document(f, pdf_file)
                
                if success:
                    print(f"   ✅ {message}\n")
                    success_count += 1
                else:
                    print(f"   ❌ {message}\n")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    print(f"\n{'='*60}")
    print(f"✨ Ingestion complete: {success_count}/{len(pdf_files)} documents processed successfully")
    print(f"{'='*60}\n")
    
    if success_count > 0:
        print("🎯 Next steps:")
        print("1. Start the app: streamlit run app.py")
        print("2. Go to '🏢 Company Knowledge' tab")
        print("3. Ask questions about your documents!")
        print("\n💡 You can also view your graph at: http://localhost:7474")

if __name__ == "__main__":
    ingest_test_documents()
