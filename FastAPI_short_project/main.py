from fastapi import FastAPI  # to build apis
from pydantic import (
    BaseModel,
)  # to define validations and rules for our reqs and responses
from typing import List

app = FastAPI()


class Tea(BaseModel):
    id: int
    name: str
    origin: str


teas: List[Tea] = []

# decorators
# functoin definition


@app.get("/")
def read_root():
    return {"message": "welcome to chaicode"}


@app.get("/teas")
def return_teas():
    return teas


@app.post("/teas")
def add_tea(tea: Tea):
    teas.append(tea)
    return tea


@app.put("?teas/{tea_id}")
def update_tea(tea_id: int, updated_tea: Tea):
    for index, tea in enumerate(teas):
        if tea.id == tea_id:
            teas[index] = updated_tea
            return updated_tea
    return {"error": "Tea not found "}


@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    for index, tea in enumerate(teas):
        if tea.id == tea_id:
            deleted = teas.pop(index)
            return deleted
        return {"error": "Tea not found "}
