from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.log_router import router as logs_router
from router.qrcode_router import router as qrcode_router
from router.monitoring_router import router as camera_router
from router.doorlock import router as doorlock_router
from router.image_upload import router as image_upload_router

from pyngrok import ngrok

# Start ngrok tunnel
public_url = ngrok.connect(8000)
print(f"FastAPI is running on: {public_url}")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    # allow_credentials=True,
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(logs_router, tags=["Logs"])
app.include_router(qrcode_router, prefix="/qr", tags=["QR Code API"])
app.include_router(camera_router, tags=["Live Monitoring"])
app.include_router(doorlock_router, tags=["Door_Unlocking API"])
app.include_router(image_upload_router, tags=["Image Upload"])

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
