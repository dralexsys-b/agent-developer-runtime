#!/usr/bin/env python3
"""
Orchestrator v2 Beta-0.1a: Минимальный вертикальный срез.
Цель: Проверка FSM, маршрутизации и цикла записи/валидации на LangGraph 1.2.0.
"""

import os
import py_compile
from pathlib import Path
from typing import TypedDict, Optional, Literal
from pprint import pprint

from langgraph.graph import StateGraph, START, END

# =============================================================================
# 1. Определения состояний
# ВАЖНО: Эта FSM описывает жизненный цикл артефакта, а не каждый технический 
# шаг графа. Состояние "generating" может предшествовать как генерации, так и 
# попытке валидации, пока артефакт не достигнет "completed" или "failed".
# =============================================================================

class FileState(TypedDict):
    file_path: str
    content: str
    status: Literal["pending", "generating", "completed", "failed"]
    retries: int
    max_retries: int
    error_message: Optional[str]

class AgentState(TypedDict):
    file: FileState
    global_status: Literal["running", "completed", "failed"]

# =============================================================================
# 2. Изолированные функции побочных эффектов (согласно ADR-006)
# =============================================================================

def execute_write_and_compile(file_path: str, content: str) -> dict:
    """Записывает файл и проверяет его компиляцию. Возвращает структурированный результат."""
    parent_dir = Path(file_path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        py_compile.compile(file_path, doraise=True)
        return {"success": True, "error": None, "error_type": None, "file_path": file_path}
    except py_compile.PyCompileError as e:
        return {"success": False, "error": str(e), "error_type": "PyCompileError", "file_path": file_path}
    except (IOError, OSError) as e:
        return {"success": False, "error": str(e), "error_type": "IOError", "file_path": file_path}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnknownError", "file_path": file_path}

# =============================================================================
# 3. Узлы LangGraph
# =============================================================================

def init_node(state: AgentState) -> dict:
    print("[init_node] Инициализация. pending -> generating")
    return {"file": {**state["file"], "status": "generating"}}

def coder_node(state: AgentState) -> dict:
    retries = state["file"]["retries"]
    print(f"[coder_node] Генерация кода. retries: {retries}")
    
    content = "def broken_function(\n    return 'missing parenthesis'" if retries == 0 else "def fixed_function():\n    return 'success'"
    
    return {"file": {**state["file"], "content": content, "status": "generating"}}

def write_and_validate_node(state: AgentState) -> dict:
    file_state = state["file"]
    print(f"[write_and_validate_node] Вызов execute_write_and_compile для: {file_state['file_path']}")
    
    result = execute_write_and_compile(file_state["file_path"], file_state["content"])
    
    if result["success"]:
        print("[write_and_validate_node] ✅ Компиляция успешна.")
        return {"file": {**file_state, "status": "completed", "error_message": None}}
    else:
        print(f"[write_and_validate_node] ❌ Ошибка ({result['error_type']}): {result['error']}")
        if file_state["retries"] < file_state["max_retries"]:
            print(f"[write_and_validate_node] 🔄 Возврат к генерации. retries -> {file_state['retries'] + 1}")
            return {
                "file": {
                    **file_state,
                    "status": "generating",
                    "retries": file_state["retries"] + 1,
                    "error_message": result["error"]
                }
            }
        else:
            print(f"[write_and_validate_node] 🛑 Лимит попыток ({file_state['max_retries']}) исчерпан.")
            return {"file": {**file_state, "status": "failed", "error_message": f"Max retries exceeded. Last: {result['error']}"}}

def router_node(state: AgentState) -> Literal["coder_node", "summary_node"]:
    status = state["file"]["status"]
    print(f"[router_node] Маршрутизация из состояния: {status}")
    return "coder_node" if status == "generating" else "summary_node"

def summary_node(state: AgentState) -> dict:
    file_status = state["file"]["status"]
    global_status = "completed" if file_status == "completed" else "failed"
    print(f"[summary_node] Финальная агрегация. Глобальный статус: {global_status}")
    return {"global_status": global_status}

# =============================================================================
# 4. Сборка графа (LangGraph 1.2.0 API)
# =============================================================================

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("init_node", init_node)
    builder.add_node("coder_node", coder_node)
    builder.add_node("write_and_validate_node", write_and_validate_node)
    builder.add_node("summary_node", summary_node)
    
    builder.add_edge(START, "init_node")
    builder.add_edge("init_node", "coder_node")
    builder.add_edge("coder_node", "write_and_validate_node")
    
    builder.add_conditional_edges(
        "write_and_validate_node",
        router_node,
        {"coder_node": "coder_node", "summary_node": "summary_node"}
    )
    builder.add_edge("summary_node", END)
    
    return builder.compile()

# =============================================================================
# 5. Точка входа
# =============================================================================

if __name__ == "__main__":
    print("🚀 Запуск Orchestrator v2 Beta-0.1a\n" + "=" * 60)
    
    initial_state: AgentState = {
        "file": {
            "file_path": "/tmp/agent_dev_beta01a_test.py",
            "content": "",
            "status": "pending",
            "retries": 0,
            "max_retries": 2,
            "error_message": None
        },
        "global_status": "running"
    }
    
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    
    print("=" * 60)
    print("📊 РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:")
    print(f"Глобальный статус: {final_state['global_status']}")
    print(f"Статус файла:      {final_state['file']['status']}")
    print(f"Попыток сделано:   {final_state['file']['retries']}")
    if final_state['file']['error_message']:
        print(f"Последняя ошибка:  {final_state['file']['error_message']}")
    
    print("\n🔍 ПОЛНЫЙ FINAL_STATE (проверка мерджа TypedDict):")
    pprint(final_state, sort_dicts=False, width=100)
    
    print("\n📄 СОДЕРЖИМОЕ ФАЙЛА:")
    try:
        with open(final_state['file']['file_path'], 'r', encoding='utf-8') as f:
            print("-" * 40 + "\n" + f.read() + "-" * 40)
    except Exception as e:
        print(f"Не удалось прочитать файл: {e}")
    print("=" * 60)
