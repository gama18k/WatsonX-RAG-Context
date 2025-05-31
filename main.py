import http.client
import urllib.parse
import json
from datetime import datetime

def main(params):

    # Etapa 1 - Leitura dos parâmetros de entrada
    mensagem = params.get("mensagem", "")
    nome = params.get("nome", "")
    cpf = params.get("cpf", "")
    valor = params.get("valor", "")
    produto = params.get("produto", "")
    contexto_genai = params.get("contexto", [])

    # Etapa 2 - Verificação de reset de contexto
    if mensagem == "/reset":
        return {
            "statusCode": 200,
            "body": {"content": "Contexto inicializado"}
        }

    # Etapa 3 - Formatação da data atual
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    now = datetime.now()
    day = now.day
    month = months[now.month - 1]
    year = now.year
    data_atual = f"{day:02d}/{month}/{year}"

    # Etapa 4 - Autenticação com o IAM para obter token de acesso
    iam_url = "iam.cloud.ibm.com"
    iam_endpoint = "/identity/token"
    apikey = "APIKEY"
    iam_payload = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": apikey
    })
    iam_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    conn = http.client.HTTPSConnection(iam_url)
    conn.request("POST", iam_endpoint, body=iam_payload, headers=iam_headers)
    iam_response = conn.getresponse()
    if iam_response.status != 200:
        raise ValueError(f"Falha ao obter token IAM: {iam_response.status} - {iam_response.reason}")
    iam_data = json.loads(iam_response.read().decode())
    token = iam_data.get("access_token")
    conn.close()

    # Etapa 5 - Inicialização do contexto com informações do cliente (se necessário)
    if not contexto_genai:
        dados_cliente = {
            "role": "system",
            "content": (
                f"Nome do cliente: {nome}\n"
                f"CPF: {cpf}\n"
                f"Valor da divida: {valor}\n"
                f"Produto da divida: {produto}\n"
                f"Data atual: {data_atual}"
                f"SYSTEM PROMPT"
            )
        }
        contexto_genai.insert(0, dados_cliente)

    # Etapa 6 - Registro da nova mensagem do usuário no contexto
    contexto_genai.append({
        "role": "user",
        "content": mensagem
    })

    # Etapa 7 - Chamada ao endpoint do WatsonX para obter resposta do modelo
    watsonx_url = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/apilink"
    watsonx_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    watsonx_payload = {"messages": contexto_genai}

    try:
        conn = http.client.HTTPSConnection(watsonx_url.split('/')[2])
        path = '/' + '/'.join(watsonx_url.split('/')[3:])
        conn.request("POST", path, body=json.dumps(watsonx_payload), headers=watsonx_headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        if response.status >= 400:
            return {"statusCode": 200, "body": f"HTTP {response.status}: {data.decode('utf-8')}"}

        try:
            watsonx_response = json.loads(data)
        except json.JSONDecodeError as e:
            raise Exception(f"Resposta não é um JSON válido: {data.decode('utf-8')} - Erro: {str(e)}")

        if not isinstance(watsonx_response, dict) or "choices" not in watsonx_response:
            raise Exception(f"Resposta JSON inesperada: {watsonx_response}")

        response_content = watsonx_response.get("choices", [{}])[0].get("message", {}).get("content", "")

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": "Failed to fetch response from WatsonX", "details": str(e)}
        }

    # Etapa 8 - Extração de conteúdo JSON da resposta, se presente
    def extrair_json_da_resposta(texto):
        inicio = texto.find("[[JSON]]")
        fim = texto.find("[[/JSON]]")
        json_extraido = None

        if inicio != -1 and fim != -1:
            trecho_json = texto[inicio + len("[[JSON]]"):fim].strip()
            try:
                json_extraido = json.loads(trecho_json)
                texto = texto[:inicio].strip()
            except json.JSONDecodeError:
                pass

        return texto, json_extraido

    texto_limpo, parametros_negociacao = extrair_json_da_resposta(response_content)

    # Etapa 9 - Registro da resposta do assistente no contexto
    contexto_genai.append({
        "role": "assistant",
        "content": texto_limpo
    })

    # Etapa 10 - Retorno da resposta final
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {
            "response": texto_limpo,
            "contexto": contexto_genai,
            "parametros_negociacao": parametros_negociacao
        }
    }
