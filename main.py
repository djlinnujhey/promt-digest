"""main.py"""
import os
import asyncio
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from agents import (
    CollectorAgent,
    AnalystAgent,
    CuratorAgent,
    FormatterAgent,
    DispatcherAgent,
    RecallNode,
    StoreNode,
)

load_dotenv()

# --- Состояние пайплайна (упрощённый типизированный словарь) ---
class DigestState(dict):
    """Typed state for the LangGraph pipeline."""
    pass

# --- Инициализация общего хранилища (Pinecone) ---
from memory.pinecone_memory import PineconeMemory

memory = PineconeMemory()

# --- Сборка графа ---
workflow = StateGraph(DigestState)

# Узлы
workflow.add_node("collect", CollectorAgent().run)
workflow.add_node("analyze", AnalystAgent().run)
workflow.add_node("recall", RecallNode(memory).run)
workflow.add_node("curate", CuratorAgent(memory).run)
workflow.add_node("format", FormatterAgent().run)
workflow.add_node("dispatch", DispatcherAgent().run)
workflow.add_node("store", StoreNode(memory).run)

# Условные переходы
workflow.add_conditional_edges(
    "collect",
    lambda s: END if not s.get("raw_articles") else "analyze",
    ["analyze"],
)

workflow.add_conditional_edges(
    "analyze",
    lambda s: END if not s.get("analyzed_items") else "recall",
    ["recall"],
)

# Последовательные переходы
workflow.add_edge("recall", "curate")
workflow.add_edge("curate", "format")
workflow.add_edge("format", "dispatch")
workflow.add_edge("dispatch", "store")
workflow.add_edge("store", END)

graph = workflow.compile()

async def run_daily():
    """Точка входа, вызываемая планировщиком."""
    today = datetime.utcnow().date().isoformat()
    await graph.ainvoke({"date": today})

if __name__ == "__main__":
    asyncio.run(run_daily())