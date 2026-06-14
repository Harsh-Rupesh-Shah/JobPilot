import asyncio
import uuid
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from backend.memory.checkpointer import get_checkpointer

def node_a(state):
    print("Node A running")
    return {"val": "A"}

def hitl_node(state):
    print("Interrupting...")
    interrupt({"msg": "Please approve"})
    return {"val": "HITL"}

async def main():
    builder = StateGraph(dict)
    builder.add_node("node_a", node_a)
    builder.add_node("hitl", hitl_node)
    builder.add_edge(START, "node_a")
    builder.add_edge("node_a", "hitl")
    builder.add_edge("hitl", END)
    
    checkpointer = get_checkpointer()
    graph = builder.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    print("Running graph...")
    async for event in graph.astream_events({"val": "init"}, config, version="v2"):
        name = event["name"]
        event_type = event["event"]
        if name == "LangGraph" and event_type == "on_chain_end":
            print("LangGraph end metadata:", event.get("metadata"))
        print(f"Event: {event_type} | Name: {name}")

    print("Reading snapshot...")
    snapshot = graph.get_state(config)
    print("Next:", snapshot.next)
    if snapshot.tasks:
        for t in snapshot.tasks:
            print("Task interrupts:", t.interrupts)

if __name__ == "__main__":
    asyncio.run(main())
