import asyncio
import os
import sys
sys.path.insert(0, "..")
from backend.llm.model import get_structured_llm
from pydantic import BaseModel

class Test(BaseModel):
    name: str

async def test():
    try:
        llm = get_structured_llm(Test)
        res = await llm.ainvoke("My name is Alice")
        print("Success:", res)
    except Exception as e:
        print("ERROR:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
