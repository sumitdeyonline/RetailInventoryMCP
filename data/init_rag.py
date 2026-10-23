import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

def initialize_vector_db():
    docs_dir = Path(__file__).parent / 'docs'
    dump_path = Path(__file__).parent / 'vector_store.json'
    
    # Load all markdown files from the docs directory
    documents = []
    for md_file in docs_dir.glob('**/*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            documents.append(Document(page_content=text, metadata={"source": md_file.name}))
    
    print(f"Loaded {len(documents)} documents.")
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Store in InMemoryVectorStore
    print("Saving to InMemoryVectorStore...")
    vector_store = InMemoryVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    vector_store.dump(str(dump_path))
    print(f"Vector DB initialized at {dump_path}")

if __name__ == "__main__":
    initialize_vector_db()
