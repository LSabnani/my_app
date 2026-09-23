import json
import time
import importlib.util
from pathlib import Path

from services.vector_store_service import query_skills, query_documents
from services.google_genai_service import invoke_llm
from services.audit_service import add_event_log
from config import SKILLS_DIR

def execute_procedural_tool(tool_name: str, args: dict) -> dict:
    """Dynamically executes procedural tools from the skills/ folder scripts."""
    try:
        if "time" in tool_name or "weather" in tool_name or "env_tools" in tool_name:
            script_path = SKILLS_DIR / "time-weather-skill" / "scripts" / "env_tools.py"
            spec = importlib.util.spec_from_file_location("env_tools", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            city = args.get("city") or args.get("keyword") or "Tokyo"
            return mod.get_time_and_weather(city)
            
        elif "person" in tool_name or "registry" in tool_name:
            script_path = SKILLS_DIR / "person-information-skill" / "scripts" / "person_search.py"
            spec = importlib.util.spec_from_file_location("person_search", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            keyword = args.get("keyword") or args.get("name") or ""
            field = args.get("field", "all")
            return mod.query_person_registry(keyword, field)
            
        elif "stock" in tool_name:
            script_path = SKILLS_DIR / "stock-market-skill" / "scripts" / "stock_search.py"
            spec = importlib.util.spec_from_file_location("stock_search", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            action = args.get("action", "top_gainers")
            ticker = args.get("ticker", "")
            return mod.query_stock_market(action, ticker)
            
        elif "doc" in tool_name or "document" in tool_name:
            script_path = SKILLS_DIR / "doc-search-skill" / "scripts" / "doc_search.py"
            spec = importlib.util.spec_from_file_location("doc_search", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            query = args.get("query") or args.get("keyword") or ""
            top_k = int(args.get("top_k", 5))
            threshold = float(args.get("doc_threshold", 0.3))
            return mod.query_document_store(query, top_k, threshold)
            
        return {"error": f"Tool '{tool_name}' not recognized."}
    except Exception as e:
        return {"error": f"Failed to execute tool '{tool_name}': {str(e)}"}

def run_custom_agent(
    user_query: str,
    conversation_id: str,
    model_name: str = "gemma-4-26b-a4b-it",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    max_turns: int = 3,
    skill_selector_mode: str = "Vector Store Selects",
    skill_threshold: float = 0.2,
    doc_threshold: float = 0.3,
    max_rag_chunks: int = 5,
    custom_endpoint: str = None
) -> dict:
    """
    Executes the Custom Agent workflow according to SPECIFICATIONS.md.
    """
    step_logs = []
    agent_type = "Custom Agent"
    
    # 1. Log Initial User Request
    add_event_log(
        conversation_id=conversation_id,
        event_type="User Request",
        invoker="User",
        target=agent_type,
        short_description=f"Received query: {user_query[:60]}...",
        payload={"query": user_query, "model": model_name, "max_turns": max_turns},
        user_query=user_query,
        agent_type=agent_type,
        model_name=model_name
    )
    
    # 2. Skill Selection
    start_skill_t = time.time()
    matched_skills = []
    
    if skill_selector_mode == "Vector Store Selects":
        matched_skills = query_skills(user_query, threshold=skill_threshold, top_k=5)
    elif skill_selector_mode == "LLM Selects":
        matched_skills = query_skills(user_query, threshold=0.01, top_k=5)
    else:
        # Specific skill selected from dropdown
        all_s = query_skills(user_query, threshold=0.0, top_k=10)
        matched_skills = [s for s in all_s if s["id"] == skill_selector_mode or s["name"] == skill_selector_mode]
        if not matched_skills and all_s:
            matched_skills = [all_s[0]]
            
    skill_elapsed = round(time.time() - start_skill_t, 4)
    
    add_event_log(
        conversation_id=conversation_id,
        event_type="Skill Search",
        invoker=agent_type,
        target="Skills Vector Store",
        short_description=f"Skill search found {len(matched_skills)} matches (threshold={skill_threshold})",
        payload={"query": user_query, "matched_skills": matched_skills},
        user_query=user_query,
        agent_type=agent_type,
        model_name=model_name,
        elapsed_time=skill_elapsed
    )
    
    step_logs.append({
        "component": "Skill Search",
        "icon": "bi-lightning-charge",
        "elapsed": f"{skill_elapsed}s",
        "log": f"Queried skills store. Matched {len(matched_skills)} skills: {[s['name'] for s in matched_skills]}"
    })
    
    # 3. Document Search (RAG Evidence Collection)
    start_doc_t = time.time()
    doc_evidence = query_documents(user_query, threshold=doc_threshold, top_k=max_rag_chunks)
    doc_elapsed = round(time.time() - start_doc_t, 4)
    
    add_event_log(
        conversation_id=conversation_id,
        event_type="Document Search",
        invoker=agent_type,
        target="Document Vector Store",
        short_description=f"Retrieved {doc_evidence.get('count', 0)} document chunks",
        payload=doc_evidence,
        user_query=user_query,
        agent_type=agent_type,
        model_name=model_name,
        elapsed_time=doc_elapsed
    )
    
    step_logs.append({
        "component": "RAG Vector Store",
        "icon": "bi-database-check",
        "elapsed": f"{doc_elapsed}s",
        "log": f"Retrieved {doc_evidence.get('count', 0)} evidence chunks exceeding threshold {doc_threshold}."
    })
    
    # 4. Multi-Turn Planning & Tool Execution Loop
    turns_count = 0
    procedural_context = []
    
    # If skills were found, prompt LLM to determine tool call
    if matched_skills:
        top_2_skills = matched_skills[:2]
        skills_text = "\n\n".join([f"Skill: {s['name']}\n{s['content']}" for s in top_2_skills])
        
        system_plan_prompt = (
            "You are an AI Agent decision orchestrator. Given the user query and available tools/skills, "
            "determine if a tool should be executed. Respond strictly in valid JSON format:\n"
            "If a tool is needed:\n"
            "{\n"
            '  "tool": "<tool_name>",\n'
            '  "arguments": {"keyword": "val", "city": "val", "action": "val", "field": "val"}\n'
            "}\n"
            "If no tool is needed, respond with:\n"
            '{"tool": "none", "arguments": {}}\n\n'
            f"Available Skills:\n{skills_text}"
        )
        
        while turns_count < max_turns:
            turns_count += 1
            llm_plan_res = invoke_llm(
                model=model_name,
                prompt=user_query,
                system_instruction=system_plan_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                custom_endpoint=custom_endpoint
            )
            
            add_event_log(
                conversation_id=conversation_id,
                event_type="LLM Tool Plan Call",
                invoker=agent_type,
                target=model_name,
                short_description=f"Turn {turns_count}: Evaluated tool execution plan",
                payload={"prompt": user_query, "response": llm_plan_res},
                user_query=user_query,
                agent_type=agent_type,
                model_name=model_name,
                elapsed_time=llm_plan_res["elapsed_time"],
                input_tokens=llm_plan_res["input_tokens"],
                output_tokens=llm_plan_res["output_tokens"]
            )
            
            # Parse JSON tool plan
            tool_name = "none"
            tool_args = {}
            try:
                raw_json = llm_plan_res["text"].strip()
                if "```json" in raw_json:
                    raw_json = raw_json.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_json:
                    raw_json = raw_json.split("```")[1].split("```")[0].strip()
                elif "{" in raw_json and "}" in raw_json:
                    raw_json = raw_json[raw_json.find("{"):raw_json.rfind("}")+1]
                plan_data = json.loads(raw_json)
                tool_name = plan_data.get("tool", "none")
                tool_args = plan_data.get("arguments", {})
            except Exception:
                tool_name = matched_skills[0]["id"]
                tool_args = {}

            # Fallback argument extraction if tool was selected without arguments
            if tool_name != "none" and not tool_args:
                # Extract city from user query for time/weather tool
                words = [w.strip("?,.!") for w in user_query.split()]
                # Common city extraction heuristic
                city = words[-1] if words else "Tokyo"
                tool_args = {"city": city, "keyword": user_query}
                
            if tool_name == "none" or not tool_name:
                break
                
            # Execute Procedural Tool
            t_start = time.time()
            tool_res = execute_procedural_tool(tool_name, tool_args)
            t_elapsed = round(time.time() - t_start, 4)
            
            add_event_log(
                conversation_id=conversation_id,
                event_type="Tool Execution",
                invoker=agent_type,
                target=tool_name,
                short_description=f"Executed tool '{tool_name}' with args {tool_args}",
                payload={"tool": tool_name, "arguments": tool_args, "result": tool_res},
                user_query=user_query,
                agent_type=agent_type,
                model_name=model_name,
                elapsed_time=t_elapsed
            )
            
            step_logs.append({
                "component": "Tools",
                "icon": "bi-gear-wide-connected",
                "elapsed": f"{t_elapsed}s",
                "log": f"Executed tool '{tool_name}' ({tool_args}). Result count: {len(tool_res.get('results', [])) if isinstance(tool_res.get('results'), list) else 'OK'}"
            })
            
            procedural_context.append(f"Tool '{tool_name}' output: {json.dumps(tool_res)}")
            break # Single loop execution per turns budget
            
    # 5. Final LLM Response Synthesis Call
    start_final_t = time.time()
    
    rag_context_str = "\n".join([f"Document Chunk ({item['document']}): {item['chunk_text']}" for item in doc_evidence.get("results", [])])
    tool_context_str = "\n".join(procedural_context)
    
    if procedural_context:
        final_system_prompt = (
            "You are an expert AI Assistant with access to live tools and RAG document context. "
            "Synthesize a clear, helpful, and accurate response for the user query based on the tool results provided.\n"
            "IMPORTANT RULES:\n"
            "- Read exact values from the tool results (such as 'current_local_time', 'time_in_city', 'temperature_celsius', etc.).\n"
            "- Always state the exact dates, times, prices, or names from the tool output.\n"
            "- NEVER output bracketed placeholder text or internal reasoning loops.\n\n"
            f"--- RAG Document Evidence ---\n{rag_context_str or 'No direct document chunks matched.'}\n\n"
            f"--- Tool & Skill Results ---\n{tool_context_str}"
        )
    else:
        final_system_prompt = (
            "You are a helpful AI Assistant. Answer the user query clearly and accurately.\n"
            f"--- RAG Document Evidence ---\n{rag_context_str or 'No document evidence matched.'}"
        )
    
    final_llm_res = invoke_llm(
        model=model_name,
        prompt=user_query,
        system_instruction=final_system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        custom_endpoint=custom_endpoint
    )
    
    add_event_log(
        conversation_id=conversation_id,
        event_type="LLM Call Response",
        invoker=agent_type,
        target=model_name,
        short_description="Synthesized final agent answer",
        payload={"prompt": user_query, "final_response": final_llm_res},
        user_query=user_query,
        agent_response=final_llm_res["text"],
        agent_type=agent_type,
        model_name=model_name,
        elapsed_time=final_llm_res["elapsed_time"],
        input_tokens=final_llm_res["input_tokens"],
        output_tokens=final_llm_res["output_tokens"]
    )
    
    step_logs.append({
        "component": "Agent",
        "icon": "bi-robot",
        "elapsed": f"{final_llm_res['elapsed_time']}s",
        "log": f"Synthesized final response using model '{model_name}'. Tokens: in={final_llm_res['input_tokens']}, out={final_llm_res['output_tokens']}."
    })
    
    return {
        "conversation_id": conversation_id,
        "user_query": user_query,
        "agent_response": final_llm_res["text"],
        "agent_type": agent_type,
        "model_name": model_name,
        "step_logs": step_logs,
        "evidence": doc_evidence,
        "skills_matched": matched_skills
    }
