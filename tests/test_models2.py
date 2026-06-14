import asyncio
import os
import sys
sys.path.insert(0, "..")
from langchain_openrouter import ChatOpenRouter
from backend.config import settings

models_to_test = [
    "openrouter/auto",
    "google/gemini-2.5-flash-free",
    "meta-llama/llama-3-8b-instruct:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "qwen/qwen3-coder:free"
]

async def test():
    for m in models_to_test:
        print(f"Testing {m}...")
        try:
            llm = ChatOpenRouter(
                model=m,
                openrouter_api_key=settings.OPENROUTER_API_KEY,
                max_tokens=10
            )
            res = await llm.ainvoke("Say hello")
            print(f"SUCCESS {m}: {res.content}")
        except Exception as e:
            print(f"ERROR {m}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test())
