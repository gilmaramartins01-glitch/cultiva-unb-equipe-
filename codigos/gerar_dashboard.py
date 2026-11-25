"""
gerar_dashboard.py — Hackathon CULTIVA UnB 2026, etapa V (Solução tecnológica)
Versão de 25/11/2026, com as correções decididas pela equipe na revisão dessa data.

Gera resultados/dashboard.html: página única, sem servidor e sem bibliotecas externas, com os dados
embutidos. Basta abrir o arquivo no navegador.

Entradas (geradas por codigos/mensuracao_224.py):
    dados/mensuracao.csv, dados/evidencias_mercado.csv,
    resultados/quadro_demonstrativo.csv, resultados/indicadores_mensuracao.csv
Os totais de identificação e reconhecimento ficam no bloco CONFIG, porque vêm do pipeline de
reconhecimento da equipe (cenário A, 24/11/2026). Ao rodar aquele pipeline de novo, atualize CONFIG.

Execução: python codigos/reconhecimento_cenario_a.py && python codigos/mensuracao_224.py && python codigos/gerar_dashboard.py
"""
import csv
import html
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CONFIG = {
    "data_base": "25/11/2026",
    "funil": [
        ["Registros públicos no portal", 1497, "Coleção \"Acervo\" do Tainacan da CAL; há ainda 129 privados e 1 rascunho, inacessíveis"],
        ["Universo analisado", 1335, "Sem a Coleção Triangular (162), por decisão da equipe"],
        ["Existência confirmada", 488, "Situação \"Localizado\" no portal"],
        ["Reconhecimento sustentado", 224, "Localizado, com aquisição documentada e controle além da guarda (cenário A, conservador)"],
        # a última etapa é preenchida com o indicador calculado
    ],
    # coleção: [sustentado, pendente, não reconhecido]
    "reconhecimento": [["Arte", 159, 316, 0], ["Inicial", 65, 266, 18], ["Galvão", 0, 347, 0], ["Chocó", 0, 163, 0],
                       ["Sem coleção", 0, 1, 0]],
    "pendencias": [["Existência física não conferida", 798], ["Aquisição não documentada", 135],
                   ["Transferência sem registro patrimonial (Galvão)", 129],
                   ["Catálogo diz \"não localizado\", SIPAC diz \"em uso\"", 21], ["Empréstimo sem documento", 10]],
    "limitacoes": [
        "Valor fundamentado só para 9 gravuras de Tarsila, com 3 vendas de uma única casa de leilões.",
        "Sem ajuste por tiragem e dimensões: o portal não informa esses dados para as obras da CAL.",
        "Confiabilidade baixa: a faixa entre o menor e o maior comparável é larga, e um deles (16x16 cm) é bem menor.",
        "Preços de oferta, anúncio e lance inicial não formam valor.",
        "Valores escriturados no SIPAC são administrativos e aparecem só como informação; o processo de doação de 2008 não foi localizado.",
        "Objetos etnográficos não recebem valor em reais.",
        "A Coleção Triangular ficou fora; nenhuma obra contemporânea está entre os 224 reconhecidos.",
        "Cobertura do acervo digital público, não do acervo físico. Exercício acadêmico: não é registro contábil da UnB nem o valor do patrimônio cultural da CAL.",
    ],
}


