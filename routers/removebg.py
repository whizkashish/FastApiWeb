import sys
sys.path.append("..")
import os
from fastapi import FastAPI, File, UploadFile, Request, APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from rembg import remove
from PIL import Image
from models import BackgroundRemovedImages
from database import SessionLocal
import uuid
import tempfile
import base64
from .auth import get_current_user

app = FastAPI()


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

UPLOAD_TO_ORIGINAL = "original"
UPLOAD_TO_PROCESSED = "processed"

UPLOAD_DIR_ORIGINAL = "uploaded_images/original"
UPLOAD_DIR_PROCESSED = "uploaded_images/processed"

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/")
async def remove_bg(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("remove-bg.html", {"request": request, "user": user})


@router.post("/")
async def remove_bg(request: Request, file: UploadFile = File(...),db: Session = Depends(get_db)):
    input_image = await file.read()
    output_image = remove(input_image, post_process_mask=True)
   
    # Create a unique file name for both original and processed images
    original_file_name = f"{uuid.uuid4()}_original.png"
    processed_file_name = f"{uuid.uuid4()}_processed.png"
    
    original_file_path = os.path.join(UPLOAD_DIR_ORIGINAL, original_file_name)
    processed_file_path = os.path.join(UPLOAD_DIR_PROCESSED, processed_file_name)
    
    # Save the original input image to the directory
    with open(original_file_path, "wb") as f:
        f.write(input_image)
    
    # Save the processed output image to the directory
    with open(processed_file_path, "wb") as f:
        f.write(output_image)
    
    # Save paths in the database
    model_original_path = os.path.join(UPLOAD_TO_ORIGINAL, original_file_name)
    model_processed_path = os.path.join(UPLOAD_TO_PROCESSED, processed_file_name)
    image = BackgroundRemovedImages(original_path=model_original_path, processed_path=model_processed_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    image_path = model_processed_path
    
    return templates.TemplateResponse("remove-bg.html", {"request": request, "imagepath": image_path})
