"""
mensuracao_224.py — Hackathon CULTIVA UnB 2026, etapa III (Mensuração) e quadro da etapa IV
Versão de 25/11/2026, com as correções decididas pela equipe na revisão dessa data.

O que faz
  1. Lê o inventário e a matriz de reconhecimento do cenário A (dados/reconhecimento.csv, gerada
     por reconhecimento_cenario_a.py) e separa os 224 registros com reconhecimento sustentado.
  2. Classifica cada registro em um grupo de mensuração (lote = mesmo autor + mesma técnica).
  3. Aplica a abordagem de mercado SOMENTE a lotes com no mínimo 3 vendas realizadas (arremates)
     de 2019 em diante. Preço = martelo + comissão do comprador lida no edital. Atualização pelo
     IPCA (BCB, SGS 433) do mês seguinte ao da venda até o mês da data-base.
  4. Grava mensuracao.csv, evidencias_mercado.csv, quadro_demonstrativo.csv e
     indicadores_mensuracao.csv.

O que NÃO faz
  - Não usa preço de oferta, anúncio ou lance inicial para formar valor.
  - Não atribui valor em reais a objetos etnográficos.
  - Não trata valor escriturado no SIPAC como mensuração: ele aparece só como informação.
  - Não gera nenhum valor: todos os preços vêm das evidências listadas em EVIDENCIAS, conferidas
    pela equipe.

Execução (a partir da raiz do repositório; só biblioteca padrão do Python 3.8+):
    python codigos/reconhecimento_cenario_a.py
    python codigos/mensuracao_224.py
Entradas: dados/inventario.csv e dados/reconhecimento.csv.
Saídas:   dados/mensuracao.csv, dados/evidencias_mercado.csv,
          resultados/quadro_demonstrativo.csv, resultados/indicadores_mensuracao.csv
"""
import csv
from collections import OrderedDict
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parent.parent
PEND = "[INFORMAÇÃO PENDENTE]"
DATA_BASE = "10/2026"          # último mês do IPCA usado na atualização
MINIMO_VENDAS = 3              # critério da equipe, para permitir mediana e faixa
ANO_MINIMO = 2019              # só vendas realizadas de 2019 em diante

# IPCA mensal em % (Banco Central do Brasil, SGS série 433), consultado em 25/11/2026 em
# https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json
IPCA = {
    "09/2023": 0.26, "10/2023": 0.24, "11/2023": 0.28, "12/2023": 0.56,
    "01/2024": 0.42, "02/2024": 0.83, "03/2024": 0.16, "04/2024": 0.38, "05/2024": 0.46, "06/2024": 0.21,
    "07/2024": 0.38, "08/2024": -0.02, "09/2024": 0.44, "10/2024": 0.56, "11/2024": 0.39, "12/2024": 0.52,
    "01/2025": 0.16, "02/2025": 1.31, "03/2025": 0.56, "04/2025": 0.43, "05/2025": 0.26, "06/2025": 0.24,
    "07/2025": 0.26, "08/2025": -0.11, "09/2025": 0.48, "10/2025": 0.09, "11/2025": 0.18, "12/2025": 0.33,
    "01/2026": 0.33, "02/2026": 0.70, "03/2026": 0.88, "04/2026": 0.67, "05/2026": 0.58, "06/2026": 0.16,
    "07/2026": 0.07, "08/2026": -0.32, "09/2026": 0.82, "10/2026": 0.14,
}

