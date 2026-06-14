import asyncio
import os
from backend.agents.supervisor import supervisor_agent
from backend.agents.state import ApplicationState

async def test():
    state = ApplicationState(
        job_description="Software Engineer at Google. Must know Python, C++, and Kubernetes.",
        resume_text="I am a software engineer with 5 years of Python experience.",
        run_id="test"
    )
    res = await supervisor_agent(state, {"configurable": {"thread_id": "test"}})
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
