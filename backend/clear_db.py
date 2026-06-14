import asyncio
from backend.db.database import db

async def wipe():
    print("Dropping collections...")
    await db.users.drop()
    await db.refresh_tokens.drop()
    await db.applications.drop()
    await db.outputs.drop()
    await db.resumes.drop()
    await db.long_term_memory.drop()
    await db.checkpoints.drop()
    await db.checkpoints_writes.drop()
    print("Database wiped successfully.")

if __name__ == "__main__":
    asyncio.run(wipe())
