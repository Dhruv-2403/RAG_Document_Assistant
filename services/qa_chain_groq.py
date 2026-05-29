
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


class QAChainGroq:
  

    def __init__(self, vector_store_manager):
      
        self.vector_store = vector_store_manager

    
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.strip() in ["", "your_groq_api_key_here"]:
            raise ValueError(
                "GROQ_API_KEY not found or not configured. "
                "Get your free key at: https://console.groq.com/keys"
            )

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Fast and capable model
            temperature=0,
            groq_api_key=api_key,
            max_tokens=1024
        )

 
        self.prompt_template = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, just say that you don't have enough information to answer the question. Don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def ask(self, question: str) -> Dict:
      
        retriever = self.vector_store.get_retriever(k=4)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )

        result = qa_chain.invoke({"query": question})

        sources = []
        for doc in result.get("source_documents", []):
            sources.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            })

        return {
            "answer": result["result"],
            "sources": sources
        }