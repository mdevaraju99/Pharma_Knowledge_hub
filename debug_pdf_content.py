#!/usr/bin/env python3
"""Debug script to check PDF content and Neo4j retrieval"""

from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# ==================== STEP 1: Check PDF Content ====================
print("=" * 80)
print("STEP 1: Extracting PDF Content")
print("=" * 80)

pdf_path = "data/complex_clinical_protocol.pdf"
r = PdfReader(pdf_path)
full_text = ""
for page in r.pages:
    full_text += page.extract_text() or ""

print(f"✓ PDF has {len(r.pages)} pages")
print(f"✓ Total extracted text: {len(full_text)} characters")

# Search for key phrases
phrases = ['CDR-SB', 'primary endpoint', 'primary outcome', 'Week 72', 'baseline', 'metric']
print("\n📍 Searching for key phrases:")
found_any = False
for phrase in phrases:
    if phrase.lower() in full_text.lower():
        found_any = True
        idx = full_text.lower().find(phrase.lower())
        context = full_text[max(0, idx-150):min(len(full_text), idx+300)]
        print(f"\n✓ Found '{phrase}':")
        print(f"   Context: ...{context}...")
    else:
        print(f"✗ NOT found: '{phrase}'")

if not found_any:
    print("⚠️ No key phrases found! PDF may not contain the answer.")

# ==================== STEP 2: Check Neo4j Connection ====================
print("\n" + "=" * 80)
print("STEP 2: Checking Neo4j Connection")
print("=" * 80)

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print(f"✓ Connected to Neo4j: {uri}")
except Exception as e:
    print(f"✗ Neo4j Connection Failed: {e}")
    print("  Make sure Neo4j is running!")
    exit(1)

# ==================== STEP 3: Check Data in Neo4j ====================
print("\n" + "=" * 80)
print("STEP 3: Checking Neo4j Data")
print("=" * 80)

with driver.session() as session:
    # Check documents
    result = session.run("MATCH (d:Document) RETURN d.filename as name, count(*) as cnt")
    docs = list(result)
    print(f"📄 Documents in Neo4j: {len(docs)}")
    for doc in docs:
        print(f"   - {doc['name']}")
    
    # Check chunks
    result = session.run("MATCH (c:Chunk) RETURN count(c) as cnt")
    chunk_count = result.single()["cnt"]
    print(f"📦 Total Chunks: {chunk_count}")
    
    if chunk_count == 0:
        print("⚠️ No chunks found! Need to ingest the PDF.")
    else:
        # Check for chunks with key phrases
        print("\n🔍 Searching Neo4j for key phrases:")
        for phrase in ['CDR-SB', 'primary endpoint', 'Week 72']:
            result = session.run(
                "MATCH (c:Chunk) WHERE c.text CONTAINS $phrase RETURN count(c) as cnt",
                phrase=phrase
            )
            count = result.single()["cnt"]
            print(f"   '{phrase}': {count} chunks")

# ==================== STEP 4: Test Vector Search ====================
print("\n" + "=" * 80)
print("STEP 4: Testing Vector Search")
print("=" * 80)

query = "The introduction mentions replicating a primary outcome. What is the specific metric and timeframe for this primary endpoint?"
print(f"Query: {query}\n")

model = SentenceTransformer('all-MiniLM-L6-v2')
query_embedding = model.encode([query])[0].tolist()

with driver.session() as session:
    # Simple keyword search first
    result = session.run(
        """MATCH (c:Chunk) 
           WHERE c.text CONTAINS 'CDR-SB' OR c.text CONTAINS 'primary endpoint'
           RETURN c.text, c.chunk_index LIMIT 5"""
    )
    keyword_results = list(result)
    print(f"📌 Keyword Search Results: {len(keyword_results)} chunks")
    for r in keyword_results:
        print(f"   Chunk #{r['c.chunk_index']}: {r['c.text'][:100]}...")
    
    # Vector similarity search (using cosine distance proxy)
    print("\n📊 Vector Search Results (using Cypher similarity):")
    result = session.run(
        """MATCH (c:Chunk) 
           WHERE c.embedding IS NOT NULL
           RETURN c.text, c.chunk_index,
                  gds.similarity.cosine($query_emb, c.embedding) as sim
           ORDER BY sim DESC LIMIT 5""",
        query_emb=query_embedding
    )
    try:
        vector_results = list(result)
        for i, r in enumerate(vector_results):
            print(f"   #{i+1} (Similarity: {r['sim']:.3f}): {r['c.text'][:80]}...")
    except Exception as e:
        print(f"   ⚠️ Vector search failed: {e}")
        print("   Fallback: Using keyword search only")

driver.close()

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
