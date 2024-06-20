import sys
sys.path.append("..")

from fastapi import FastAPI, File, UploadFile, Request, APIRouter
from fastapi.responses import FileResponse
from rembg import remove
from PIL import Image
import uuid
import tempfile
import base64
from .auth import get_current_user

app = FastAPI()


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")
@router.get("/")
async def remove_bg(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("remove-bg.html", {"request": request, "user": user})


@router.post("/")
async def remove_bg(request: Request, file: UploadFile = File(...)):
    input_image = await file.read()
    output_image = remove(input_image, post_process_mask=True)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(output_image)
    
    # Read the output image and encode it as a base64 string
    encoded_image = False
    with open(temp_file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    user = await get_current_user(request)
    return templates.TemplateResponse("remove-bg.html", {"request": request, "user": user, "encoded_image": encoded_image})
