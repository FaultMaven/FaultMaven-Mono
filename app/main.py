from fastapi import FastAPI

app = FastAPI()  # This is what "app.main:app" refers to

@app.get("/")
def read_root():
    return {"message": "Hello, FaultMaven!"}

