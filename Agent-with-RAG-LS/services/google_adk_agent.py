import time
from services.google_genai_service import invoke_llm
from services.vector_store_service import query_skills, query_documents
from services.audit_service import add_event_log

def run_google_adk_agent(
    user_query: str,
    conversation_id: str,
    model_name: str = "gemma-4-26b-a4b-it",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    doc_threshold: float = 0.3,
    max_rag_chunks: int = 5,
    custom_endpoint: str = None
) -> dict:
    """
    Simulates Google ADK LlmAgent workflow with skill discovery and tool execution logging.
    """
    agent_type = "Google ADK Agent"
    step_logs = []
    
    # 1. Log Request
    add_event_log(
        conversation_id=conversation_id,
        event_type="User Request",
        invoker="User",
        target=agent_type,
        short_description=f"Google ADK Agent query: {user_query[:60]}...",
        payload={"query": user_query, "agent": agent_type, "model": model_name},
        user_query=user_query,
        agent_type=agent_type,
        model_name=model_name
    )
    
    # 2. RAG Retrieval Step
    t0 = time.time()
    doc_evidence = query_documents(user_query, threshold=doc_threshold, top_k=max_rag_chunks)
    dt0 = round(time.time() - t0, 4)
    
    step_logs.append({
        "component": "ADK RAG Engine",
        "icon": "bi-layers-half",
        "elapsed": f"{dt0}s",
        "log": f"Retrieved {doc_evidence.get('count', 0)} chunks via ADK doc retriever."
    })
    
    # 3. ADK Tool & Skill Search
    t1 = time.time()
    skills = query_skills(user_query, threshold=0.15, top_k=3)
    dt1 = round(time.time() - t1, 4)
    
    step_logs.append({
        "component": "ADK Skill Toolset",
        "icon": "bi-box-seam",
        "elapsed": f"{dt1}s",
        "log": f"Loaded {len(skills)} tools into Google ADK Agent tool registry."
    })
    
    # 4. ADK LLM Invocation
    t2 = time.time()
    rag_context = "\n".join([f"[{item['document']}]: {item['chunk_text']}" for item in doc_evidence.get("results", [])])
    skills_context = "\n".join([f"Tool {s['name']}: {s['description']}" for s in skills])
    
    adk_prompt = (
        f"[Google ADK LlmAgent Context]\n"
        f"Registered Skills/Tools: {skills_context or 'None'}\n"
        f"Evidence Chunks:\n{rag_context or 'None'}\n\n"
        f"User Query: {user_query}"
    )
    
    adk_res = invoke_llm(
        model=model_name,
        prompt=adk_prompt,
        system_instruction="You are a Google ADK LlmAgent. Answer the query thoroughly using available evidence.",
        temperature=temperature,
        max_tokens=max_tokens,
        custom_endpoint=custom_endpoint
    )
    
    add_event_log(
        conversation_id=conversation_id,
        event_type="LLM Call Response",
        invoker=agent_type,
        target=model_name,
        short_description="Google ADK Agent completed response generation",
        payload={"prompt": user_query, "adk_response": adk_res},
        user_query=user_query,
        agent_response=adk_res["text"],
        agent_type=agent_type,
        model_name=model_name,
        elapsed_time=adk_res["elapsed_time"],
        input_tokens=adk_res["input_tokens"],
        output_tokens=adk_res["output_tokens"]
    )
    
    step_logs.append({
        "component": "Google ADK Core",
        "icon": "bi-google",
        "elapsed": f"{adk_res['elapsed_time']}s",
        "log": f"Generated final ADK response. Tokens: in={adk_res['input_tokens']}, out={adk_res['output_tokens']}."
    })
    
    return {
        "conversation_id": conversation_id,
        "user_query": user_query,
        "agent_response": adk_res["text"],
        "agent_type": agent_type,
        "model_name": model_name,
        "step_logs": step_logs,
        "evidence": doc_evidence,
        "skills_matched": skills
    }
