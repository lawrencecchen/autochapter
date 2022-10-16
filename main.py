from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/autochapter")
async def autochapter(youtube_url: str = ""):
    return {"message": "Hello World"}