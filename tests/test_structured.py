import asyncio
import os
import sys
sys.path.insert(0, "..")
from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel
from backend.config import settings

class TestSchema(BaseModel):
    name: str
    age: int

async def test():
    try:
        llm = ChatOpenRouter(
            model="openrouter/auto",
            openrouter_api_key=settings.OPENROUTER_API_KEY,
            temperature=0,
            max_tokens=100
        )
        structured_llm = llm.with_structured_output(TestSchema)
        res = await structured_llm.ainvoke("My name is John and I am 30 years old")
        print("SUCCESS structured output:", res)
    except Exception as e:
        print("ERROR structured output:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
