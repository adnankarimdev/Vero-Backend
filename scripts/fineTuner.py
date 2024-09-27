from langchain.document_loaders import TextLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import pickle
import os

os.environ["OPENAI_API_KEY"] = (
    "sk-proj-BkqMCfMCu8aJz0M19aj9T3BlbkFJCqFGN85AiM1NP2lJyrF1"
)

faiss_index_path = "faiss_index_p&s"
documents_path = "faiss_documents_p&s.pkl"

# Load the text file
loader = TextLoader(
    "/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/results/P&S/allReviews.txt"
)
documents = loader.load()

# Create embeddings using OpenAI's API
embeddings = OpenAIEmbeddings()

# Store documents as embeddings in a vector store
vectorstore = FAISS.from_documents(documents, embeddings)

# Save the FAISS index
vectorstore.save_local(faiss_index_path)

# Save the documents metadata
with open(documents_path, "wb") as f:
    pickle.dump(documents, f)

print("FAISS index and documents saved successfully.")
