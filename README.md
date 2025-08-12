# mini-rag-app

This is a minimal implementaion of the RAG model for question answering.

## Requirements

- Python 3.10 or later

#### Install Python using MiniConda
1) Download and install MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install#anaconda-website).
2) Create a new envirnment using the following command:
```bash
$ conda create -n mini-rag python=3.10
```
3) Activate the environment:
```bash
$ conda activate mini-rag
```
### Setup the environment variables
```bash
$ cp .env.examples .env
```
Set your environment variables in the `.env` file. Like `HF_ACCESS_TOKEN` value

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```
- Update `.env` with your credentials 


```bash
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server
```bash
$ uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
