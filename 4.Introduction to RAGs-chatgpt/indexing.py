from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


def index_pdf_to_qdrant(
    pdf_filename: str,
    collection_name: str = "learning_vectors",
    qdrant_url: str = "http://localhost:6333/",
):

    load_dotenv()

    # Load PDF
    pdf_path = Path(__file__).parent / "uploads" / pdf_filename
    loader = PyPDFLoader(file_path=pdf_path)
    docs = loader.load()
    # print(docs[0])

    # Clean invalid surrogate characters
    for doc in docs:
        if doc.page_content:
            doc.page_content = doc.page_content.encode("utf-8", "ignore").decode(
                "utf-8", "ignore"
            )

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(docs)

    # Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Store in Qdrant
    vector_store = QdrantVectorStore.from_documents(
        docs,
        embeddings,
        url=qdrant_url,
        collection_name=collection_name,
    )

    print("------------ indexing of docs done here ------------")
    return {"message": "indexing of docs done here"}
