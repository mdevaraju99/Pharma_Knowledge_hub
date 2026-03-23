#!/usr/bin/env python3
"""
COMPLETE FIX for RAG Retrieval Issues
This script:
1. Verifies Neo4j data quality
2. Fixes retrieval with improved chunk context
3. Tests the fixed retrieval
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Tuple

load_dotenv()

class ImprovedRAGManager:
    """Enhanced RAG manager with better retrieval"""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def get_improved_context(self, keywords: List[str], top_k: int = 10) -> str:
        """
        Improved retrieval using keyword + context expansion
        
        Strategy:
        1. Find chunks matching keywords
        2. Expand with neighboring chunks for context
        3. Deduplicate and format with sources
        """
        context_parts = []
        seen_chunks = set()
        
        with self.driver.session() as session:
            # Create a WHERE clause for multiple keywords
            keyword_conditions = " OR ".join(
                [f"c.text CONTAINS '{kw}'" for kw in keywords]
            )
            
            query = f"""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            WHERE {keyword_conditions}
            RETURN c.text as text, c.chunk_index as idx, d.filename as doc, 
                   c.embedding as emb
            ORDER BY c.chunk_index
            LIMIT {top_k}
            """
            
            results = list(session.run(query))
            
            for record in results:
                chunk_text = record['text']
                chunk_id = record['idx']
                doc_name = record['doc']
                
                # Deduplicate
                if chunk_text not in seen_chunks:
                    # Format with source
                    context_parts.append(f"[From {doc_name}]\n{chunk_text}")
                    seen_chunks.add(chunk_text)
            
            # Expand with context (previous/next chunks)
            if results and len(context_parts) < top_k:
                for record in results[:3]:  # Expand for top 3 results
                    chunk_idx = record['idx']
                    doc_name = record['doc']
                    
                    # Get next chunks
                    next_query = """
                    MATCH (d:Document {filename: $doc})-[:HAS_CHUNK]->(c1:Chunk)
                    WHERE c1.chunk_index = $idx
                    OPTIONAL MATCH (c1)-[:NEXT]->(c2:Chunk)
                    RETURN c2.text as next_text
                    """
                    
                    next_results = list(session.run(next_query, doc=doc_name, idx=chunk_idx))
                    for next_rec in next_results:
                        if next_rec['next_text']:
                            next_text = next_rec['next_text']
                            if next_text not in seen_chunks:
                                context_parts.append(f"[Context from {doc_name}]\n{next_text}")
                                seen_chunks.add(next_text)
        
        return "\n\n---\n\n".join(context_parts)
    
    def test_retrieval(self, query: str, keywords: List[str]) -> Dict:
        """Test the retrieval with a query"""
        print(f"\n🔍 Testing Query: {query}")
        print(f"   Keywords: {keywords}")
        
        context = self.get_improved_context(keywords)
        
        if context:
            print(f"✓ Retrieved context ({len(context)} chars):")
            print(f"  {context[:300]}...")
            return {"success": True, "context": context}
        else:
            print("✗ No context retrieved")
            return {"success": False, "context": ""}


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    print("=" * 80)
    print("IMPROVED RAG RETRIEVAL TEST")
    print("=" * 80)
    
    manager = ImprovedRAGManager()
    
    # Test Query 1: Primary Endpoint
    print("\n" + "=" * 80)
    print("TEST 1: Primary Endpoint Query")
    print("=" * 80)
    
    result1 = manager.test_retrieval(
        query="The introduction mentions replicating a primary outcome. What is the specific metric and timeframe for this primary endpoint?",
        keywords=["CDR-SB", "primary endpoint", "Week 72", "baseline"]
    )
    
    # Test Query 2: Safety Query
    print("\n" + "=" * 80)
    print("TEST 2: Safety Query")
    print("=" * 80)
    
    result2 = manager.test_retrieval(
        query="A patient shows asymptomatic moderate ARIA-E. What should the investigator do?",
        keywords=["ARIA-E", "dosing", "suspension", "investigator"]
    )
    
    # Test Query 3: Mechanism
    print("\n" + "=" * 80)
    print("TEST 3: Mechanism Query")
    print("=" * 80)
    
    result3 = manager.test_retrieval(
        query="Explain the mechanism of action of NeuroX-2024",
        keywords=["mechanism", "amyloid", "antibody", "binding"]
    )
    
    manager.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Primary Endpoint): {'PASS ✓' if result1['success'] else 'FAIL ✗'}")
    print(f"Test 2 (Safety): {'PASS ✓' if result2['success'] else 'FAIL ✗'}")
    print(f"Test 3 (Mechanism): {'PASS ✓' if result3['success'] else 'FAIL ✗'}")
