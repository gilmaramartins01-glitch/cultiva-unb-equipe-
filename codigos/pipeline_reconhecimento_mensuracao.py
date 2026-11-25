"""
pipeline_reconhecimento_mensuracao.py
Hackathon CULTIVA UnB 2026 — Etapas II (Reconhecimento) e III (Mensuração)

O que faz
    Lê dados/inventario_bruto.csv (extraído da API do Tainacan da CAL/UnB) e gera:
      dados/inventario.csv                          base padronizada nos campos-alvo
      dados/reconhecimento.csv                      matriz de reconhecimento por registro
      dados/mensuracao.csv                          modelo de mensuração por registro
      resultados/indicadores/indicadores.csv        indicadores obrigatórios
      resultados/candidatos_validacao.csv           candidatos à validação aprofundada

Regra de ouro
    O script NÃO atribui valor monetário a nenhum registro. Valor só entra por
    evidência documentada pela equipe em dados/evidencias_mercado.csv (ver
    metodologia/mensuracao.md). Dado ausente permanece como [INFORMAÇÃO PENDENTE].

Dependências: Python 3.9+ e pandas  (pip install pandas)
Execução:     python codigos/pipeline_reconhecimento_mensuracao.py   (a partir da raiz do repositório)
"""
import re
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO — decisões da equipe ficam aqui, visíveis e alteráveis
# ----------------------------------------------------------------------------
ENTRADA = Path("dados/inventario_bruto.csv")
DATA_CONSULTA = "2026-11-23T22:13:07Z"          # data/hora da extração (UTC)
FONTE = "Acervo Digital da CAL/UnB (Tainacan), coleção 'Acervo' (id 1565), API REST pública"

INCLUIR_TRIANGULAR = False                      # decisão da equipe em 23/11/2026
COLECOES_ARTE = ["Arte"]
COLECOES_ETNO = ["Inicial", "Galvão", "Chocó"]  # CNRC não aparece no metadado "Coleção"
COLECAO_CONTEMPORANEA = "Triangular"            # só usada se INCLUIR_TRIANGULAR = True

# Subconjunto "obras contemporâneas" dentro do acervo artístico (regras, item 4.2):
# multimídia, videoarte, instalações, arte postal, obras conceituais e outros suportes.
# Critério operacional: denominação ou técnica/suporte contendo um destes termos.
TERMOS_CONTEMPORANEA = (r"arte digital|performance|perfomance|v[ií]deo|instala|postal|comput|"
                        r"digital|pvc|projetad|animaç|multim|sonor|livro de artista|objeto")

PEND = "[INFORMAÇÃO PENDENTE]"
REF_REC = "NBC TSP Estrutura Conceitual (R1); NBC TSP 37, item 6"
REF_HER = "NBC TSP 37, itens 7 e 77"


def m(nome):
    """Nome da coluna de metadado no inventário bruto."""
    return "meta_" + nome


def ano(texto):
    """Primeiro ano de quatro dígitos encontrado no texto (ou vazio)."""
    achado = re.search(r"(1[89]\d\d|20\d\d)", str(texto))
    return achado.group(1) if achado else ""


