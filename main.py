from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, Users, removebg
from starlette import status
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="uploaded_images"), name="images")


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}

# @app.get("/")
# async def root():
#     return RedirectResponse(url="/todos",status_code=status.HTTP_302_FOUND)

app.include_router(removebg.router)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(Users.router)