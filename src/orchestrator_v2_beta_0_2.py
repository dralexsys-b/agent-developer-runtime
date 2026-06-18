#!/usr/bin/env python3
"""
Orchestrator v2 Beta-0.2.r1: Полный цикл Generate → Validate → Retry → Success
Цель: Доказать работоспособность retry-логики с реальным LLM-вызовом.

retry_count: количество уже выполненных retry (повторных попыток после неудачной валидации).
max_retries: максимальное количество retry.

Примечание: FORCE_INVALID_CODE_ON_FIRST_ATTEMPT — временный тестовый механизм
для Beta-0.2.r1. Планируется к удалению или замене тестами в следующей ревизии.
"""

import os
import re
import uuid
import tempfile
import py_compile
from typing import TypedDict, Optional, Literal
from pprint import pprint

import requests
from langgraph.graph import StateGraph, START, END

# =============================================================================
# Константы конфигурации
# =============================================================================

VERSION = "Beta-0.2.r1"

LLM_BASE_URL = "http://127.0.0.1:8081"
LLM_CHAT_ENDPOINT = f"{LLM_BASE_URL}/v1/chat/completions"
LLM_TIMEOUT = 120  # seconds

# ВРЕМЕННЫЙ тестовый механизм для Beta-0.2.r1
# Планируется к удалению или замене тестами в следующей ревизии
FORCE_INVALID_CODE_ON_FIRST_ATTEMPT = True

# =============================================================================
# Определения состояний
# =============================================================================

class ValidationResult(TypedDict):
    success: bool
    error: Optional[str]

class AgentState(TypedDict):
    request_id: str
    user_request: str
    generated_code: Optional[str]
    temp_file_path: Optional[str]
    validation_result: Optional[ValidationResult]
    retry_count: int  # количество уже выполненных retry
    max_retries: int
    status: Literal["pending", "coding", "validating", "retrying", "completed", "failed"]
    error_message: Optional[str]
    raw_response: Optional[dict]
    timings: Optional[dict]
    last_prompt: Optional[str]

# =============================================================================
# Изолированные функции побочных эффектов (ADR-006)
# =============================================================================

