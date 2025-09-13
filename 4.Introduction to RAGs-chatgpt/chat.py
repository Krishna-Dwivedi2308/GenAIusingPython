from dotenv import load_dotenv

load_dotenv()
# backend/main.py
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from google import genai
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    collection_name: str


import os
from indexing import index_pdf_to_qdrant

app = FastAPI()

# allow requests from frontend (adjust origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use pathlib for paths
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = UPLOAD_DIR / file.filename
    print(file.filename)
    # Save uploaded file
    with open(file_location, "wb") as f:
        f.write(await file.read())
        collection_name = f"learning_vectors_{file.filename}"
    # now it should be checked if this collection already exists but let us leave it for now
    try:
        # Index into Qdrant
        vector_store = index_pdf_to_qdrant(
            pdf_filename=file.filename,
            collection_name=collection_name,
            qdrant_url="http://localhost:6333/",
        )
        message = f"file '{file.filename}' processed and indexed successfully"
    except Exception as e:
        message = f"Error while processing file '{file.filename}': {str(e)}"
        return {"error": f"Failed to process {file.filename}: {str(e)}"}
    finally:
        # Always remove the uploaded file
        if file_location.exists():
            file_location.unlink()

    return JSONResponse(
        status_code=200, content={"info": message, "collection_name": collection_name}
    )


# now file is uploaded in server and stored in uploads folder

# index the received file and store in vector db
messages = []


@app.post("/chat")
async def chat(req: ChatRequest):
    query = req.query
    if not query:
        return {"error": "No query provided"}
    collection_name = req.collection_name
    if not collection_name:
        return {"error": "No collection name provided"}
    print(query)
    print(collection_name)
    # 1. take user query
    # 2. embeddins for user query and search in vector db for the query
    # 3. now give user query and related relevant chunks to LLM for cleaner response
    # query=input("You:")
    # 2. vector similarity search

    messages.append({"role": "user", "content": query})

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    # # using [embedding] model create embeddings of [split_docs] and store in DB
    url = "http://localhost:6333/"  # Qdrant instance

    vector_db = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=url,
        collection_name=collection_name,
    )

    # # vector similarity search [query] in DB

    search_results = vector_db.similarity_search(query)

    # # print('search results',search_results)
    # # print([items.metadata['page'] for items in search_results])

    # # now give user query and related relevant chunks to LLM for cleaner response
    # context = "\n\n\n".join([f"Book Title: {result.metadata['title']}\nPage Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}"for result in search_results])
    context = "\n\n\n".join(
        [
            f"Book Title: {result.metadata.get('title', 'Unknown')}\n"
            f"Page Content: {result.page_content}\n"
            f"Page Number: {result.metadata.get('page_label', 'N/A')}\n"
            f"File Location: {result.metadata.get('source', 'N/A')}"
            for result in search_results
        ]
    )

    SYSTEM_PROMPT = f"""
    You are a helpful AI assistant who answers user queries based on the provided context 
    retrieved from a pdf file along with page_contents and page number.

    You should only answer the user based on the 'user query' and the following context , and navigate 
    the user to open the right page number to know more .

    usrer query: 
    {query}
    context: 
    {context}

    note that you can only answer the user query based on the context provided.
    also, do not miss any page content data . use all of it in your response.
    merge all the page content to generate a meaningful response but do not change the language of the page content or the examples. 
    Just slightly add more or modify them to make sense for the user in case they are incomplete in some way.

    example output(structure only-add markdown formatting to it from your side):
    Your Query: 
    {query}
    Results from your Book: 
    Book Title: Book Title

    Reference 1: 
    Page Snippet: This is the first page content. 
    Page Number: 1

    Reference 2: 
    Page Snippet: This is the second page content. 
    Page Number: 2

    Reference 3: Page Snippet: This is the third page content. 
    Page Number: 3   

    For better understanding , refers these pages : 1,2,3
    The output should be in proper md code so that i can use it at frontend
    """

    # # # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=SYSTEM_PROMPT,
    )
    print(response.text)

    messages.append({"role": "assistant", "content": response.text})

    return {"info": response.text}
