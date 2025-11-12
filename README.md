# Project Overview

This project is a **blog generation system** designed to help companies quickly produce high-quality Markdown content based on company materials and user input. It leverages local LLMs served via Ollama to generate, modify, and optionally translate blog posts.

---

## Repo structure

```bash
.
├── api/
│   ├── dependencies.py
│   ├── main.py
│   ├── models/
│   ├── routers/
│   └── services/
├── pdfs/
│   ├── company_description.pdf
│   └── example_post.pdf
├── src
│   ├── blog_generation.py
│   ├── chunking.py
│   └── config/
└── tests
    └── test_endpoints.py
├── Dockerfile
├── docker-compose.yaml
├── README.md
└── requirements.txt
```


## How It Works

At runtime, the system follows these steps:

1. **PDF Parsing & Chunking**

   * Input PDFs (company descriptions or example posts) are parsed into Markdown text.
   * Each PDF is stored as a single "chunk" and tagged depending on its type (company description vs. example post).

2. **Context-Aware Blog Generation**

   * When a user submits a request, the system uses the stored chunks as context and examples. 
   * The generation process is split into three LLM inference steps.

3. **Inference steps** 
   1. **Blog Generation:** The system produces an initial blog post in Markdown based on user input and context.
   2. **Tone Modification (Optional):** The user can specify a tone of voice (e.g., authoritative, friendly) to adjust the writing style.
   3. **Translation (Optional):** The content can be translated into another language using the translation model.


# Run with Docker

This project is containerized with Docker Compose. The stack launches your FastAPI app and an Ollama instance for local LLM inference.

## Prerequisites
- Docker installed and running
- Docker Compose

## 1) Build and start containers
From the project root:
```bash
docker compose up -d --build
```
What this does:
- Builds the FastAPI image (Python 3.12)
- Starts two containers:
  - **blog_api** → FastAPI app on port **8080**
  - **ollama** → Ollama server on port **11434**
- Creates a persistent volume `ollama_data` to store model files

## 2) Pull the required LLM models
After containers are running, pull models into the Ollama container:
```bash
docker exec -it ollama ollama pull mistral:latest && \
docker exec -it ollama ollama pull zongwei/gemma3-translator:4b
```

Confirm pulled models:
```bash
docker exec -it ollama ollama list
```

# API Usage 
The FastAPI service exposes two main endpoints on port 8080: one to set the generation tone and one to generate a blog post. 

**Hosting:** http://localhost:8080

 **Health Check:** 
 ```bash 
 curl http://localhost:8080/health 
 ``` 


## 1) Set Tone of Voice 

 **Description:** Sets the tone or writing style that the blog generator will use for subsequent content generation requests. This is an optional setting, by default the tone is neutral. 

**Endpoint:** ``` POST /settings/tone ``` 

 **Example Request:** 
 ```bash
curl -X POST http://localhost:8080/settings/tone \
-H 'Content-Type: application/json' \
-d '{"tone":"authoritative"}'
 ``` 
 
 **Example Response:** 
 ```json
 { "tone": "authoritative" } 
 ``` 
## 2) Generate Blog Post 

**Description:** Generates a full blog post in Markdown format based on the given purpose or topic in a given language. The tone of voice (if set earlier) influences the style of the generated text. The ```language``` parameter is optional. 


**Endpoint:** ``` POST /generate ``` 

**Example Request:** 

```bash 
curl -X POST http://localhost:8080/generate \
-H 'Content-Type: application/json' \
-d '{"purpose": "How to keep energy bill low in the winter.", "language": "english"}'
```

**Example Response:** 
```json 
{ "markdown": "# Spend less on energy this winter ..."} 
``` 

# Models Used

This project uses two local models pulled and served by Ollama. The first model is used for content generation and tone adaptation, the second model used for translation.

## 1) Mistral:latest

* **Model Name / Version:** Mistral:latest
* **Parameter Count:** ~7B
* **License:** Apache 2.0
* **Notes:** Chosen for high-quality, general-purpose content generation. Good for producing blog posts in Markdown with coherent structure and style.

## 2) Gemma3 Translator

* **Model Name / Version:** zongwei/gemma3-translator:4b
* **Parameter Count:** 4B
* **License:** Open-source (specific license per Ollama model repo)
* **Notes:** Chosen for high-quality translation tasks. Enables multilingual support or content translation for generated text.





