AI-Powered Smart Service Desk System

Overview:
The AI-Powered Smart Service Desk System is an intelligent query resolution platform built using Retrieval-Augmented Generation (RAG). It enables users to ask questions and receive accurate, context-aware answers from large document datasets.

Features
1.Semantic Search using FAISS and Sentence Transformers
2.LLM Integration with Groq API for intelligent responses
3.Document Processing with OCR (Tesseract) for PDFs and images
4.FastAPI Backend for scalable and high-performance APIs
5.Efficient Query Handling with optimized retrieval pipeline
6.Handles large-scale document datasets efficiently

Tech Stack
Backend: FastAPI (Python)
Vector Database: FAISS
Embeddings: Sentence Transformers
LLM API: Groq API
OCR: Tesseract OCR
Other Tools: NumPy, Pandas

How It Works
Upload documents (PDF/Image)
Extract text using OCR
Convert text into embeddings
Store embeddings in FAISS
User submits query
Retrieve relevant context
Generate response using LLM

Future Enhancements
UI dashboard using React
Multi-language support
Advanced analytics & logging
Cloud deployment (AWS/GCP)
