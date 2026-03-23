"""
Diagnose Neo4j vector index and chunk embeddings
"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def diagnose_neo4j():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            print("=== NEO4J DIAGNOSIS ===\n")
            
            # 1. Check vector index
            print("1. Checking vector indexes...")
            result = session.run("SHOW INDEXES")
            indexes = [record.data() for record in result]
            
            vector_indexes = [idx for idx in indexes if idx.get('type') == 'VECTOR']
            if vector_indexes:
                print(f"✅ Found {len(vector_indexes)} vector index(es):")
                for idx in vector_indexes:
                    print(f"   - {idx.get('name')}: {idx.get('state')}")
            else:
                print("❌ NO VECTOR INDEX FOUND!")
                print("   This is the problem! Creating vector index...")
                try:
                    session.run("""
                        CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
                        FOR (c:Chunk) ON (c.embedding)
                        OPTIONS {indexConfig: {
                         `vector.dimensions`: 384,
                         `vector.similarity_function`: 'cosine'
                        }}
                    """)
                    print("   ✅ Vector index created!")
                except Exception as e:
                    print(f"   ❌ Failed to create index: {e}")
            
            print()
            
            # 2. Check chunks
            print("2. Checking chunks...")
            result = session.run("""
                MATCH (c:Chunk)
                RETURN count(c) as total_chunks,
                       count(c.embedding) as chunks_with_embeddings
            """)
            stats = result.single()
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Chunks with embeddings: {stats['chunks_with_embeddings']}")
            
            if stats['chunks_with_embeddings'] == 0:
                print("   ❌ NO EMBEDDINGS FOUND!")
                print("   Documents need to be re-uploaded with embeddings")
            elif stats['chunks_with_embeddings'] < stats['total_chunks']:
                print(f"   ⚠️ {stats['total_chunks'] - stats['chunks_with_embeddings']} chunks missing embeddings")
            else:
                print("   ✅ All chunks have embeddings")
            
            print()
            
            # 3. Sample chunk data
            print("3. Sample chunk data...")
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                RETURN d.filename as doc, c.text as text, 
                       size(c.embedding) as embedding_size
                LIMIT 3
            """)
            for record in result:
                print(f"   Doc: {record['doc']}")
                print(f"   Text preview: {record['text'][:80]}...")
                print(f"   Embedding dims: {record['embedding_size']}")
                print()
            
            print()
            
            # 4. Test vector search
            print("4. Testing vector search...")
            try:
                # Create a dummy query embedding (384 dimensions, all 0.1)
                dummy_embedding = [0.1] * 384
                
                result = session.run("""
                    CALL db.index.vector.queryNodes('pharma_vector_index', 3, $query_embedding)
                    YIELD node, score
                    RETURN node.text as text, score
                    LIMIT 3
                """, query_embedding=dummy_embedding)
                
                results = [record.data() for record in result]
                if results:
                    print(f"   ✅ Vector search is working! Found {len(results)} results")
                    for r in results:
                        print(f"      Score: {r['score']:.4f}, Text: {r['text'][:60]}...")
                else:
                    print("   ❌ Vector search returned no results")
                    
            except Exception as e:
                print(f"   ❌ Vector search failed: {e}")
                print("   Index may need time to populate or rebuild")
            
    finally:
        driver.close()

if __name__ == "__main__":
    diagnose_neo4j()
