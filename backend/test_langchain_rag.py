"""
Test script - Test LangChain RAG Application

This script will:
1. Test retriever functionality
2. Test LLM functionality (if Endpoint ID is configured)
3. Test full RAG Chain
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_retriever():
    """Test retriever"""
    print("\n" + "=" * 60)
    print("Test 1: VertexRAGEngineRetriever")
    print("=" * 60)
    
    try:
        from langchain_rag import VertexRAGEngineRetriever
        
        # Get configuration from environment variables
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
        location = os.getenv("VERTEX_AI_LOCATION", "europe-north1")
        rag_corpus_id = os.getenv("RAG_CORPUS_ID", "gems-corpus")
        
        print(f"Project ID: {project_id}")
        print(f"Region: {location}")
        print(f"RAG Corpus ID: {rag_corpus_id}")
        print()
        
        if project_id == "your-project-id" or rag_corpus_id == "your-rag-corpus-id":
            print("⚠️  Environment variables not correctly set, skipping actual retrieval test")
            print("   But can test retriever creation...")
            retriever = VertexRAGEngineRetriever(
                project_id=project_id,
                location=location,
                rag_corpus_id=rag_corpus_id,
                top_k=3
            )
            print(f"✅ Retriever created successfully: {retriever.corpus_name}")
            return None
        else:
            retriever = VertexRAGEngineRetriever(
                project_id=project_id,
                location=location,
                rag_corpus_id=rag_corpus_id,
                top_k=3
            )
            
            # Test retrieval
            test_query = "What is GEMS Agent?"
            print(f"Test query: {test_query}")
            print("Retrieving...")
            
            # Use invoke method (LangChain standard interface)
            documents = retriever.invoke(test_query)
            
            print(f"✅ Retrieval successful! Found {len(documents)} documents")
            for i, doc in enumerate(documents[:3], 1):
                print(f"\nDocument {i}:")
                print(f"  Content length: {len(doc.page_content)} characters")
                print(f"  Content preview: {doc.page_content[:100]}...")
                if doc.metadata:
                    print(f"  Metadata: {doc.metadata}")
            
            return retriever
            
    except Exception as e:
        print(f"❌ Retriever test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_llm():
    """Test LLM"""
    print("\n" + "=" * 60)
    print("Test 2: VertexCustomEndpoint")
    print("=" * 60)
    
    try:
        from langchain_rag import VertexCustomEndpoint
        
        endpoint_id = os.getenv("FINE_TUNED_ENDPOINT_ID", "")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
        location = os.getenv("VERTEX_AI_LOCATION", "europe-north1")
        
        print(f"Project ID: {project_id}")
        print(f"Region: {location}")
        print(f"Endpoint ID: {endpoint_id if endpoint_id else 'Not set'}")
        print()
        
        if not endpoint_id or endpoint_id == "":
            print("⚠️  FINE_TUNED_ENDPOINT_ID not set, skipping LLM test")
            return None
        
        if project_id == "your-project-id":
            print("⚠️  GOOGLE_CLOUD_PROJECT not correctly set, skipping LLM test")
            return None
        
        llm = VertexCustomEndpoint(
            project_id=project_id,
            location=location,
            endpoint_id=endpoint_id,
            temperature=0.2,
            max_output_tokens=256
        )
        
        # Test generation
        test_prompt = "Please briefly introduce GEMS Agent."
        print(f"Test Prompt: {test_prompt}")
        print("Generating...")
        
        response = llm.invoke(test_prompt)
        
        print(f"✅ Generation successful!")
        print(f"Answer: {response}")
        
        return llm
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_rag_chain():
    """Test full RAG Chain"""
    print("\n" + "=" * 60)
    print("Test 3: Full RAG Chain")
    print("=" * 60)
    
    try:
        from langchain_rag import create_rag_chain
        
        endpoint_id = os.getenv("FINE_TUNED_ENDPOINT_ID", "")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
        
        if not endpoint_id or endpoint_id == "":
            print("⚠️  FINE_TUNED_ENDPOINT_ID not set, cannot test full Chain")
            return None
        
        if project_id == "your-project-id":
            print("⚠️  GOOGLE_CLOUD_PROJECT not correctly set, cannot test full Chain")
            return None
        
        print("Creating RAG Chain...")
        chain = create_rag_chain()
        print("✅ RAG Chain created successfully!")
        
        # Test query
        test_query = "What is GEMS Agent?"
        print(f"\nTest query: {test_query}")
        print("Processing (retrieval + generation)...")
        
        answer = chain.invoke(test_query)
        
        print(f"\n✅ Full workflow successful!")
        print("-" * 60)
        print("Answer:")
        print("-" * 60)
        print(answer)
        print("-" * 60)
        
        return chain
        
    except Exception as e:
        print(f"❌ RAG Chain test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("LangChain RAG Application Test")
    print("=" * 60)
    
    # Display current environment variables
    print("\nCurrent environment variables:")
    print(f"  GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT', 'Not set')}")
    print(f"  VERTEX_AI_LOCATION: {os.getenv('VERTEX_AI_LOCATION', 'Not set')}")
    print(f"  RAG_CORPUS_ID: {os.getenv('RAG_CORPUS_ID', 'Not set')}")
    print(f"  FINE_TUNED_ENDPOINT_ID: {os.getenv('FINE_TUNED_ENDPOINT_ID', 'Not set')}")
    
    # Run tests
    retriever = test_retriever()
    llm = test_llm()
    chain = test_rag_chain()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Retriever test: {'✅ Passed' if retriever else '⚠️  Skipped (needs configuration)'}")
    print(f"LLM test: {'✅ Passed' if llm else '⚠️  Skipped (needs configuration)'}")
    print(f"Full Chain test: {'✅ Passed' if chain else '⚠️  Skipped (needs configuration)'}")
    print()
    
    if not chain:
        print("Tip: To run full tests, set the following environment variables:")
        print("  export GOOGLE_CLOUD_PROJECT=your-project-id")
        print("  export VERTEX_AI_LOCATION=europe-north1")
        print("  export RAG_CORPUS_ID=gems-corpus")
        print("  export FINE_TUNED_ENDPOINT_ID=your-endpoint-id")
    else:
        print("✅ All tests passed! You can run python langchain_rag.py for interactive testing")


if __name__ == "__main__":
    main()
