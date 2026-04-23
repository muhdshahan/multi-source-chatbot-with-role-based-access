# Multi-Source Intelligent Chatbot

A role-based intelligent chatbot system that retrieves and generates responses from multiple data sources, including structured documents, knowledge bases, and video content, while enforcing strict access control.

## Overview

This project implements a unified chatbot interface capable of handling queries across heterogeneous data sources. It integrates structured product data from a PDF catalogue, unstructured knowledge from YouTube transcripts, and visual information from video frames. The system ensures that users can only access permitted sources and prevents cross-source data leakage through strict access control.

## Features

- Multi-source query handling (PDF, YouTube, Video)
- Retrieval-Augmented Generation (RAG) for semantic search
- Structured product retrieval using relational database
- Semantic similarity search using FAISS
- Role-based access control enforced before retrieval
- Prevention of cross-source data leakage
- Context-aware response generation using LLaMA-3.1-8B-Instant
- Hallucination minimization through grounding on retrieved context
- Query and response logging for monitoring and debugging

## Tech Stack

- Backend: Django
- Vector Database: FAISS
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- LLM: LLaMA-3.1-8B-Instant (via Groq API)
- YouTube Ingestion: youtube_transcript_api
- Video Processing: OpenCV
- Object Detection: YOLOv8m (yolov8m.pt)

## Setup Instructions

```
1. Create Virtual Environment
    python -m venv venv
    venv\Scripts\activate      # Windows

2. Install Dependencies
    pip install -r requirements.txt

3. Configure Environment Variables
    Create a .env file in the root directory: GROQ_API_KEY=your_api_key_here
```
## Database Setup
```
python manage.py makemigrations
python manage.py migrate

Create Superuser
python manage.py createsuperuser
```
## Data Ingestion
```
Source 1: PDF Catalogue
python ingestion/run_pdf_ingest.py

Source 2: YouTube Transcripts
python ingestion/run_youtube_ingest.py

Source 3: Video Processing
python ingestion/run_video_ingest.py
```
## How to Run Locally
```
python manage.py runserver
Access the application at: http://127.0.0.1:8000/api/ui/
```
## API Usage
```
Endpoint

POST /api/chat/

Request
{
  "query": "What is logistic regression?"
}
Response
{
  "response": "Generated answer based on retrieved context"
}
```

## Access Control

Each user is assigned a set of allowed sources. Access control is enforced before retrieval, ensuring that only authorized data is accessed. This prevents unauthorized queries and eliminates cross-source data leakage.

## Limitations

Object detection accuracy may vary in complex or crowded scenes
Limited detection of fine-grained attributes (e.g., gender, clothing details)
YouTube transcripts may contain noise or incomplete context
PDF parsing depends on consistent table formatting
FAISS is suitable for prototype-scale deployments
No automated testing or formal evaluation metrics implemented
