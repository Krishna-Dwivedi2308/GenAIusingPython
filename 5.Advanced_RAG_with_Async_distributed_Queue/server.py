from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Requestqueue.connection import queue
from Requestqueue.worker import process_query


class Query(BaseModel):
    query: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
async def chat(query: Query):
    # in this router we must enqueue the query and send user a response that their query has been queued
    job = queue.enqueue(process_query, query.query)
    return {"status": "queued", "job_id": job.id}


# now ideal method is to store the result corresponding to the job id in DB and return it to the user
# but RQ also provides us with polling so , we can try that in a seperate route
@app.get("/result/{job_id}")
def get_result(job_id: str = Path(..., description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    if job.is_finished:
        return {"status": "finished", "result": job.result}
    else:
        return {"status": "pending", "job_id": job_id}
