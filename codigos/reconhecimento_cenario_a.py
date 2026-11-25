"""
reconhecimento_cenario_a.py — Hackathon CULTIVA UnB 2026, etapa II (Reconhecimento)
Versão de 25/11/2026.

Aplica o cenário A (conservador), decidido pela equipe em 24/11/2026, sobre a matriz gerada pela
regra inicial de 23/11 (dados/reconhecimento_regra_23nov.csv, saída do
pipeline_reconhecimento_mensuracao.py). São dois ajustes:

  P6  Coleção Galvão: registros "Localizado" e com aquisição descrita passam de sustentados a
      pendentes, porque a coleção veio por transferência do IPHAN e não tem registro patrimonial
      identificável. Guarda e exposição não bastam como controle.
  P5  "Não localizado" no portal, mas com tombamento "Em uso" no SIPAC: passa de não reconhecido
      a pendente de conferência física. Depende de dados/vinculos_portal_sipac.csv (saída do
      cruzamento com o relatório de bens do SIPAC; não contém dados pessoais).

Regras, na ordem em que se aplicam:
  R1     "Não localizado", sem registro patrimonial que o contradiga -> Não reconhecimento fundamentado
  R3-P5  "Não localizado", mas tombamento "Em uso" no SIPAC           -> Pendente de verificação
  R3-P1  "Situação" vazia: existência física não conferida            -> Pendente de verificação
  R3-P2  Emprestado, sem documento no cadastro                        -> Pendente de verificação
  R3-P3  Localizado, mas falta forma, procedência ou data de aquisição-> Pendente de verificação
  R3-P6  Localizado e com aquisição descrita, em coleção sem registro patrimonial (Galvão) -> Pendente
  R2     Localizado, com forma, procedência e data de aquisição       -> Reconhecimento sustentado

Execução (raiz do repositório; só biblioteca padrão):  python codigos/reconhecimento_cenario_a.py
Saída: dados/reconhecimento.csv
"""
import csv
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "reconhecimento_regra_23nov.csv"
VINCULOS = RAIZ / "dados" / "vinculos_portal_sipac.csv"
SAIDA = RAIZ / "dados" / "reconhecimento.csv"
PENDENTE = "Pendente de verificação"


def ler(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def main():
    rec = ler(ENTRADA)
    divergentes, tem_vinculos = set(), VINCULOS.exists()
    if tem_vinculos:
        divergentes = {v["numero_registro_portal"] for v in ler(VINCULOS) if v["divergencia_existencia"] == "Sim"}
    else:
        print("AVISO: dados/vinculos_portal_sipac.csv não encontrado. A regra P5 não foi aplicada: os registros\n"
              "       'Não localizado' ficam todos em R1. Com o arquivo, 21 deles passam a pendentes (18 em R1).")

    for r in rec:
        crit, classe = r["criterio_aplicado"], r["classificacao"]
        motivo = ""
        if classe.startswith("Não reconhecimento"):
            if r["numero_registro"] in divergentes:
                r["classificacao"] = PENDENTE
                r["criterio_aplicado"] = "R3 – P5: 'Não localizado' no portal, mas tombamento 'Em uso' no SIPAC"
                r["c1_existencia_do_recurso"] = "Contraditória: 'Não localizado' no portal e 'Em uso' no SIPAC"
                r["justificativa"] = ("Os dois sistemas se contradizem sobre a existência do bem. Não se presume a existência "
                                      "pelo SIPAC; o registro fica pendente de conferência física.")
                r["conclusao_contabil_proposta"] = "Manter pendente; conferir fisicamente e conciliar portal e SIPAC"
                motivo = "P5: catálogo diz 'não localizado', SIPAC diz 'em uso'"
            else:
                r["criterio_aplicado"] = "R1: 'Não localizado' no portal, sem registro patrimonial que o contradiga"
                if not tem_vinculos:
                    r["criterio_aplicado"] += " [cruzamento com o SIPAC não aplicado nesta execução]"
        elif classe.startswith("Reconhecimento sustentado"):
            if r["colecao"] == "Galvão":
                r["classificacao"] = PENDENTE
                r["criterio_aplicado"] = "R3 – P6: Localizado e com aquisição descrita, mas em coleção sem registro patrimonial (Galvão)"
                r["c2_controle_evidencia_de_incorporacao"] = ("Transferência do IPHAN descrita no catálogo; sem bem identificável no SIPAC "
                                                              "e sem o instrumento da transferência")
                r["justificativa"] = ("Guarda e exposição não bastam como controle. Não se sabe se a transferência foi de titularidade "
                                      "ou apenas de guarda; o registro fica pendente até se conhecer o instrumento.")
                r["conclusao_contabil_proposta"] = "Manter pendente; obter o instrumento da transferência do IPHAN"
                motivo = "P6: transferência sem registro patrimonial (Galvão)"
            else:
                r["criterio_aplicado"] = "R2: Localizado, com forma, procedência e data de aquisição"
        else:
            if "existência física não conferida" in crit:
                motivo = "P1: existência física não conferida"
            elif "empréstimo" in crit:
                motivo = "P2: empréstimo sem documento"
            else:
                motivo = "P3: aquisição não documentada"
            r["criterio_aplicado"] = crit.replace("R3: ", "R3 – " + motivo[:2] + ": ", 1)
        r["motivo_pendencia"] = motivo
        r["cenario"] = "A (conservador), decisão da equipe em 24/11/2026"

    with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rec[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rec)

    print("Gerado: dados/reconhecimento.csv,", len(rec), "registros")
    for k, v in Counter(r["classificacao"] for r in rec).most_common():
        print(f"  {k}: {v}")
    for k, v in sorted(Counter(r["motivo_pendencia"] for r in rec if r["motivo_pendencia"]).items()):
        print(f"    {k}: {v}")
    for k, v in sorted(Counter((r["colecao"], r["classificacao"]) for r in rec).items()):
        print("   ", k, v)


if __name__ == "__main__":
    main()
