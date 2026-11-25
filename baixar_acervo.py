import os
import re
import sys
import time
from urllib.parse import urlparse, unquote
import pandas as pd
import requests
import urllib3

# ======================= CONFIGURAÇÕES =======================
BASE_URL = "https://www.acervocal.unb.br/wp-json/tainacan/v2"
COLECAO_ID = 1565
ITENS_POR_PAGINA = 96
PASTA_SAIDA = f"acervo_colecao_{COLECAO_ID}"
ARQUIVO_EXCEL = "obras.xlsx"
PASTA_IMAGENS = "imagens"
BAIXAR_IMAGENS = True
BAIXAR_ANEXOS = True
VERIFICAR_CERTIFICADO = False
PAUSA = 0.3
TENTATIVAS = 3
# =============================================================

if not VERIFICAR_CERTIFICADO:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sessao = requests.Session()
sessao.verify = VERIFICAR_CERTIFICADO
sessao.headers.update({"User-Agent": "Mozilla/5.0 (pesquisa academica - UnB)"})

EXTENSOES_ARQUIVO = (".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".webp",
                     ".pdf", ".mp3", ".mp4", ".wav")

def get_com_tentativas(url, params=None, stream=False):
    ultimo_erro = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resp = sessao.get(url, params=params, timeout=90, stream=stream)
            resp.raise_for_status()
            return resp
        except requests.exceptions.SSLError as e:
            print("\n** ERRO DE CERTIFICADO (TLS) **")
            print("Deixe VERIFICAR_CERTIFICADO = False no topo do script.")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            ultimo_erro = e
            print(f"    falha (tentativa {tentativa}/{TENTATIVAS}): {e}")
            time.sleep(2 * tentativa)
    raise ultimo_erro

def texto_limpo(valor):
    if valor is None:
        return ""
    if isinstance(valor, list):
        return " | ".join(t for t in (texto_limpo(v) for v in valor) if t)
    if isinstance(valor, dict):
        for chave in ("value_as_string", "name", "title", "rendered", "value", "url"):
            if chave in valor:
                return texto_limpo(valor[chave])
        return ""
    texto = re.sub(r"<[^>]+>", " ", str(valor))
    return re.sub(r"\s+", " ", texto).strip()

def nome_seguro(texto, limite=80):
    texto = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", str(texto))
    return re.sub(r"\s+", " ", texto).strip(" .")[:limite] or "sem_nome"

def extensao_da_url(url, padrao=".jpg"):
    caminho = unquote(urlparse(url).path)
    ext = os.path.splitext(caminho)[1].lower()
    return ext if ext and len(ext) <= 5 else padrao

def urls_em_html(html):
    if not isinstance(html, str):
        return []
    urls = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', html)
    return [u for u in urls if u.lower().split("?")[0].endswith(EXTENSOES_ARQUIVO)]

def url_thumbnail(item):
    thumb = item.get("thumbnail")
    if isinstance(thumb, dict):
        for tamanho in ("full", "large", "medium_large", "medium"):
            dado = thumb.get(tamanho)
            if isinstance(dado, list) and dado and isinstance(dado[0], str):
                return dado[0]
            if isinstance(dado, str) and dado.startswith("http"):
                return dado
    return ""

def url_de_anexo(anexo):
    if not isinstance(anexo, dict):
        return ""
    for chave in ("url", "source_url", "guid", "link"):
        v = anexo.get(chave)
        if isinstance(v, dict):
            v = v.get("rendered") or v.get("raw")
        if isinstance(v, str) and v.startswith("http") and v.lower().split("?")[0].endswith(EXTENSOES_ARQUIVO):
            return v
    thumbs = anexo.get("thumbnail") or anexo.get("thumbnails")
    if isinstance(thumbs, dict):
        for tamanho in ("full", "large", "medium"):
            d = thumbs.get(tamanho)
            if isinstance(d, list) and d and isinstance(d[0], str):
                return d[0]
            if isinstance(d, str) and d.startswith("http"):
                return d
    return ""

def baixar_itens():
    url = f"{BASE_URL}/collection/{COLECAO_ID}/items/"
    todos, pagina, total_paginas = [], 1, None
    while True:
        params = {"perpage": ITENS_POR_PAGINA, "order": "ASC", "orderby": "title", "paged": pagina}
        print(f"Lendo pagina {pagina}" + (f"/{total_paginas}" if total_paginas else "") + "...")
        resp = get_com_tentativas(url, params=params)
        if total_paginas is None:
            try:
                total_paginas = int(resp.headers.get("X-WP-TotalPages", 0)) or None
            except ValueError:
                total_paginas = None
            if resp.headers.get("X-WP-Total"):
                print(f"Total de obras na colecao: {resp.headers['X-WP-Total']}")
        dados = resp.json()
        itens = dados.get("items", []) if isinstance(dados, dict) else dados
        if not itens:
            break
        todos.extend(itens)
        if (total_paginas and pagina >= total_paginas) or len(itens) < ITENS_POR_PAGINA:
            break
        pagina += 1
        time.sleep(PAUSA)
    print(f"{len(todos)} obras lidas.\n")
    return todos

def listar_anexos(item_id):
    try:
        resp = get_com_tentativas(f"{BASE_URL}/items/{item_id}/attachments")
        dados = resp.json()
        if isinstance(dados, dict):
            dados = dados.get("items") or dados.get("attachments") or []
        return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"    nao consegui listar anexos do item {item_id}: {e}")
        return []

