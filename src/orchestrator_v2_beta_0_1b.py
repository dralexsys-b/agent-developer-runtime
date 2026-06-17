#!/usr/bin/env python3
"""
Orchestrator v2 Beta-0.1b: Минимальный LLM-вызов через OpenAI-compatible API.
Цель: Замена детерминированной заглушки на реальный вызов llama-server.
"""

import uuid
from typing import TypedDict, Optional, Literal
from pprint import pprint

import requests
from langgraph.graph import StateGraph, START, END

# =============================================================================
# Константы конфигурации
# =============================================================================

LLM_BASE_URL = "http://127.0.0.1:8081"
LLM_CHAT_ENDPOINT = f"{LLM_BASE_URL}/v1/chat/completions"
LLM_TIMEOUT = 120  # seconds

# =============================================================================
# Определения состояний
# =============================================================================

class AgentState(TypedDict):
    request_id: str
    request: str
    response: str
    raw_response: Optional[dict]
    status: Literal["pending", "completed", "failed"]
    error_message: Optional[str]

# =============================================================================
# Изолированная функция побочных эффектов (ADR-006)
# =============================================================================

def execute_llm_call(prompt: str) -> dict:
    """
    Выполняет HTTP POST к llama-server и возвращает структурированный результат.
    Использует безопасный парсинг JSON через .get() с понятными сообщениями об ошибках.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            LLM_CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=LLM_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Безопасный парсинг структуры ответа
        choices = data.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            return {
                "success": False,
                "content": None,
                "raw_response": data,
                "error": "Response missing 'choices' array or array is empty",
                "error_type": "JSONError"
            }
        
        first_choice = choices[0]
        message = first_choice.get("message")
        if not message or not isinstance(message, dict):
            return {
                "success": False,
                "content": None,
                "raw_response": data,
                "error": "First choice missing 'message' object",
                "error_type": "JSONError"
            }
        
        content = message.get("content")
        if content is None:
            return {
                "success": False,
                "content": None,
                "raw_response": data,
                "error": "Message missing 'content' field",
                "error_type": "JSONError"
            }
        
        return {
            "success": True,
            "content": content,
            "raw_response": data,
            "error": None,
            "error_type": None
        }
        
    except requests.exceptions.Timeout as e:
        return {
            "success": False,
            "content": None,
            "raw_response": None,
            "error": f"Timeout after {LLM_TIMEOUT}s: {str(e)}",
            "error_type": "TimeoutError"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "content": None,
            "raw_response": None,
            "error": f"Connection failed: {str(e)}",
            "error_type": "ConnectionError"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "content": None,
            "raw_response": None,
            "error": f"HTTP error: {str(e)}",
            "error_type": "HTTPError"
        }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "raw_response": None,
            "error": f"Unknown error: {str(e)}",
            "error_type": "UnknownError"
        }

# =============================================================================
# Узлы LangGraph
# =============================================================================

def coder_node(state: AgentState) -> dict:
    """
    Вызывает LLM и обновляет state.
    Переход: pending → completed или pending → failed
    """
    print(f"[coder_node] Request ID: {state['request_id']}")
    print(f"[coder_node] Вызов execute_llm_call для: {state['request'][:50]}...")
    result = execute_llm_call(state["request"])
    
    if result["success"]:
        print("[coder_node] ✅ LLM вызов успешен")
        print(f"[coder_node] Переход: pending → completed")
        return {
            **state,
            "response": result["content"],
            "raw_response": result["raw_response"],
            "status": "completed",
            "error_message": None
        }
    else:
        print(f"[coder_node] ❌ LLM вызов неудачен ({result['error_type']}): {result['error']}")
        print(f"[coder_node] Переход: pending → failed")
        return {
            **state,
            "response": "",
            "raw_response": None,
            "status": "failed",
            "error_message": result["error"]
        }

def summary_node(state: AgentState) -> dict:
    """
    Агрегирует финальный результат.
    """
    print(f"[summary_node] Request ID: {state['request_id']}")
    print(f"[summary_node] Финальный статус: {state['status']}")
    
    if state["status"] == "completed":
        print(f"[summary_node] ✅ Запрос успешно выполнен")
        print(f"[summary_node] Ответ (первые 200 символов):")
        print(state["response"][:200])
    else:
        print(f"[summary_node] ❌ Запрос завершился с ошибкой")
        print(f"[summary_node] Ошибка: {state['error_message']}")
    
    return state

# =============================================================================
# Сборка графа
# =============================================================================

def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("coder_node", coder_node)
    builder.add_node("summary_node", summary_node)
    
    builder.add_edge(START, "coder_node")
    builder.add_edge("coder_node", "summary_node")
    builder.add_edge("summary_node", END)
    
    return builder.compile()

# =============================================================================
# Точка входа
# =============================================================================

if __name__ == "__main__":
    print("🚀 Запуск Orchestrator v2 Beta-0.1b (LLM Integration)\n")
    print("=" * 70)
    
    initial_state: AgentState = {
        "request_id": str(uuid.uuid4()),
        "request": "Write a Python function that calculates the factorial of a number",
        "response": "",
        "raw_response": None,
        "status": "pending",
        "error_message": None
    }
    
    print(f"Request ID: {initial_state['request_id']}")
    print(f"Request: {initial_state['request']}")
    print("=" * 70)
    print()
    
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    print("\n" + "=" * 70)
    print("📊 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
    print(f"Request ID: {final_state['request_id']}")
    print(f"Status: {final_state['status']}")
    
    if final_state['error_message']:
        print(f"Error: {final_state['error_message']}")
    
    print("\n🔍 ПОЛНЫЙ FINAL_STATE:")
    pprint(final_state, sort_dicts=False, width=100)
    
    print("=" * 70)
