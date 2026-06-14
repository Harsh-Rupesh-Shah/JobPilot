from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from backend.auth.jwt import decode_token

router = APIRouter()

async def get_user_from_token_query(token: str):
    """Helper to authenticate SSE requests which don't use Authorization headers easily in EventSource"""
    from fastapi import HTTPException, status
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError()
        return user_id
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.get("/{run_id}")
async def stream_run(run_id: str, token: str, request: Request):
    """
    Server-Sent Events endpoint. Streams token outputs from LangGraph.
    """
    user_id = await get_user_from_token_query(token)
    
    async def event_generator():
        # Stub implementation. Will yield real SSE tokens from langgraph astream_events
        yield f"data: {{\"event\": \"complete\"}}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
