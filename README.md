# Hackathon CULTIVA UnB 2026 — Valoração do Patrimônio Cultural da CAL/UnB

Este repositório apresenta a solução desenvolvida pela nossa equipe para a **Identificação, Reconhecimento, Mensuração e Evidenciação** dos ativos culturais sob a custódia da Casa da Cultura da América Latina (CAL/UnB).

> Exercício acadêmico. Os números deste repositório não são registro contábil oficial da UnB nem o valor total do patrimônio cultural da CAL. A cobertura é do acervo digital público, não do acervo físico.

## 👥 Integrantes da Equipe
- **Nome da Equipe:** Grupo 3
- **Integrantes:**  Ana Rosa Gomes Cunhas, David Mendes, Gilmara Martins de Oliveira e Iverton José Fernandes

## 🔎 Resultado em resumo (posição em 25/11/2026)

| Etapa | Resultado |
|---|---|
| Registros públicos identificados no portal | 1.497 |
| Universo analisado (sem a Coleção Triangular) | 1.335 |
| Reconhecimento sustentado (cenário A, conservador) | 224 (Arte 159; Inicial 65) |
| Mensuração fundamentada pelo valor corrente operacional | 9 registros; R$ 75.898,62 |
| Valor indicativo, não fundamentado | 1 registro |
| Mensuração pendente | 149 registros |
| Não monetária (objetos etnográficos) | 65 registros |

O valor fundamentado refere-se a nove gravuras em metal de Tarsila do Amaral, com base em três vendas realizadas em leilão. Preços de oferta não formam valor, objetos etnográficos não recebem valor em reais e valores escriturados no SIPAC aparecem só como informação.

## 📂 Estrutura do Repositório

| Pasta | Conteúdo |
|---|---|
| `metodologia/` | `reconhecimento.md` (critérios e regras do cenário A) e `memorial_mensuracao.md` (base, técnica, cálculo, sensibilidade e limitações) |
| `dados/` | `inventario.csv` (1.335 registros), `reconhecimento.csv` (matriz do cenário A), `mensuracao.csv` (224 registros), `evidencias_mercado.csv` (vendas usadas no cálculo), `reconhecimento_regra_23nov.csv` (matriz da regra inicial, entrada do cenário A) e `brutos/obras.xlsx` (extração) |
| `codigos/` | `baixar_acervo.py` (extração), `pipeline_reconhecimento_mensuracao.py` (inventário e regra inicial, 23/11), `reconhecimento_cenario_a.py`, `mensuracao_224.py` e `gerar_dashboard.py` |
| `resultados/` | `indicadores.csv`, `indicadores_mensuracao.csv`, `quadro_demonstrativo.csv`, `dashboard.html` e `candidatos_validacao_23nov.csv` |
| `relatorio_final/` | `nota_explicativa_minuta.md`, com a declaração de uso de IA |

A regra inicial de 23/11/2026 sustentava 353 registros. O cenário A, conservador, adotado em 24/11, reduziu esse número a 224: a Coleção Galvão (129 registros) passou a pendente, por falta de registro patrimonial da transferência.

## ▶️ Como reproduzir

Requer apenas Python 3.8 ou superior, sem bibliotecas externas. A partir da raiz do repositório:

```
python codigos/reconhecimento_cenario_a.py
python codigos/mensuracao_224.py
python codigos/gerar_dashboard.py
```

Depois, abra `resultados/dashboard.html` no navegador.

Para aplicar a outro lote ou a outro acervo: acrescente as vendas realizadas à lista `EVIDENCIAS` de `mensuracao_224.py` e a regra do lote à função `grupo`. Um lote só recebe valor quando alcança três vendas realizadas.

## 📊 Fontes de Dados
- **Acervo Digital da CAL/UnB:** https://www.acervocal.unb.br/ (Plataforma Tainacan)
- **Vendas em leilão:** Acervo Leilões, com os endereços de cada lote em `dados/evidencias_mercado.csv`
- **IPCA:** Banco Central do Brasil, SGS série 433 (https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json)
- **Monografia Temática:** *Coleções Museológicas da Universidade de Brasília: Identificação e descrição da gestão* (Imai, M. F., 2016).
- **Normativos Governamentais e Técnicos:** NBC TSP 37, NBC TSP 38 (Mensuração) e Portaria STN nº 548/2015.

---
## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL

Este trabalho utilizou ferramentas de inteligência artificial generativa, conforme permitido pelas regras do Hackathon CULTIVA UnB 2026.

Nenhum valor monetário foi gerado pela IA. Os preços de venda, as comissões e as datas vêm de leilões consultados e confirmados pela equipe, que também tomou todas as decisões metodológicas: cenário de reconhecimento, mínimo de três vendas por lote, exclusão de ofertas, tratamento dos valores escriturados e não atribuição de valor aos objetos etnográficos. A equipe revisou o material em 25/11/2026 e responde integralmente pelo conteúdo.

### Registro de uso de IA

| Data | Ferramenta | O que foi pedido | O que foi gerado | O que a equipe validou ou precisa validar |
|---|---|---|---|---|
| 23/11/2026, 20h30 | Gemini Enterprise | Estruturação metodológica do repositório, dicionário de dados e fundamentação de reconhecimento (NBC TSP 37) | Estrutura do repositório e textos de apoio | Revisão conceitual dos critérios de controle patrimonial; adequação da planilha ao dicionário |
| 23/11/2026 | Claude (Anthropic) | Extração do acervo, inventário, matriz de reconhecimento e modelo de mensuração | `inventario.csv`, `reconhecimento.csv`, `mensuracao.csv` e o pipeline de 23/11 | Amostra de registros contra o portal |
| 24/11/2026 | Claude (Anthropic) | Comparação com o SIPAC, identificação dos 224 reconhecidos, mensuração, nota e painel | Triagem dos 224, memorial, nota, quadro e painel (versões de 24/11) | Cenário de reconhecimento; evidências de mercado |
| 25/11/2026 | Claude (Anthropic) | Conferir as correções da equipe e aplicá-las | Conferência da aritmética e do IPCA; `reconhecimento_cenario_a.py`, `mensuracao_224.py`, `gerar_dashboard.py`, memorial, nota, quadro, indicadores e painel desta versão | Arremates, comissão de 5% e referências normativas conferidos pela equipe |