# ----------------------------------------------------------------------------
# 1. INVENTÁRIO PADRONIZADO
# ----------------------------------------------------------------------------
def montar_inventario(bruto):
    escopo = COLECOES_ARTE + COLECOES_ETNO + [""]          # "" = registro sem coleção informada
    if INCLUIR_TRIANGULAR:
        escopo.append(COLECAO_CONTEMPORANEA)
    b = bruto[bruto[m("Coleção")].isin(escopo)].copy()

    def categoria(l):
        col = l[m("Coleção")]
        if col in COLECOES_ETNO:
            return "Etnográfica"
        if col == COLECAO_CONTEMPORANEA:
            return "Arte – obra contemporânea"
        if col in COLECOES_ARTE:
            alvo = l["denominacao"] + " " + l[m("Material/Técnica/Suporte")]
            return "Arte – obra contemporânea" if re.search(TERMOS_CONTEMPORANEA, alvo, re.I) else "Arte"
        return "Não classificada (coleção não informada)"

    inv = pd.DataFrame({
        "id_original": b["id_original"],
        "numero_registro": b[m("Número de Registro")],
        "colecao": b[m("Coleção")],
        "categoria": b.apply(categoria, axis=1),
        "denominacao": b["denominacao"],
        "titulo": b[m("Título")],
        "autoria": b[m("Autoria")],
        "grupo_de_origem": b[m("Grupo indígena")],
        "local_producao": b[m("Local de produção")],
        "data_producao": b[m("Data de produção")],
        "tecnica_materiais": b[m("Material/Técnica/Suporte")],
        "dimensoes": b[m("Dimensões")],
        "tiragem": b[m("Tiragem")],
        "procedencia": b[m("Procedência")],
        "forma_aquisicao": b[m("Forma de aquisição")],
        "data_aquisicao": b[m("Data de aquisição")],
        "ano_aquisicao": b[m("Data de aquisição")].map(ano),
        "situacao_localizacao": b[m("Situação")],
        "estado_conservacao": b[m("Estado de conservação")],
        "numero_patrimonio": "",                               # não existe no portal
        "exposicoes": b[m("Exposições")],
        "condicoes_reproducao": b[m("Condições de reprodução")].map(
            lambda t: "Direitos reservados (Lei nº 9.610/1998), conforme o portal" if t else ""),
        "com_imagem": b[m("Com imagem?")],
        "url": b["url"],
        "fonte": FONTE,
        "data_consulta_utc": DATA_CONSULTA,
    })
    return inv.reset_index(drop=True)


# ----------------------------------------------------------------------------
# 2. RECONHECIMENTO
# ----------------------------------------------------------------------------
def reconhecer(l):
    """Aplica as regras de decisão a um registro e devolve as colunas da matriz."""
    sit, forma, proc, data = (l["situacao_localizacao"], l["forma_aquisicao"],
                              l["procedencia"], l["data_aquisicao"])
    etno = l["categoria"] == "Etnográfica"

    # C1 — existência do recurso
    existencia = {
        "Localizado": "Evidenciada: situação 'Localizado' no cadastro",
        "Não localizado": "Não confirmada: situação 'Não localizado' no cadastro",
        "Emprestado": "Evidenciada, mas em empréstimo; o cadastro não informa quem cede e quem recebe",
    }.get(sit, "Não verificável: situação não informada no cadastro")

    # C2 — controle (evidência de aquisição, doação ou transferência)
    faltas = [n for n, v in [("forma de aquisição", forma), ("procedência", proc),
                             ("data de aquisição", data)] if not v]
    if not faltas:
        controle = f"Evento de incorporação documentado: {forma}, origem {proc}, data {data}"
    elif len(faltas) == 3:
        controle = "Sem evidência de aquisição, doação ou transferência no cadastro"
    else:
        controle = "Evidência parcial; falta " + ", ".join(faltas)

    # C3 — potencial de serviços / C4 — benefícios econômicos
    if sit == "Não localizado":
        servicos = "Não exercível enquanto o bem não for localizado"
    elif l["exposicoes"]:
        servicos = "Evidenciado por histórico de exposições no cadastro"
    else:
        servicos = "Presumível pela finalidade museológica (exposição, pesquisa e ensino); sem uso documentado no cadastro"
    economicos = "Não evidenciados; bem mantido pelo potencial de serviços, não para gerar caixa"

    # Investigação adicional
    inv = ["número de patrimônio e termo de incorporação não constam no portal"]
    if forma == "Transferência":
        inv.append("confirmar se a transferência foi de titularidade ou apenas de guarda")
    if sit == "Emprestado":
        inv.append("confirmar a direção e o instrumento do empréstimo")
    if sit == "":
        inv.append("conferência física do bem")
    if faltas:
        inv.append("localizar documento de " + ", ".join(faltas))
    if etno:
        inv.append("verificar restrições de acesso e consulta à comunidade de origem")

    # Regra de decisão — exatamente uma de três categorias
    if sit == "Não localizado":
        classe = "Não reconhecimento fundamentado"
        criterio = "R1: bem cadastrado como 'Não localizado'"
        just = ("Sem evidência atual de existência, a entidade não demonstra recurso controlado nem fluxo provável "
                "de potencial de serviços (item 6(a)). A conclusão vale enquanto o bem não for localizado e não "
                "dispensa a apuração do paradeiro.")
        conclusao = "Não reconhecer; apurar o paradeiro e reavaliar"
    elif sit == "Localizado" and not faltas:
        classe = "Reconhecimento sustentado pelas evidências"
        criterio = "R2: 'Localizado' e incorporação documentada (forma, origem e data)"
        just = ("Existência evidenciada e evento de incorporação identificado sustentam que o bem é recurso controlado "
                "com potencial de serviços (definição de ativo e item 6(a)). O item 6(b), mensuração confiável, é "
                "tratado em mensuracao.csv; enquanto não atendido, aplica-se a divulgação dos itens 7 e 77.")
        conclusao = ("Ativo do patrimônio cultural controlado pela entidade; registro no balanço condicionado à "
                     "mensuração confiável; até lá, divulgação em nota explicativa")
    else:
        classe = "Pendente de verificação"
        motivos = []
        if sit == "":
            motivos.append("existência física não conferida")
        if sit == "Emprestado":
            motivos.append("empréstimo sem identificação de cedente e cessionário")
        if faltas:
            motivos.append("falta " + ", ".join(faltas))
        criterio = "R3: " + "; ".join(motivos)
        just = ("As evidências do cadastro não bastam para concluir sobre existência ou controle. "
                "Constar no portal da CAL não permite presumir controle pela UnB.")
        conclusao = "Sem conclusão; depende da investigação adicional indicada"

    return pd.Series({
        "c1_existencia_do_recurso": existencia,
        "c2_controle_evidencia_de_incorporacao": controle,
        "c3_potencial_de_servicos": servicos,
        "c4_beneficios_economicos": economicos,
        "natureza_e_classificacao": "Ativo imobilizado – bem do patrimônio cultural tangível (acervo museológico)",
        "classificacao": classe,
        "criterio_aplicado": criterio,
        "justificativa": just,
        "conclusao_contabil_proposta": conclusao,
        "investigacao_adicional": "; ".join(inv),
        "restricao_etica": ("Bem de origem em povo indígena ou comunidade tradicional: o reconhecimento não o torna "
                            "mercadoria negociável nem autoriza presunção de livre alienação") if etno else "",
        "referencia_normativa": REF_REC + ("; " + REF_HER if classe.startswith("Reconhecimento") else ""),
    })


