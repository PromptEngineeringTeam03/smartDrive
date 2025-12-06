"""
DriveSmart AI - Part 2: LangGraph Implementation
Advanced workflow with state management and feedback loops
Save as: langgraph_implementation.py
"""

import os
from pathlib import Path
from typing import TypedDict, List
from dotenv import load_dotenv

# Load environment variables ONCE with override
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path, override=True)

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import chromadb

# ============================================================================
# DEFINE STATE FOR LANGGRAPH
# ============================================================================

class TrafficQueryState(TypedDict):
    """State that flows through the LangGraph"""
    query: str
    jurisdiction: str
    retrieved_docs: List
    analysis: str
    answer: str
    confidence: float
    needs_clarification: bool
    iteration_count: int

# ============================================================================
# INITIALIZE COMPONENTS
# ============================================================================

def initialize_components():
    """Initialize all components with proper error handling"""
    
    # Get API key with strip
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    print(f"✓ API Key loaded: {api_key[:20]}...")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=api_key
    )
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )
    
    # Connect to existing ChromaDB collection
    chroma_client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DB")
    )
    
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="traffic_laws",
        embedding_function=embeddings
    )
    
    print("✓ All components initialized successfully")
    
    return llm, vectorstore

# ============================================================================
# LANGGRAPH NODE FUNCTIONS
# ============================================================================

# Initialize components globally
llm, vectorstore = initialize_components()

def retrieve_documents(state: TrafficQueryState) -> TrafficQueryState:
    """Node 1: Retrieve relevant documents from ChromaDB"""
    
    query = state["query"]
    jurisdiction = state.get("jurisdiction", "Massachusetts")
    
    # Search (without filter for now, as it may cause issues)
    docs = vectorstore.similarity_search(query, k=3)
    
    state["retrieved_docs"] = docs
    
    print(f"[RETRIEVE] Found {len(docs)} documents")
    
    return state

def analyze_confidence(state: TrafficQueryState) -> TrafficQueryState:
    """Node 2: Analyze confidence of retrieved documents"""
    
    docs = state["retrieved_docs"]
    
    # Calculate confidence based on number of docs
    if len(docs) >= 2:
        state["confidence"] = 0.8
        state["needs_clarification"] = False
    elif len(docs) == 1:
        state["confidence"] = 0.5
        state["needs_clarification"] = True
    else:
        state["confidence"] = 0.2
        state["needs_clarification"] = True
    
    print(f"[ANALYZE] Confidence: {state['confidence']:.2f}")
    
    return state

def generate_answer(state: TrafficQueryState) -> TrafficQueryState:
    """Node 3: Generate answer using LLM"""
    
    docs = state["retrieved_docs"]
    query = state["query"]
    
    # Format documents
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Create prompt
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a traffic law expert. Use the following context to answer the question accurately.

Context:
{context}

Question: {question}

Provide a clear, accurate answer with:
1. Direct answer
2. Legal statute reference
3. Penalties (if applicable)
4. Prevention tips

Answer:"""
    )
    
    # Generate answer
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": query})
    
    state["answer"] = answer
    
    print(f"[GENERATE] Answer generated ({len(answer)} chars)")
    
    return state

def request_clarification(state: TrafficQueryState) -> TrafficQueryState:
    """Node 4: Request clarification if confidence is low"""
    
    state["answer"] = f"""I found limited information about your query: "{state['query']}"

Could you please provide more details such as:
- Specific jurisdiction (state/city)?
- Exact scenario or violation type?
- Any additional context?

This will help me provide a more accurate answer."""
    
    print("[CLARIFY] Requesting more information")
    
    return state

def refine_query(state: TrafficQueryState) -> TrafficQueryState:
    """Node 5: Refine query based on feedback (for cycles)"""
    
    iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = iteration
    
    # Expand query with synonyms or related terms
    original_query = state["query"]
    state["query"] = f"{original_query} traffic violation law penalty"
    
    print(f"[REFINE] Iteration {iteration}, expanded query")
    
    return state

# ============================================================================
# ROUTING FUNCTIONS (EDGES)
# ============================================================================

def should_clarify(state: TrafficQueryState) -> str:
    """Decide whether to clarify or generate answer"""
    
    if state["needs_clarification"] and state.get("iteration_count", 0) == 0:
        return "refine"
    elif state["needs_clarification"]:
        return "clarify"
    else:
        return "generate"

def should_iterate(state: TrafficQueryState) -> str:
    """Decide whether to iterate or end"""
    
    iteration = state.get("iteration_count", 0)
    
    if iteration < 2 and state["confidence"] < 0.6:
        return "retrieve"  # Try again with refined query
    else:
        return "end"

# ============================================================================
# BUILD LANGGRAPH
# ============================================================================

def build_traffic_law_graph():
    """Build the LangGraph workflow with feedback loops"""
    
    # Create state graph
    workflow = StateGraph(TrafficQueryState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("analyze", analyze_confidence)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("clarify", request_clarification)
    workflow.add_node("refine", refine_query)
    
    # Set entry point
    workflow.set_entry_point("retrieve")
    
    # Add edges
    workflow.add_edge("retrieve", "analyze")
    
    # Conditional edge from analyze
    workflow.add_conditional_edges(
        "analyze",
        should_clarify,
        {
            "generate": "generate",
            "clarify": "clarify",
            "refine": "refine"
        }
    )
    
    # Feedback loop: refine -> retrieve
    workflow.add_edge("refine", "retrieve")
    
    # Conditional edge from generate
    workflow.add_conditional_edges(
        "generate",
        should_iterate,
        {
            "retrieve": "retrieve",
            "end": END
        }
    )
    
    # End from clarify
    workflow.add_edge("clarify", END)
    
    # Compile with checkpointing
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    print("✓ LangGraph workflow compiled successfully")
    
    return app

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Test the LangGraph workflow"""
    
    print("=" * 70)
    print("DriveSmart AI - LangGraph Implementation")
    print("=" * 70)
    
    # Build graph
    app = build_traffic_law_graph()
    
    # Test queries
    test_queries = [
        {
            "query": "What are the penalties for using a phone while driving?",
            "jurisdiction": "Massachusetts"
        },
        {
            "query": "Can I turn right on red?",
            "jurisdiction": "California"
        },
        {
            "query": "speed limit",  # Intentionally vague to trigger refinement
            "jurisdiction": "Massachusetts"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test Query {i}: {test['query']}")
        print(f"Jurisdiction: {test['jurisdiction']}")
        print(f"{'='*70}\n")
        
        # Create initial state
        initial_state = {
            "query": test["query"],
            "jurisdiction": test["jurisdiction"],
            "retrieved_docs": [],
            "analysis": "",
            "answer": "",
            "confidence": 0.0,
            "needs_clarification": False,
            "iteration_count": 0
        }
        
        # Run graph
        config = {"configurable": {"thread_id": f"test_{i}"}}
        
        for output in app.stream(initial_state, config):
            # Print step output
            node_name = list(output.keys())[0]
            print(f"Step: {node_name}")
        
        # Get final state
        final_state = output[node_name]
        
        print(f"\n{'='*70}")
        print("FINAL ANSWER:")
        print(f"{'='*70}")
        print(f"Confidence: {final_state['confidence']:.2%}")
        print(f"Iterations: {final_state['iteration_count']}")
        print(f"\n{final_state['answer']}\n")

if __name__ == "__main__":
    main()