def execute_llm_call(prompt: str) -> dict:
    """
    Выполняет HTTP POST к llama-server и возвращает структурированный результат.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.2,
        "stream": False
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
        
        choices = data.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            return {"success": False, "content": None, "raw_response": data, "timings": None, "error": "Response missing 'choices' array or array is empty", "error_type": "JSONError"}
        
        first_choice = choices[0]
        message = first_choice.get("message")
        if not message or not isinstance(message, dict):
            return {"success": False, "content": None, "raw_response": data, "timings": None, "error": "First choice missing 'message' object", "error_type": "JSONError"}
        
        content = message.get("content")
        if content is None:
            return {"success": False, "content": None, "raw_response": data, "timings": None, "error": "Message missing 'content' field", "error_type": "JSONError"}
        
        timings = data.get("timings")
        
        return {"success": True, "content": content, "raw_response": data, "timings": timings, "error": None, "error_type": None}
        
    except requests.exceptions.Timeout as e:
        return {"success": False, "content": None, "raw_response": None, "timings": None, "error": f"Timeout after {LLM_TIMEOUT}s: {str(e)}", "error_type": "TimeoutError"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "content": None, "raw_response": None, "timings": None, "error": f"Connection failed: {str(e)}", "error_type": "ConnectionError"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "content": None, "raw_response": None, "timings": None, "error": f"HTTP error: {str(e)}", "error_type": "HTTPError"}
    except Exception as e:
        return {"success": False, "content": None, "raw_response": None, "timings": None, "error": f"Unknown error: {str(e)}", "error_type": "UnknownError"}

def execute_write_and_compile(temp_path: str, code: str) -> ValidationResult:
    """
    Записывает код во временный файл и проверяет через py_compile.
    """
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        py_compile.compile(temp_path, doraise=True)
        return {"success": True, "error": None}
        
    except py_compile.PyCompileError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_code_from_response(content: str) -> Optional[str]:
    """
    Извлекает Python-код из markdown-блока.
    """
    # Попытка 1: ```python ... ```
    pattern = r'```python\s*(.*?)\s*```'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Попытка 2: ```py ... ```
    pattern = r'```py\s*(.*?)\s*```'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Попытка 3: ``` ... ```
    pattern = r'```\s*(.*?)\s*```'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return None

def maybe_force_invalid_code(new_retry_count: int) -> Optional[str]:
    """
    ВРЕМЕННЫЙ тестовый механизм для Beta-0.2.r1.
    Возвращает заведомо битый код для тестирования retry-логики.
    Планируется к удалению или замене тестами в следующей ревизии.
    """
    if FORCE_INVALID_CODE_ON_FIRST_ATTEMPT and new_retry_count == 0:
        return "def broken_function(\n"
    return None

# =============================================================================
# Узлы LangGraph
# =============================================================================

def coder_node(state: AgentState) -> dict:
    """
    Вызывает LLM и извлекает Python-код из ответа.
    Инкрементирует retry_count только если предыдущая валидация была неудачной.
    """
    print(f"\n[coder_node] Request ID: {state['request_id']}")
    print(f"[coder_node] retry_count={state['retry_count']}")
    
    # Инкремент retry_count на основе validation_result
    is_retry = (
        state["validation_result"] is not None
        and not state["validation_result"]["success"]
    )
    
    new_retry_count = (
        state["retry_count"] + 1
        if is_retry
        else state["retry_count"]
    )
    
    if is_retry:
        status = "retrying"
        print(f"[coder_node] Retry режим, retry_count: {state['retry_count']} → {new_retry_count}")
    else:
        status = "coding"
        print(f"[coder_node] Первый вызов, retry_count=0")
    
    # Использование отдельной функции для принудительного битого кода
    generated_code = maybe_force_invalid_code(new_retry_count)
    if generated_code is not None:
        print(f"[coder_node] ⚠️  FORCE_INVALID_CODE_ON_FIRST_ATTEMPT=True, возвращаю битый код")
        raw_response = None
        timings = None
        last_prompt = None
    else:
        # Формирование промпта (Markdown-safe: конкатенация вместо f""")
        if not is_retry:
            prompt = (
                "Write a Python function that "
                + state['user_request']
                + ".\nReturn ONLY the code inside ```python ... ``` block."
            )
        else:
            prompt = (
                "The previous code had a syntax error. Please fix it.\n\n"
                "User request: " + state['user_request'] + "\n\n"
                "Previous code:\n```python\n"
                + state['generated_code'] + "\n```\n\n"
                "Error message:\n"
                + state['validation_result']['error'] + "\n\n"
                "Return ONLY the fixed code inside ```python ... ``` block."
            )
        
        last_prompt = prompt
        
        print(f"[coder_node] Вызов execute_llm_call...")
        result = execute_llm_call(prompt)
        
        if result["success"]:
            generated_code = extract_code_from_response(result["content"])
            raw_response = result["raw_response"]
            timings = result["timings"]
            
            if generated_code is None:
                print(f"[coder_node] ❌ Код не найден в ответе")
                return {
                    **state,
                    "generated_code": None,
                    "retry_count": new_retry_count,
                    "status": "failed",
                    "error_message": "No code in LLM response",
                    "raw_response": raw_response,
                    "timings": timings,
                    "last_prompt": last_prompt
                }
        else:
            print(f"[coder_node] ❌ LLM вызов неудачен: {result['error']}")
            return {
                **state,
                "generated_code": None,
                "retry_count": new_retry_count,
                "status": "failed",
                "error_message": result["error"],
                "raw_response": result["raw_response"],
                "timings": result["timings"],
                "last_prompt": last_prompt
            }
    
    print(f"[coder_node] ✅ Код сгенерирован (status={status}, retry_count={new_retry_count})")
    print(f"[coder_node] Код (первые 100 символов): {(generated_code or '')[:100]}...")
    
    return {
        **state,
        "generated_code": generated_code,
        "retry_count": new_retry_count,
        "status": status,
        "raw_response": raw_response,
        "timings": timings,
        "last_prompt": last_prompt
    }

def validator_node(state: AgentState) -> dict:
    """
    Сохраняет код во временный файл и проверяет через py_compile.
    """
    print(f"\n[validator_node] Request ID: {state['request_id']}")
    print(f"[validator_node] retry_count={state['retry_count']}")
    
    # Проверка generated_code
    if state["generated_code"] is None:
        print(f"[validator_node] ❌ generated_code is None, невозможно валидировать")
        return {
            **state,
            "validation_result": {"success": False, "error": "generated_code is None"},
            "status": "failed"
        }
    
    # Очистка старого временного файла (если есть)
    if state["temp_file_path"]:
        try:
            os.unlink(state["temp_file_path"])
            print(f"[validator_node] 🗑️  Старый временный файл удалён: {state['temp_file_path']}")
        except OSError as e:
            print(f"[validator_node] ⚠️  Не удалось удалить старый файл: {e}")
    
    # Создание нового временного файла
    fd, temp_path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    print(f"[validator_node] Временный файл: {temp_path}")
    
    # Вызов изолированной функции
    validation_result = execute_write_and_compile(temp_path, state["generated_code"])
    
    if validation_result["success"]:
        print(f"[validator_node] ✅ Компиляция успешна")
    else:
        print(f"[validator_node] ❌ Ошибка компиляции: {validation_result['error']}")
    
    return {
        **state,
        "temp_file_path": temp_path,
        "validation_result": validation_result,
        "status": "validating"
    }