# ----------------------------------------------------------------------------
# 3. MENSURAÇÃO (base separada da técnica; nenhum valor é gerado aqui)
# ----------------------------------------------------------------------------
def mensurar(l):
    cat, classe = l["categoria"], l["classificacao"]
    gravura = l["denominacao"].strip().lower() == "gravura"

    # Fatores de comparabilidade (regras, item 9.2) disponíveis no cadastro
    fatores = {"autoria": l["autoria"], "técnica": l["tecnica_materiais"], "dimensões": l["dimensoes"],
               "data de produção": l["data_producao"], "estado de conservação": l["estado_conservacao"]}
    if gravura:
        fatores["tiragem"] = l["tiragem"]
    presentes = [k for k, v in fatores.items() if v]
    ausentes = [k for k, v in fatores.items() if not v]
    indice = len(presentes) / len(fatores)
    grau = ("Alta" if indice >= 0.8 else "Média" if indice >= 0.6 else
            "Baixa" if indice >= 0.3 else "Insuficiente")

    # BASE de mensuração
    if l["forma_aquisicao"] in ("Doação", "Transferência"):
        base_inicial = ("Custo atribuído, por se tratar de aquisição sem contraprestação "
                        "(NBC TSP 37, item 12; NBC TSP 38, itens 10 a 13)")
    else:
        base_inicial = "[INFORMAÇÃO PENDENTE: forma de aquisição não informada; define custo histórico ou custo atribuído]"
    base_corrente = ("Valor corrente operacional, por ser bem mantido pelo potencial de serviços e não para "
                     "retorno financeiro (NBC TSP 37, item 27; NBC TSP 38, itens 23 a 25)")

    # TÉCNICA de estimativa e situação
    if classe == "Não reconhecimento fundamentado":
        tecnica = "Não aplicável"
        situacao = "Não aplicável – não reconhecimento fundamentado"
        just = "Registro não reconhecido; não há objeto de mensuração enquanto o bem não for localizado."
        proximo = "Apurar o paradeiro do bem"
    elif cat == "Etnográfica":
        tecnica = ("Nenhuma técnica aplicável com as evidências disponíveis; eventual avaliação especializada, "
                   "com participação da comunidade de origem")
        situacao = "Impossibilidade de estimativa confiável com as evidências disponíveis"
        just = ("Abordagem de mercado afastada: não há transações comparáveis identificadas e o bem não pode ser "
                "tratado como mercadoria livremente negociável. Abordagem de custo sem base: o cadastro não traz "
                "custo de aquisição nem custo de reposição, e a substituibilidade do objeto é questão cultural a "
                "ser respondida por especialista. Aplica-se a divulgação não financeira (NBC TSP 37, itens 7 e 77).")
        proximo = "Laudo ou avaliação especializada; documento de incorporação; consulta sobre restrições culturais"
    elif cat == "Arte – obra contemporânea":
        tecnica = ("Sem comparáveis diretos identificados; abordagem de custo (NBC TSP 38, itens 43 e 44) apenas "
                   "se houver custo documentado de produção ou reexibição; caso contrário, avaliação especializada")
        situacao = "Impossibilidade de estimativa confiável com as evidências disponíveis"
        just = ("Suporte não convencional (registro de performance, arte digital, impressão sobre suporte sintético "
                "e similares): o cadastro não informa certificado de autenticidade, edição, direitos de exibição e "
                "reprodução, nem condições de conservação do suporte, e não há comparável direto.")
        proximo = ("Certificado de autenticidade e edição; contrato ou termo com direitos associados; "
                   "condição do suporte; custo documentado de produção")
    elif cat == "Arte" and l["autoria"] and l["tecnica_materiais"]:
        tecnica = ("Abordagem de mercado (NBC TSP 38, item 42): transações de obras do mesmo autor e técnica, "
                   "ajustadas por dimensões, tiragem, conservação e data")
        situacao = ("Elegível – pesquisa de comparáveis pendente" if classe.startswith("Reconhecimento")
                    else "Condicionada ao reconhecimento – pesquisa de comparáveis pendente")
        just = ("Autoria e técnica identificadas permitem buscar transações comparáveis. Nenhum valor é atribuído "
                "antes de a equipe documentar as evidências de mercado. Fatores ausentes: "
                + (", ".join(ausentes) if ausentes else "nenhum") + ".")
        proximo = ("Resultados de leilão ou venda efetiva do mesmo autor e técnica; "
                   + ("medição física e " if not l["dimensoes"] else "") + "exame do estado de conservação")
    else:
        tecnica = "Nenhuma técnica aplicável com as evidências disponíveis; avaliação especializada"
        situacao = "Impossibilidade de estimativa confiável com as evidências disponíveis"
        just = "Sem autoria ou técnica identificada no cadastro não há como selecionar comparáveis."
        proximo = "Atribuição de autoria e identificação da técnica por especialista"

    return pd.Series({
        "finalidade_de_manutencao": "Potencial de serviços (exposição, pesquisa e ensino)",
        "base_mensuracao_inicial": base_inicial,
        "base_mensuracao_valor_corrente": base_corrente,
        "tecnica_de_estimativa": tecnica,
        "fatores_comparabilidade_presentes": ", ".join(presentes) if presentes else "nenhum",
        "fatores_comparabilidade_ausentes": ", ".join(ausentes) if ausentes else "nenhum",
        "indice_completude_comparabilidade": round(indice, 2),
        "grau_confiabilidade_das_evidencias": grau,
        "situacao_mensuracao": situacao,
        "valor_estimado": PEND,
        "intervalo_minimo": PEND,
        "intervalo_maximo": PEND,
        "moeda": "BRL",
        "data_base": PEND,
        "natureza_da_evidencia": PEND,
        "fonte_da_evidencia_url": PEND,
        "justificativa": just,
        "proxima_evidencia_necessaria": proximo,
    })


