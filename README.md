# Assistente Virtual com IBM WatsonX.ai

Este projeto implementa um assistente virtual utilizando IBM WatsonX.ai, arquitetura RAG (Retrieval-Augmented Generation) e modelos de linguagem avançados (LLaMA 3 70B Instruct).  


## Funcionalidades

- Autenticação segura via IBM Cloud API Key.
- Pesquisa vetorial para recuperar dados contextuais relevantes (RAG).
- Geração de respostas formais, acolhedoras e personalizadas.
- Implantação do serviço AI como endpoint REST escalável.

---

## Tecnologias Utilizadas

- Python 3.11
- IBM WatsonX AI SDK (`ibm_watsonx_ai`)
- IBM Cloud Functions (para execução serverless)
- Jupyter Notebook (orquestração, deploy e testes)
- LLaMA 3 70B Instruct (foundation model)
- RAG (Retrieval-Augmented Generation)
- JSON Schema (validação de requisições e respostas)

---

## Pré-requisitos

- Conta IBM Cloud com permissões para WatsonX.ai e Cloud Functions.
- IBM Cloud API Key com acesso ao serviço WatsonX.
- Espaço configurado no IBM Cloud para deploy dos assets (vector index e AI Service).
- Python 3.11 instalado localmente.
- Jupyter Notebook instalado para testes e deploy.

