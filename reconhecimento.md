# Etapa II — Reconhecimento contábil

**Arquivo gerado:** `dados/reconhecimento.csv` (1.335 registros)
**Código:** `codigos/pipeline_reconhecimento_mensuracao.py`
**Fonte dos dados:** Acervo Digital da CAL/UnB, coleção "Acervo" (Tainacan, id 1565), consulta de 23/11/2026, 22h13 UTC.

## 1. Escopo

| Conjunto | Registros | Situação |
|---|---|---|
| Arte | 475 | Incluído (11 marcados como obra contemporânea) |
| Inicial | 349 | Incluído (etnográfica) |
| Galvão | 347 | Incluído (etnográfica) |
| Chocó | 163 | Incluído (etnográfica) |
| Sem coleção informada | 1 | Incluído como "Não classificada" |
| Triangular | 162 | **Fora do escopo por decisão da equipe em 23/11/2026** |
| CNRC | — | Não aparece no metadado "Coleção"; não utilizada por ora |

A inclusão da coleção Triangular depende apenas de mudar `INCLUIR_TRIANGULAR = True` no código.

## 2. Fundamento normativo

- **NBC TSP Estrutura Conceitual (R1):** ativo é recurso controlado no presente pela entidade, como resultado de evento passado. [VERIFICAR: número do item na versão R1, em cfc.org.br]
- **NBC TSP 37 — Ativo Imobilizado, item 6:** o item é reconhecido se (a) for provável que benefícios econômicos futuros ou potencial de serviços fluam para a entidade e (b) puder ser mensurado confiavelmente.
- **NBC TSP 37, itens 7 e 77:** o bem do patrimônio cultural tangível que satisfaz a definição de ativo, mas não o critério de mensuração confiável, não é reconhecido no balanço; a entidade divulga em nota as dificuldades de mensuração e a relevância do bem. Quando houver informação de custo ou de valor corrente, o ativo passa a ser reconhecido.
- **Vigência:** a NBC TSP 37 aplica-se a partir de 1º/1/2027 e revoga a NBC TSP 07. A análise é, portanto, prospectiva.

Os itens acima foram lidos em reprodução da norma (legisweb.com.br) e devem ser conferidos no texto oficial do CFC antes da entrega final.

## 3. Critérios examinados por registro

| Critério | Coluna | Evidência usada no cadastro |
|---|---|---|
| Existência do recurso | `c1_existencia_do_recurso` | Metadado "Situação" (Localizado, Não localizado, Emprestado ou vazio) |
| Controle pela entidade | `c2_controle_evidencia_de_incorporacao` | "Forma de aquisição", "Procedência" e "Data de aquisição" |
| Potencial de serviços | `c3_potencial_de_servicos` | "Exposições"; na falta, finalidade museológica |
| Benefícios econômicos | `c4_beneficios_economicos` | Não evidenciados; bem não mantido para gerar caixa |
| Natureza e classificação | `natureza_e_classificacao` | Bem do patrimônio cultural tangível (acervo) |
| Investigação adicional | `investigacao_adicional` | Lacunas específicas do registro |

O portal não traz número de patrimônio nem termo de incorporação. Por isso, constar no portal não foi tratado como prova de controle, e todo registro carrega a pendência de confirmação documental.

## 4. Regras de decisão

| Regra | Condição | Classificação |
|---|---|---|
| R1 | Situação = "Não localizado" | Não reconhecimento fundamentado |
| R2 | Situação = "Localizado" **e** forma, procedência e data de aquisição preenchidas | Reconhecimento sustentado pelas evidências |
| R3 | Qualquer outro caso | Pendente de verificação, com o motivo específico |

**Alcance de R2.** A classificação "sustentado" refere-se à definição de ativo e ao item 6(a). O item 6(b), mensuração confiável, é examinado em `dados/mensuracao.csv`. Enquanto ele não for atendido, a conclusão contábil proposta é a divulgação dos itens 7 e 77, e não o registro no balanço.

**Alcance de R1.** A conclusão vale enquanto o bem não for localizado e não dispensa a apuração do paradeiro.

## 5. Resultado

| Categoria | Sustentado | Não reconhecimento | Pendente | Total |
|---|---|---|---|---|
| Arte | 159 | 0 | 305 | 464 |
| Arte – obra contemporânea | 0 | 0 | 11 | 11 |
| Etnográfica | 194 | 38 | 627 | 859 |
| Não classificada | 0 | 1 | 0 | 1 |
| **Total** | **353** | **39** | **943** | **1.335** |

Principais motivos de pendência:

- **Existência física não conferida** (situação não informada): 798 registros, dos quais 734 têm só esse motivo.
- **Forma de aquisição não informada:** 175 registros, entre eles os 163 da coleção Chocó, que informam procedência (Embaixada da Colômbia) e ano (1989), mas não a forma.
- **Empréstimo sem identificação das partes:** 10 registros da coleção Galvão.

## 6. Coleções etnográficas

- O reconhecimento como ativo não torna o objeto mercadoria negociável nem autoriza presumir livre alienação (coluna `restricao_etica`).
- A coleção Galvão (347 registros) consta como transferência do IPHAN em 2002. É preciso confirmar se houve transferência de titularidade ou apenas de guarda.
- Toda a etapa de investigação adicional inclui a verificação de restrições de acesso e a consulta à comunidade de origem.

## 7. Limitações

- A análise usa apenas metadados públicos do portal; não houve acesso a termos de doação, ao sistema patrimonial da UnB nem conferência física.
- O campo "Situação" está vazio em 799 dos 1.497 registros do portal, o que limita o critério de existência.
- A regra R2 aceita o cadastro museológico como evidência de incorporação. Uma equipe mais conservadora pode exigir o termo de doação e reclassificar esses 353 registros como pendentes.
- Há 129 registros privados e 1 rascunho na coleção, não acessíveis.
