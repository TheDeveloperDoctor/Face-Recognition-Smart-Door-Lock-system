# app/camera/router.py
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from .stream import generate_video_stream

router = APIRouter()

@router.get("/live", response_class=StreamingResponse)
def live_camera_feed():
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
