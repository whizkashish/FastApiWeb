import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, status, Request, Form
from starlette.responses import RedirectResponse
from database import SessionLocal
from .auth import get_current_user, authenticate_user, get_password_hash
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {"description": "Not Found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")

@router.get("/change-password", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("change-password.html", {"request": request, "user": user})

@router.post("/change-password", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, 
                           username: str = Form(...),
                           password: str = Form(...),
                           new_password: str = Form(...),
                           db: Session = Depends(get_db)
                           ):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user = authenticate_user(username, password, db)
    msg = "Invalid username or password"
    if user is not False:
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        msg = "Password Updated"

    return templates.TemplateResponse("change-password.html", {"request": request,"user":user, "msg": msg})


