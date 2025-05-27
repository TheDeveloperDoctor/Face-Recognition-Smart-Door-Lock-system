from fastapi import APIRouter
from access_logs import get_all_logs

router = APIRouter()

@router.get("/logs")
async def get_logs():
    logs = get_all_logs()
    return {"logs": logs}