# ----------------------------------------------------------------------------
# 4. EXECUÇÃO
# ----------------------------------------------------------------------------
def main():
    bruto = pd.read_csv(ENTRADA, sep=";", dtype=str, keep_default_na=False)
    inv = montar_inventario(bruto)

    rec = pd.concat([inv[["id_original", "numero_registro", "colecao", "categoria", "denominacao", "url"]],
                     inv.apply(reconhecer, axis=1)], axis=1)
    base = inv.merge(rec[["id_original", "classificacao"]], on="id_original")
    men = pd.concat([base[["id_original", "numero_registro", "colecao", "categoria", "denominacao",
                           "autoria", "tecnica_materiais", "classificacao", "url"]],
                     base.apply(mensurar, axis=1)], axis=1).rename(
                         columns={"classificacao": "classificacao_reconhecimento"})

    # Candidatos à validação aprofundada: registros reconhecidos, mais completos primeiro
    # (os não reconhecidos ficam de fora; os pendentes entram depois dos sustentados)
    cand = men[men["classificacao_reconhecimento"] != "Não reconhecimento fundamentado"].copy()
    cand["_sust"] = cand["classificacao_reconhecimento"].str.startswith("Reconhecimento")
    cand = cand.sort_values(["categoria", "_sust", "indice_completude_comparabilidade"],
                            ascending=[True, False, False])
    cand = cand.groupby("categoria").head(8)[
        ["categoria", "numero_registro", "denominacao", "autoria", "tecnica_materiais",
         "classificacao_reconhecimento",
         "fatores_comparabilidade_presentes", "indice_completude_comparabilidade", "situacao_mensuracao", "url"]]

    # Indicadores obrigatórios (regras, item 15)
    campos = ["numero_registro", "colecao", "denominacao", "tecnica_materiais", "dimensoes", "procedencia",
              "forma_aquisicao", "data_aquisicao", "situacao_localizacao", "estado_conservacao", "data_producao"]
    completude = (inv[campos] != "").mean().mean()
    n = len(inv)
    cont = rec["classificacao"].value_counts()
    ind = [
        ("Registros públicos identificados na coleção 'Acervo'", len(bruto)),
        ("Registros recuperados", len(bruto)),
        ("Cobertura sobre o universo público identificável (%)", 100.0),
        ("Registros no escopo desta análise", n),
        ("Registros fora do escopo por decisão da equipe (Triangular)", len(bruto) - n),
        ("Completude cadastral média de 11 campos principais (%)", round(100 * completude, 1)),
        ("Registros duplicados (por número de registro)", int(inv["numero_registro"].duplicated().sum())),
        ("Reconhecimento sustentado pelas evidências", int(cont.get("Reconhecimento sustentado pelas evidências", 0))),
        ("Não reconhecimento fundamentado", int(cont.get("Não reconhecimento fundamentado", 0))),
        ("Reconhecimento pendente de verificação", int(cont.get("Pendente de verificação", 0))),
        ("Mensuração fundamentada", 0),
        ("Mensuração pendente (elegível ou condicionada, aguardando comparáveis)",
         int(men["situacao_mensuracao"].str.contains("pendente").sum())),
        ("Impossibilidade de estimativa confiável com as evidências disponíveis",
         int(men["situacao_mensuracao"].str.startswith("Impossibilidade").sum())),
        ("Valor agregado estimado", "Não aplicável: nenhum registro com mensuração fundamentada"),
        ("Rastreabilidade: registros com URL, fonte e decisão documentada (%)",
         round(100 * ((inv["url"] != "") & (rec["criterio_aplicado"] != "")).mean(), 1)),
        ("Casos validados em profundidade", 0),
    ]

    # Gravação: dado ausente vira [INFORMAÇÃO PENDENTE]
    inv_saida = inv.replace("", PEND)
    inv_saida["numero_patrimonio"] = "[INFORMAÇÃO PENDENTE: campo inexistente no portal]"
    Path("resultados/indicadores").mkdir(parents=True, exist_ok=True)
    op = dict(sep=";", index=False, encoding="utf-8-sig")
    inv_saida.to_csv("dados/inventario.csv", **op)
    rec.to_csv("dados/reconhecimento.csv", **op)
    men.to_csv("dados/mensuracao.csv", **op)
    cand.to_csv("resultados/candidatos_validacao.csv", **op)
    pd.DataFrame(ind, columns=["indicador", "valor"]).to_csv("resultados/indicadores/indicadores.csv", **op)

    print(f"Registros no escopo: {n}")
    print(pd.crosstab(rec["categoria"], rec["classificacao"], margins=True).to_string())
    print(pd.crosstab(men["categoria"], men["situacao_mensuracao"], margins=True).to_string())


if __name__ == "__main__":
    main()