# Evidências de mercado. Cada linha é uma evidência conferida pela equipe na página indicada.
# Ofertas, anúncios e vendas sem endereço verificável não são listados (decisão da equipe em 25/11/2026).
# natureza: "Venda realizada (arremate)" é a única que pode entrar no cálculo.
EVIDENCIAS = [
    dict(lote="Tarsila do Amaral – gravura em metal", obra="Crianças no vilarejo, gravura em metal, P/A, 16x16 cm",
         casa="Acervo Leilões", leilao="37397", lote_leilao="108", data="30/08/2023", martelo=1600.00, comissao=0.05,
         natureza="Venda realizada (arremate)", url="https://acervoleiloes.com.br/peca.asp?ID=18264246",
         diferencas="Prova de artista; dimensões bem menores que as demais"),
    dict(lote="Tarsila do Amaral – gravura em metal", obra="Anjos (1972), gravura em metal, 45/100, 53x42 cm",
         casa="Acervo Leilões", leilao="38749", lote_leilao="214", data="27/10/2023", martelo=7000.00, comissao=0.05,
         natureza="Venda realizada (arremate)", url="https://acervoleiloes.com.br/peca.asp?ID=18901735",
         diferencas="Comparável mais próximo: série de 1972, tiragem de 100"),
    dict(lote="Tarsila do Amaral – gravura em metal", obra="Carnaval em Madureira, gravura em metal, prova de estado II, 58x38 cm",
         casa="Acervo Leilões", leilao="49334", lote_leilao="100", data="22/01/2025", martelo=7900.00, comissao=0.05,
         natureza="Venda realizada (arremate)", url="https://acervoleiloes.com.br/peca.asp?ID=24190524",
         diferencas="Prova de estado, fora da tiragem numerada"),
]

# Valores apenas informativos (não entram em nenhum total de valor fundamentado)
SANCHEZ_INDICATIVO = dict(valor=18591.70, faixa_min=14478.41, faixa_max=22704.99, vendas=2,
                          fonte="Relatório de mensuração da equipe (24/11/2026)",
                          alerta="2 vendas realizadas, abaixo do mínimo de 3; vendas da edição de 2020 e a obra da CAL é de 1993")
SIPAC_NAVARRO = "8.050,00 para o conjunto de 81 bens (não rateado por obra; não confirmado)"
SIPAC_CAL1000 = 100.00


def fator_ipca(data_venda):
    """Acumula o IPCA do mês seguinte ao da venda até DATA_BASE (convenção documentada no memorial)."""
    _, mes, ano = data_venda.split("/")
    mes, ano = int(mes), int(ano)
    mf, af = (int(x) for x in DATA_BASE.split("/"))
    fator = 1.0
    while (ano, mes) < (af, mf):
        mes += 1
        if mes == 13:
            mes, ano = 1, ano + 1
        fator *= 1 + IPCA[f"{mes:02d}/{ano}"] / 100
    return fator