def ler(rel):
    with open(RAIZ / rel, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def e(s):
    return html.escape(str(s))


def main():
    ind = {x["indicador"]: x["valor"] for x in ler("resultados/indicadores_mensuracao.csv")}
    quadro = ler("resultados/quadro_demonstrativo.csv")
    evid = ler("dados/evidencias_mercado.csv")
    n_fund = int(ind["Mensuração fundamentada pelo valor corrente operacional (registros)"])
    valor = ind["Mensuração fundamentada pelo valor corrente operacional (R$)"]
    faixa = ind["Faixa do valor fundamentado, pelo menor e pelo maior comparável (R$)"]
    n_ind = int(ind["Valor indicativo, não fundamentado (registros)"])
    analisados = CONFIG["funil"][1][1]
    reconhecidos = CONFIG["funil"][3][1]
    funil = CONFIG["funil"] + [["Com mensuração fundamentada", n_fund,
                               "Lote com no mínimo 3 vendas realizadas (arremates) desde 2019"]]

    cartoes = [
        (f"{analisados:,}".replace(",", "."), "registros analisados", "Universo público, sem a Triangular"),
        (str(reconhecidos), "registros reconhecidos", "Cenário A, conservador"),
        (str(n_fund), "com mensuração fundamentada", "Gravuras em metal de Tarsila do Amaral"),
        ("R$ " + valor, "valor corrente fundamentado (Tarsila)", f"Faixa: R$ {faixa}. Não é o valor do acervo."),
    ]
    h_cart = "".join(f'<div class="card"><div class="num">{e(a)}</div><div class="lab">{e(b)}</div><div class="sub">{e(c)}</div></div>'
                     for a, b, c in cartoes)

    topo = funil[0][1]
    h_funil = "".join(
        f'<div class="row" title="{e(d)}"><div class="rl">{e(n)}</div>'
        f'<div class="track"><div class="bar" style="width:{max(100*v/topo, 0.6):.2f}%"></div><span class="val">{v:,}</span></div></div>'.replace(",", ".")
        for n, v, d in funil)
    por100_rec = 100 * reconhecidos / analisados
    por100_fund = 100 * n_fund / analisados
    txt_funil = (f"De cada 100 registros analisados, cerca de {por100_rec:.0f} têm reconhecimento sustentado e menos de 1 "
                 f"({por100_fund:.2f}".replace(".", ",") + ") chega a uma mensuração fundamentada. "
                 f"Fora do funil: com valor indicativo (não fundamentado): {n_ind} (Sánchez), que não entra em nenhum total.")

    tot = max(sum(r[1:]) for r in CONFIG["reconhecimento"])
    h_rec = ""
    for nome, s, p, nr in CONFIG["reconhecimento"]:
        seg = "".join(f'<div class="seg {c}" style="width:{100*v/tot:.2f}%" title="{e(nome)} – {t}: {v}"></div>'
                      for v, c, t in ((s, "s1", "sustentado"), (p, "s2", "pendente"), (nr, "s3", "não reconhecido")) if v)
        h_rec += (f'<div class="row"><div class="rl">{e(nome)}</div><div class="track stack">{seg}'
                  f'<span class="val">{s} · {p} · {nr}</span></div></div>')

    h_pend = "".join(f"<tr><td>{e(a)}</td><td class='r'>{b}</td></tr>" for a, b in CONFIG["pendencias"])
    h_quadro = "".join(
        f"<tr{' class=tot' if q['grupo'].startswith('TOTAL') else ''}><td>{e(q['grupo'])}</td><td class='r'>{e(q['registros'])}</td>"
        f"<td>{e(q['situacao'])}</td><td class='r'>{e(q['valor_corrente_fundamentado_rs'])}</td><td>{e(q['faixa_por_obra_rs'])}</td>"
        f"<td>{e(q['informacao_nao_somada'])}</td></tr>" for q in quadro)
    h_evid = "".join(
        f"<tr><td>{e(v['lote'])}</td><td>{e(v['obra_comparavel'])}</td><td>{e(v['casa'])}</td><td>{e(v['data'])}</td>"
        f"<td>{e(v['natureza_evidencia'])}</td><td class='r'>{e(v['valor_atualizado_rs'])}</td>"
        f"<td>{'<b>Sim</b>' if v['usada_no_calculo']=='Sim' else 'Não'}</td>"
        f"<td>{('<a href=%s>abrir</a>' % e(v['url'])) if v['url'].startswith('http') else e(v['diferencas_para_o_bem'])}</td></tr>"
        for v in evid)
    h_lim = "".join(f"<li>{e(x)}</li>" for x in CONFIG["limitacoes"])

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Painel – Patrimônio cultural da CAL/UnB</title>
<style>
:root{{--bg:#f9f9f9;--sf:#fff;--tx:#191919;--t2:#666;--gr:#e7e7e7;--s1:#257de0;--s2:#c2c2c2;--s3:#f47230}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0b0b0b;--sf:#191919;--tx:#efefef;--t2:#9c9c9c;--gr:#303030;--s1:#338ced;--s2:#5a5a5a;--s3:#e76624}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:24px;margin:0 0 4px}}h2{{font-size:17px;margin:0 0 12px}}
.aviso{{color:var(--t2);margin:0 0 20px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:16px}}
.card,section{{background:var(--sf);border:1px solid var(--gr);border-radius:10px;padding:16px}}section{{margin-bottom:16px}}
.num{{font-size:28px;font-weight:650}}.lab{{font-weight:600}}.sub{{color:var(--t2);font-size:13px}}
.row{{display:grid;grid-template-columns:230px 1fr;gap:12px;align-items:center;margin:6px 0}}.rl{{font-size:14px}}
.track{{position:relative;height:22px;display:flex;align-items:center;gap:2px}}.bar{{height:14px;background:var(--s1);border-radius:0 4px 4px 0}}
.seg{{height:14px}}.seg:last-of-type{{border-radius:0 4px 4px 0}}.s1{{background:var(--s1)}}.s2{{background:var(--s2)}}.s3{{background:var(--s3)}}
.val{{margin-left:8px;font-size:13px;color:var(--tx);font-variant-numeric:tabular-nums;white-space:nowrap}}
.leg{{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--t2);margin-bottom:8px}}.leg i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:13.5px}}th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--gr);vertical-align:top}}
th{{color:var(--t2);font-weight:600}}.r{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}.tot td{{font-weight:650}}
p.t{{color:var(--t2);margin:10px 0 0}}a{{color:var(--s1)}}ul{{margin:0;padding-left:20px}}
@media (max-width:640px){{.row{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Patrimônio cultural da CAL/UnB: do registro à mensuração</h1>
<p class="aviso">Hackathon CULTIVA UnB 2026 · posição em {CONFIG['data_base']} · exercício acadêmico; não é registro contábil da UnB nem o valor total do patrimônio cultural da CAL.</p>
<div class="cards">{h_cart}</div>
<section><h2>Onde os registros param</h2>{h_funil}<p class="t">{e(txt_funil)}</p></section>
<section><h2>Reconhecimento por coleção</h2>
<div class="leg"><span><i class="s1"></i>Sustentado</span><span><i class="s2"></i>Pendente de verificação</span><span><i class="s3"></i>Não reconhecimento fundamentado</span></div>
{h_rec}<p class="t">Os números ao lado de cada barra seguem a ordem da legenda.</p></section>
<section><h2>Por que {sum(b for _, b in CONFIG['pendencias']):,} registros ficaram pendentes</h2><div class="tw"><table><tr><th>Motivo</th><th class="r">Registros</th></tr>{h_pend}</table></div></section>
<section><h2>Mensuração dos 224 reconhecidos</h2><div class="tw"><table>
<tr><th>Grupo</th><th class="r">Registros</th><th>Situação</th><th class="r">Valor corrente fundamentado (R$)</th><th>Faixa por obra (R$)</th><th>Informação não somada</th></tr>{h_quadro}</table></div>
<p class="t">Base: valor corrente operacional. Técnica: abordagem de mercado por lote (mesmo autor e mesma técnica), com no mínimo 3 vendas realizadas desde 2019; preço = martelo + comissão do comprador; atualização pelo IPCA até {e(ind['Data-base da atualização pelo IPCA'])}.</p></section>
<section><h2>Vendas usadas no cálculo</h2><div class="tw"><table>
<tr><th>Lote</th><th>Evidência</th><th>Casa</th><th>Data</th><th>Natureza</th><th class="r">Atualizado (R$)</th><th>Usada</th><th>Fonte ou motivo</th></tr>{h_evid}</table></div></section>
<section><h2>Limitações</h2><ul>{h_lim}</ul></section>
</main></body></html>"""
    pagina = pagina.replace(f"{sum(b for _, b in CONFIG['pendencias']):,}", f"{sum(b for _, b in CONFIG['pendencias']):,}".replace(",", "."))
    saida = RAIZ / "resultados" / "dashboard.html"
    saida.write_text(pagina, encoding="utf-8")
    print("Gerado:", saida.relative_to(RAIZ))


if __name__ == "__main__":
    main()