def router_function(state: AgentState) -> str:
    """
    Чистая функция маршрутизации (ADR-004).
    НЕ является узлом графа, только routing function.
    """
    print(f"\n[router_function] Request ID: {state['request_id']}")
    print(f"[router_function] retry_count={state['retry_count']}")
    print(f"[router_function] validation_success={state['validation_result']['success']}")
    
    if state["validation_result"]["success"]:
        print(f"[router_function] → summary_node (успех)")
        return "summary_node"
    
    if state["retry_count"] >= state["max_retries"]:
        print(f"[router_function] → summary_node (retries exhausted: {state['retry_count']}/{state['max_retries']})")
        return "summary_node"
    
    print(f"[router_function] → coder_node (retry)")
    return "coder_node"


def summary_node(state: AgentState) -> dict:
    """
    Финальная агрегация результата + очистка временных файлов.
    """
    print(f"\n[summary_node] Request ID: {state['request_id']}")
    print(f"[summary_node] retry_count={state['retry_count']}")
    
    # Защита от None в validation_result
    validation = state.get("validation_result")
    
    if validation and validation["success"]:
        status = "completed"
        print(f"[summary_node] ✅ Запрос успешно выполнен")
    else:
        status = "failed"
        error_msg = validation["error"] if validation else "validation_result is None"
        print(f"[summary_node] ❌ Запрос завершился с ошибкой")
        print(f"[summary_node] Ошибка: {error_msg}")
    
    # Очистка временного файла
    if state["temp_file_path"]:
        try:
            os.unlink(state["temp_file_path"])
            print(f"[summary_node] 🗑️  Временный файл удалён: {state['temp_file_path']}")
        except OSError as e:
            print(f"[summary_node] ⚠️  Не удалось удалить временный файл: {e}")
    
    return {
        **state,
        "status": status
    }


# =============================================================================
# Сборка графа
# =============================================================================

def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("coder_node", coder_node)
    builder.add_node("validator_node", validator_node)
    builder.add_node("summary_node", summary_node)
    
    builder.add_edge(START, "coder_node")
    builder.add_edge("coder_node", "validator_node")
    
    # Условные рёбра из validator_node через router_function
    builder.add_conditional_edges(
        "validator_node",
        router_function,
        {
            "coder_node": "coder_node",
            "summary_node": "summary_node"
        }
    )
    
    builder.add_edge("summary_node", END)
    
    return builder.compile()


# =============================================================================
# Точка входа
# =============================================================================

if __name__ == "__main__":
    print(f"🚀 Запуск Orchestrator v2 {VERSION} (Generate → Validate → Retry → Success)")
    print("=" * 80)
    print(f"VERSION: {VERSION}")
    print(f"FORCE_INVALID_CODE_ON_FIRST_ATTEMPT: {FORCE_INVALID_CODE_ON_FIRST_ATTEMPT}")
    print("=" * 80)
    
    initial_state: AgentState = {
        "request_id": str(uuid.uuid4()),
        "user_request": "calculates the factorial of a number",
        "generated_code": None,
        "temp_file_path": None,
        "validation_result": None,
        "retry_count": 0,
        "max_retries": 2,
        "status": "pending",
        "error_message": None,
        "raw_response": None,
        "timings": None,
        "last_prompt": None
    }
    
    print(f"\nRequest ID: {initial_state['request_id']}")
    print(f"User Request: {initial_state['user_request']}")
    print("=" * 80)
    
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    # Диагностика: проверка типа возвращаемого состояния
    print(f"\n🔍 Final state type: {type(final_state).__name__}")
    assert isinstance(final_state, dict), (
        f"Expected dict, got {type(final_state).__name__}"
    )
    
    # Проверка наличия ключевых полей
    assert "status" in final_state
    assert "retry_count" in final_state
    assert "request_id" in final_state
    
    print("\n" + "=" * 80)
    print("📊 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
    print(f"VERSION: {VERSION}")
    print(f"Request ID: {final_state['request_id']}")
    print(f"Status: {final_state['status']}")
    print(f"Retry Count: {final_state['retry_count']}")
    
    if final_state['error_message']:
        print(f"Error: {final_state['error_message']}")
    
    if final_state.get('timings'):
        print(f"\n⏱️  Timings:")
        pprint(final_state['timings'], sort_dicts=False, width=100)
    
    print("\n🔍 ПОЛНЫЙ FINAL_STATE:")
    pprint(final_state, sort_dicts=False, width=100)
    
    print("=" * 80)