def salvar_arquivo(url, caminho):
    if os.path.exists(caminho) and os.path.getsize(caminho) > 0:
        return True
    try:
        resp = get_com_tentativas(url, stream=True)
        temp = caminho + ".parcial"
        with open(temp, "wb") as f:
            for bloco in resp.iter_content(chunk_size=65536):
                f.write(bloco)
        os.replace(temp, caminho)
        return True
    except Exception as e:
        print(f"    ERRO ao baixar {url}: {e}")
        return False

def ficha_da_obra(item):
    linha = {
        "id": item.get("id"),
        "Titulo": texto_limpo(item.get("title")),
        "Descricao": texto_limpo(item.get("description")),
        "Link no acervo": item.get("url", ""),
    }
    metadados = item.get("metadata") or {}
    if isinstance(metadados, dict):
        for slug, meta in metadados.items():
            if isinstance(meta, dict):
                nome = str(meta.get("name") or slug).strip()
                valor = meta.get("value_as_string")
                if valor in (None, ""):
                    valor = meta.get("value")
            else:
                nome, valor = slug, meta
            valor = texto_limpo(valor)
            if nome.lower() in ("titulo", "title", "descricao", "description"):
                if valor and valor != linha.get("Titulo") and valor != linha.get("Descricao"):
                    linha[f"{nome} (ficha)"] = valor
                continue
            linha[nome] = valor
    linha["Criado em"] = item.get("creation_date", "")
    linha["Modificado em"] = item.get("modification_date", "")
    return linha

def baixar_midias(item, linha, pasta_imgs):
    registro = linha.get("Numero de Registro") or linha.get("id")
    prefixo = nome_seguro(f"{registro}_{linha.get('Titulo', '')}", 70)
    urls = []
    if BAIXAR_IMAGENS:
        principal = url_thumbnail(item)
        if principal:
            urls.append(principal)
        urls += urls_em_html(item.get("document_as_html"))
        if isinstance(item.get("document"), str) and item["document"].lower().split("?")[0].endswith(EXTENSOES_ARQUIVO):
            urls.append(item["document"])
    if BAIXAR_ANEXOS:
        for anexo in listar_anexos(item.get("id")):
            u = url_de_anexo(anexo)
            if u:
                urls.append(u)
        time.sleep(PAUSA)
    vistos, unicas = set(), []
    for u in urls:
        base = re.sub(r"-\d+x\d+(?=\.\w+$)", "", unquote(urlparse(u).path))
        if base not in vistos:
            vistos.add(base)
            unicas.append(u)
    arquivos = []
    for n, u in enumerate(unicas, 1):
        sufixo = "" if n == 1 else f"_{n}"
        nome = f"{prefixo}{sufixo}{extensao_da_url(u)}"
        if salvar_arquivo(u, os.path.join(pasta_imgs, nome)):
            arquivos.append(nome)
        time.sleep(PAUSA)
    return unicas, arquivos

def organizar_colunas(df):
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, (df.astype(str).apply(lambda c: c.str.strip()) != "").any()]
    primeiras = ["Numero de Registro", "Titulo", "Denominacao", "Autoria",
                 "Grupo indigena", "Data de producao", "Local de producao",
                 "Material/Tecnica/Suporte", "Dimensoes", "Descricao"]
    finais = ["Qtd. arquivos", "Arquivos baixados", "URLs dos arquivos",
              "Link no acervo", "id", "Criado em", "Modificado em"]
    inicio = [c for c in primeiras if c in df.columns]
    fim = [c for c in finais if c in df.columns]
    meio = [c for c in df.columns if c not in inicio and c not in fim]
    return df[inicio + meio + fim]

def main():
    print(f"Acervo CAL/UnB - colecao {COLECAO_ID}\n")
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    pasta_imgs = os.path.join(PASTA_SAIDA, PASTA_IMAGENS)
    if BAIXAR_IMAGENS or BAIXAR_ANEXOS:
        os.makedirs(pasta_imgs, exist_ok=True)
    itens = baixar_itens()
    if not itens:
        print("Nenhuma obra encontrada. Confira o numero da colecao.")
        return
    linhas = []
    for i, item in enumerate(itens, 1):
        linha = ficha_da_obra(item)
        if BAIXAR_IMAGENS or BAIXAR_ANEXOS:
            print(f"[{i}/{len(itens)}] {linha.get('Numero de Registro', '')} {linha['Titulo'][:60]}")
            urls, arquivos = baixar_midias(item, linha, pasta_imgs)
            linha["Qtd. arquivos"] = len(arquivos)
            linha["Arquivos baixados"] = " | ".join(arquivos)
            linha["URLs dos arquivos"] = " | ".join(urls)
        linhas.append(linha)
        if i % 50 == 0:
            organizar_colunas(pd.DataFrame(linhas)).to_excel(
                os.path.join(PASTA_SAIDA, ARQUIVO_EXCEL), index=False)
    df = organizar_colunas(pd.DataFrame(linhas))
    caminho_excel = os.path.join(PASTA_SAIDA, ARQUIVO_EXCEL)
    df.to_excel(caminho_excel, index=False)
    print("\n================ PRONTO ================")
    print(f"Obras:     {len(df)}")
    if "Qtd. arquivos" in df.columns:
        print(f"Arquivos:  {int(df['Qtd. arquivos'].sum())} baixados em '{os.path.abspath(pasta_imgs)}'")
        print(f"Sem imagem: {int((df['Qtd. arquivos'] == 0).sum())} obras")
    print(f"Planilha:  {os.path.abspath(caminho_excel)}")

if __name__ == "__main__":
    main()