def ler(nome):
    p = RAIZ / "dados" / nome
    if not p.exists():
        raise SystemExit(f"Arquivo não encontrado: dados/{nome}")
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def gravar(caminho, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(linhas)


def br(v):
    return "" if v is None else f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def grupo(o):
    """Grupo de mensuração de um registro reconhecido."""
    if o["categoria"] == "Etnográfica":
        return "Objetos etnográficos (Coleção Inicial)"
    autor, tec = o["autoria"], o["tecnica_materiais"].lower()
    if autor == PEND or o["tecnica_materiais"] == PEND:
        return "Cadastro incompleto"
    metal = "água-forte" in tec or "gravura em metal" in tec   # água-forte é técnica de gravura em metal
    if autor == "Zeila Navarro Swain":
        return "Zeila Navarro Swain (doação de 2008)"
    if autor == "Tarsila do Amaral":
        return "Tarsila do Amaral – gravura em metal" if metal else "Tarsila do Amaral – serigrafia (CAL.1198)"
    if autor == "Maciej Babinski" and metal:
        return "Maciej Babinski – gravura em metal"
    if autor == "Milan Dusek":
        return "Milan Dusek – gravuras"
    if autor == "Tomás Sánches":
        return "Tomás Sánchez – serigrafia (CAL.1208)"
    if o["numero_registro"] == "CAL.1000":
        return "Johann Georg Scheuermann – desenho (CAL.1000)"
    return "Demais obras de arte"


def main():
    inv = {x["id_original"]: x for x in ler("inventario.csv")}
    rec = ler("reconhecimento.csv")
    # Cenário A (conservador): registros sustentados em dados/reconhecimento.csv (gerado por reconhecimento_cenario_a.py)
    obras = [inv[r["id_original"]] for r in rec
             if r["classificacao"].startswith("Reconhecimento sustentado")]
    assert len(obras) == 224, f"Esperados 224 registros reconhecidos; encontrados {len(obras)}"

    # --- Evidências: preço com comissão, atualização e uso no cálculo
    ev_saida, por_lote = [], {}
    for e in EVIDENCIAS:
        realizada = e["natureza"] == "Venda realizada (arremate)"
        completa = realizada and e["martelo"] is not None and e["comissao"] is not None and e["data"].count("/") == 2
        no_periodo = completa and int(e["data"][-4:]) >= ANO_MINIMO
        preco = round(e["martelo"] * (1 + e["comissao"]), 2) if completa else None
        atual = round(preco * fator_ipca(e["data"]), 2) if no_periodo else None
        if no_periodo:
            por_lote.setdefault(e["lote"], []).append(atual)
        ev_saida.append(dict(e, _preco=preco, _atual=atual, _candidata=no_periodo))
    lotes_ok = {l: v for l, v in por_lote.items() if len(v) >= MINIMO_VENDAS}
    evid = []
    for e in ev_saida:
        usada = e["_candidata"] and e["lote"] in lotes_ok
        evid.append(OrderedDict(
            lote=e["lote"], obra_comparavel=e["obra"], casa=e["casa"], leilao=e["leilao"], lote_do_leilao=e["lote_leilao"],
            data=e["data"], natureza_evidencia=e["natureza"], martelo_rs=br(e["martelo"]),
            comissao_comprador="" if e["comissao"] is None else f'{e["comissao"]:.0%}',
            preco_com_comissao_rs=br(e["_preco"]), atualizado_ipca_ate=DATA_BASE if e["_atual"] else "",
            valor_atualizado_rs=br(e["_atual"]), usada_no_calculo="Sim" if usada else "Não",
            diferencas_para_o_bem=e["diferencas"], url=e["url"], data_consulta="25/11/2026"))
    gravar(RAIZ / "dados" / "evidencias_mercado.csv", evid)

    # --- Mensuração por registro
    BASE = "Custo atribuído na entrada (aquisição sem contraprestação); valor corrente operacional na mensuração subsequente"
    linhas = []
    for o in sorted(obras, key=lambda x: x["numero_registro"]):
        g = grupo(o)
        m = dict(tecnica="Não aplicada", situacao="", valor=None, fmin=None, fmax=None, conf="", indic="", escrit="",
                 n="", just="", prox="")
        if g in lotes_ok:
            v = lotes_ok[g]
            m.update(tecnica="Abordagem de mercado por lote (autor + técnica)",
                     situacao="Mensuração fundamentada – abordagem de mercado por lote (mínimo atingido)",
                     valor=round(median(v), 2), fmin=min(v), fmax=max(v), conf="Baixa", n=len(v),
                     just="Mediana de 3 vendas realizadas (martelo + 5% de comissão), atualizadas pelo IPCA. Todas de uma única "
                          "casa de leilões; sem ajuste por tiragem e dimensões, que o portal não informa.",
                     prox="Medir as obras, registrar tiragem e ampliar o número de vendas comparáveis")
        elif g.startswith("Tomás Sánchez"):
            s = SANCHEZ_INDICATIVO
            m.update(situacao="Valor indicativo (não fundamentado)", indic=br(s["valor"]), fmin=s["faixa_min"], fmax=s["faixa_max"],
                     conf="Insuficiente", n=s["vendas"], just=s["alerta"] + ". Fonte: " + s["fonte"] + ".",
                     prox="Localizar ao menos mais uma venda realizada do mesmo autor e técnica")
        elif g.startswith("Maciej Babinski"):
            m.update(situacao="Pendente – evidência insuficiente", n=1,
                     just="Só foram encontradas ofertas e 1 venda realizada desde 2019 (R$ 300,00 em 2021). Abaixo do mínimo de 3 vendas.",
                     prox="Localizar vendas realizadas de gravuras em metal do autor")
        elif g.startswith("Milan Dusek"):
            m.update(situacao="Pendente – evidência insuficiente", n=0, just="Nenhuma venda realizada localizada.",
                     prox="Laudo de especialista ou vendas realizadas do autor")
        elif g.startswith("Tarsila do Amaral – serigrafia"):
            m.update(situacao="Pendente – evidência insuficiente", n=0,
                     just="Desde 2019 só foi localizada a venda de um álbum de 4 pranchas, não comparável a uma serigrafia avulsa.",
                     prox="Localizar vendas realizadas de serigrafias avulsas da autora")
        elif g == "Demais obras de arte":
            m.update(situacao="Pendente – evidência insuficiente", n=0,
                     just="Autor com uma ou duas obras no conjunto; nenhum lote alcançou 3 vendas realizadas.",
                     prox="Vendas realizadas do mesmo autor e técnica ou laudo de especialista")
        elif g.startswith("Zeila"):
            m.update(situacao="Pendente – valor escriturado apenas informativo", escrit=SIPAC_NAVARRO, n=0,
                     just="Sem mercado observável. O valor escriturado no SIPAC para o conjunto é administrativo, não é custo histórico "
                          "documentado e não foi confirmado: o processo de doação de 2008 não foi localizado.",
                     prox="Processo de doação de 2008 e laudo de especialista para o conjunto")
        elif g.startswith("Johann"):
            m.update(situacao="Pendente – valor escriturado apenas informativo", escrit=br(SIPAC_CAL1000), n=0,
                     just="Valor escriturado no SIPAC (administrativo, uniforme para os bens do mesmo ato). Não é mensuração.",
                     prox="Laudo de especialista")
        elif g == "Cadastro incompleto":
            m.update(situacao="Pendente – cadastro incompleto", just="Sem autoria ou sem técnica no cadastro; não há lote a formar.",
                     prox="Consulta à CAL para completar o cadastro")
        else:
            m.update(tecnica="Nenhuma em dinheiro (divulgação não financeira)", situacao="Não monetária – objeto etnográfico",
                     just="Objeto de comunidade tradicional: a equipe não atribui valor em reais, por limite ético e por não haver "
                          "mercado legítimo nem custo de reposição.",
                     prox="Descrição, povo de origem e relevância cultural na nota explicativa")
        linhas.append(OrderedDict(
            numero_registro=o["numero_registro"], colecao=o["colecao"], categoria=o["categoria"], denominacao=o["denominacao"],
            autoria=o["autoria"], grupo_de_origem=o["grupo_de_origem"], tecnica_materiais=o["tecnica_materiais"],
            procedencia=o["procedencia"], forma_aquisicao=o["forma_aquisicao"], data_aquisicao=o["data_aquisicao"],
            grupo_mensuracao=g, base_mensuracao=BASE, tecnica_de_estimativa=m["tecnica"], situacao_mensuracao=m["situacao"],
            valor_fundamentado_rs=br(m["valor"]), faixa_minima_rs=br(m["fmin"]), faixa_maxima_rs=br(m["fmax"]),
            data_base=DATA_BASE if m["valor"] else "", grau_confiabilidade=m["conf"], vendas_realizadas_no_lote=m["n"],
            valor_indicativo_nao_fundamentado_rs=m["indic"], valor_escriturado_sipac_informativo=m["escrit"],
            justificativa=m["just"], proxima_evidencia_necessaria=m["prox"], url=o["url"], fonte=o["fonte"]))
    gravar(RAIZ / "dados" / "mensuracao.csv", linhas)

    # --- Quadro demonstrativo por grupo
    ordem = ["Tarsila do Amaral – gravura em metal", "Tarsila do Amaral – serigrafia (CAL.1198)",
             "Tomás Sánchez – serigrafia (CAL.1208)", "Maciej Babinski – gravura em metal", "Milan Dusek – gravuras",
             "Demais obras de arte", "Zeila Navarro Swain (doação de 2008)", "Johann Georg Scheuermann – desenho (CAL.1000)",
             "Cadastro incompleto", "Objetos etnográficos (Coleção Inicial)"]
    quadro, tot_reg, tot_val = [], 0, 0.0
    for g in ordem:
        ls = [l for l in linhas if l["grupo_mensuracao"] == g]
        val = round(sum(float(l["valor_fundamentado_rs"].replace(".", "").replace(",", ".")) for l in ls if l["valor_fundamentado_rs"]), 2)
        tot_reg += len(ls); tot_val += val
        quadro.append(OrderedDict(
            grupo=g, registros=len(ls), situacao=ls[0]["situacao_mensuracao"],
            valor_corrente_fundamentado_rs=br(val) if val else "",
            valor_por_obra_rs=ls[0]["valor_fundamentado_rs"],
            faixa_por_obra_rs=(ls[0]["faixa_minima_rs"] + " a " + ls[0]["faixa_maxima_rs"]) if ls[0]["faixa_minima_rs"] else "",
            grau_confiabilidade=ls[0]["grau_confiabilidade"],
            informacao_nao_somada=(("Valor indicativo: " + ls[0]["valor_indicativo_nao_fundamentado_rs"]) if ls[0]["valor_indicativo_nao_fundamentado_rs"]
                                   else ("Escriturado no SIPAC: " + ls[0]["valor_escriturado_sipac_informativo"]) if ls[0]["valor_escriturado_sipac_informativo"] else "")))
    assert tot_reg == 224
    quadro.append(OrderedDict(grupo="TOTAL (o valor refere-se só às 9 gravuras de Tarsila; não é o valor do acervo da CAL)",
                              registros=tot_reg, situacao="", valor_corrente_fundamentado_rs=br(tot_val), valor_por_obra_rs="",
                              faixa_por_obra_rs="", grau_confiabilidade="", informacao_nao_somada=""))
    gravar(RAIZ / "resultados" / "quadro_demonstrativo.csv", quadro)

    # --- Indicadores
    def n(prefixo):
        return sum(1 for l in linhas if l["situacao_mensuracao"].startswith(prefixo))
    fund = [l for l in linhas if l["valor_fundamentado_rs"]]
    v1 = float(fund[0]["valor_fundamentado_rs"].replace(".", "").replace(",", "."))
    fmin = float(fund[0]["faixa_minima_rs"].replace(".", "").replace(",", "."))
    fmax = float(fund[0]["faixa_maxima_rs"].replace(".", "").replace(",", "."))
    ind = [
        ("Registros com reconhecimento sustentado (cenário A)", 224),
        ("Mensuração fundamentada pelo valor corrente operacional (registros)", len(fund)),
        ("Mensuração fundamentada pelo valor corrente operacional (R$)", br(tot_val)),
        ("Faixa do valor fundamentado, pelo menor e pelo maior comparável (R$)", f"{br(fmin*len(fund))} a {br(fmax*len(fund))}"),
        ("Valor por obra do lote fundamentado, mediana (R$)", br(v1)),
        ("Data-base da atualização pelo IPCA", DATA_BASE),
        ("Valor indicativo, não fundamentado (registros)", n("Valor indicativo")),
        ("Mensuração pendente – evidência insuficiente (registros)", n("Pendente – evidência")),
        ("Mensuração pendente – valor escriturado apenas informativo (registros)", n("Pendente – valor escriturado")),
        ("Mensuração pendente – cadastro incompleto (registros)", n("Pendente – cadastro")),
        ("Mensuração pendente, total (registros)", n("Pendente")),
        ("Não monetária, objetos etnográficos (registros)", n("Não monetária")),
        ("Registros reconhecidos sem mensuração fundamentada", 224 - len(fund)),
        ("Mensuração fundamentada sobre os reconhecidos (%)", f"{100*len(fund)/224:.1f}".replace(".", ",")),
        ("Evidências de mercado registradas / usadas no cálculo", f'{len(evid)} / {sum(1 for e in evid if e["usada_no_calculo"]=="Sim")}'),
        ("Valor escriturado no SIPAC tratado como mensuração (registros)", 0),
    ]
    gravar(RAIZ / "resultados" / "indicadores_mensuracao.csv", [OrderedDict(indicador=a, valor=b) for a, b in ind])

    for a, b in ind:
        print(f"{a}: {b}")
    for e in evid:
        if e["usada_no_calculo"] == "Sim":
            print("  usada:", e["obra_comparavel"], "->", e["valor_atualizado_rs"])


if __name__ == "__main__":
    main()
