import solver
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/solve")
async def solve():
    response = await solver.solver("https://d000d.com/e/b0pckrukog0h","0x4AAAAAAALn0BYsCrtFUbm_");
    return response;
