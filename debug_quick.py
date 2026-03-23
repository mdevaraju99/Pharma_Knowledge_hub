#!/usr/bin/env python3
"""Quick debug script without heavy ML dependencies"""

from PyPDF2 import PdfReader
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("STEP 1: Extracting PDF Content")
print("=" * 80)

pdf_path = "data/complex_clinical_protocol.pdf"
r = PdfReader(pdf_path)
full_text = ""
page_texts = []

for i, page in enumerate(r.pages):
    text = page.extract_text() or ""
    page_texts.append(text)
    full_text += text

print(f"✓ PDF has {len(r.pages)} pages, {len(full_text)} total characters")

# Search for key phrases
phrases = ['CDR-SB', 'primary endpoint', 'primary outcome', 'Week 72', 'baseline', 'metric', 'change from baseline']
print("\n📍 Searching for key phrases in PDF:")
found_phrases = {}

for phrase in phrases:
    count = full_text.lower().count(phrase.lower())
    found_phrases[phrase] = count
    if count > 0:
        print(f"✓ '{phrase}': Found {count} times")
        # Show first occurrence
        idx = full_text.lower().find(phrase.lower())
        context = full_text[max(0, idx-100):min(len(full_text), idx+250)]
        print(f"  Context: ...{context[:200]}...\n")
    else:
        print(f"✗ '{phrase}': NOT found")

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
    print("  Make sure Neo4j is running with: podman start neo4j-pharma")
    exit(1)

print("\n" + "=" * 80)
print("STEP 3: Checking Neo4j Data")
print("=" * 80)

with driver.session() as session:
    # Check documents
    result = session.run("MATCH (d:Document) RETURN d.filename as name, d.upload_date, count(*) as cnt")
    docs = list(result)
    print(f"📄 Documents in Neo4j: {len(docs)}")
    for doc in docs:
        print(f"   - {doc['name']} (uploaded: {doc['d.upload_date']})")
    
    # Check chunks
    result = session.run("MATCH (c:Chunk) RETURN count(c) as cnt")
    chunk_count = result.single()["cnt"]
    print(f"📦 Total Chunks: {chunk_count}")
    
    if chunk_count == 0:
        print("\n⚠️ NO CHUNKS FOUND IN NEO4J!")
        print("   You need to ingest the PDF first.")
        print("   This is the ROOT CAUSE of 'No relevant information found'")
    else:
        # Check for chunks with key phrases
        print("\n🔍 Searching Neo4j Chunks for key phrases:")
        for phrase in phrases:
            result = session.run(
                "MATCH (c:Chunk) WHERE c.text CONTAINS $phrase RETURN count(c) as cnt",
                phrase=phrase
            )
            count = result.single()["cnt"]
            if count > 0:
                print(f"   ✓ '{phrase}': {count} chunks")
            else:
                print(f"   ✗ '{phrase}': 0 chunks")
        
        # Show sample chunks
        print("\n📝 Sample Chunks from Neo4j:")
        result = session.run(
            "MATCH (c:Chunk) RETURN c.text LIMIT 3"
        )
        for i, record in enumerate(result, 1):
            text = record['c.text']
            print(f"   [{i}] {text[:100]}...")

driver.close()

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

if chunk_count == 0:
    print("""
⚠️ PROBLEM: No chunks in Neo4j database!

ROOT CAUSES:
1. PDF was never ingested to Neo4j
2. Or ingestion failed silently
3. Or Neo4j data was cleared

SOLUTION:
1. Go to app.py and run: streamlit run app.py
2. Open Chatbot tab
3. Go to "Company Knowledge" tab  
4. Upload 'data/complex_clinical_protocol.pdf'
5. Wait for "Document processed and graph created!" message

Then try your question again!
""")
elif not any(found_phrases.values()):
    print("""
⚠️ PROBLEM: PDF doesn't contain key clinical trial information!

The PDF may be:
1. A different document than expected
2. Generated incorrectly
3. Scanned as images (not extractable text)

SOLUTION:
1. Verify the PDF has the answer
2. Try opening it manually to check content
3. Generate a new test PDF with correct clinical trial data
""")
else:
    print("""
⚠️ PROBLEM: Data exists but retrieval is failing!

ROOT CAUSES:
1. Vector embeddings not properly generated
2. Retrieval similarity threshold too high
3. Chunks too small to capture full answer
4. Query phrasing doesn't match document

SOLUTION: Run the fixed ingestion and retrieval scripts
""")
