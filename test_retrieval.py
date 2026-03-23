"""
Test RAG retrieval to diagnose the issue
"""
from utils.rag_pipeline import get_rag_context

def test_retrieval():
    print("Testing RAG retrieval...\n")
    
    test_queries = [
        "primary endpoint",
        "clinical trial results",
        "mechanism of action",
        "Alzheimer's disease treatment",
        "efficacy outcomes"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 60)
        
        try:
            context = get_rag_context(query, top_k=5)
            
            if context and len(context.strip()) > 0:
                print(f"✅ Found {len(context)} characters of context")
                print(f"Preview: {context[:200]}...")
            else:
                print("❌ No context retrieved!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n")

if __name__ == "__main__":
    test_retrieval()
