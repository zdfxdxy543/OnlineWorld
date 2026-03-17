from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

IMAGE_DIR = "storage/netdisk/ai_images/"

@router.get("/ai_image/{file_name}")
def get_ai_image(file_name: str):
    file_path = os.path.join(IMAGE_DIR, file_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path, media_type="image/png")
