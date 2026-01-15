import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# URL do site
url = "https://www.flordosol.com.br/colares/"

# Cabeçalhos HTTP para imitar um navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Fazer a requisição HTTP para obter o conteúdo da página
response = requests.get(url, headers=headers)
response.raise_for_status()

# Analisar o conteúdo HTML da página
soup = BeautifulSoup(response.text, "html.parser")

# Função para gerar nomes de arquivos válidos
def limpar_nome_arquivo(nome):
    # Remove parâmetros de URL
    nome = urlparse(nome).path
    # Remove caracteres inválidos
    nome = re.sub(r'[<>:"/\\|?*]', '', nome)
    return os.path.basename(nome)

# Encontrar todas as tags de imagem e outros elementos que podem conter URLs de imagens
imagens = soup.find_all("img")
links_imagens = []

for img in imagens:
    img_url = img.get("src") or img.get("data-src")
    if img_url:
        img_url = urljoin(url, img_url)
        links_imagens.append(img_url)

# Baixar todas as imagens encontradas
for img_url in links_imagens:
    try:
        # Nome da imagem (limpo de caracteres inválidos)
        img_nome = limpar_nome_arquivo(img_url)
        
        # Criar uma pasta para a imagem
        pasta_imagem = os.path.join("imagens_colares", os.path.splitext(img_nome)[0])
        os.makedirs(pasta_imagem, exist_ok=True)
        
        # Caminho completo para salvar a imagem
        caminho_img = os.path.join(pasta_imagem, img_nome)
        
        # Baixar a imagem
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()
        
        # Salvar a imagem no disco
        with open(caminho_img, "wb") as f:
            f.write(img_response.content)
        
        print(f"Imagem {img_nome} baixada com sucesso na pasta {pasta_imagem}!")
    except Exception as e:
        print(f"Erro ao baixar a imagem {img_url}: {e}")

print("Download concluído!")
