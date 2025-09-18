from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from google import genai


def process_query(query: str):
    # now we can keep count also and limit our requests
    # if count>30 sleep(10s) - something like this
    messages = []
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )
    # # using [embedding] model create embeddings of [split_docs] and store in DB
    url = "http://localhost:6333/"  # Qdrant instance
    collection_name = "book_vector"
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=url,
        collection_name=collection_name,
    )
    print("Processing query...", query)
    messages.append({"role": "user", "content": query})
    # # vector similarity search [query] in DB
    search_results = vector_db.similarity_search(query)
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
    print(response.text, "\n\n\n")
    # now ideally we should save the response to a DB, but here for now we just print
    messages.append({"role": "assistant", "content": response.text})

    return {"info": response.text}
