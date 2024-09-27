from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import os
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = (
    "sk-proj-BkqMCfMCu8aJz0M19aj9T3BlbkFJCqFGN85AiM1NP2lJyrF1"
)

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
# Path where the FAISS index and documents are saved
faiss_index_path = "faiss_index_p&s"
documents_path = "faiss_documents_p&s.pkl"

# Load the documents metadata
import pickle

with open(documents_path, "rb") as f:
    documents = pickle.load(f)

# Create an embedding instance (use the same embedding method used during saving)
embeddings = OpenAIEmbeddings()

# Load the FAISS index
vectorstore = FAISS.load_local(
    faiss_index_path, embeddings, allow_dangerous_deserialization=True
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,  # Or use another model if you have one
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
)

# Example query
query = "Which locations have the best reviews?"
response = qa_chain({"query": query})

print(response["result"])
