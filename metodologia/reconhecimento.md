# Etapa II — Reconhecimento: critérios, regras e resultado

Destino no repositório: `metodologia/reconhecimento.md`
Arquivos: `dados/reconhecimento.csv` (1.335 registros), `codigos/reconhecimento_cenario_a.py`
Versão de 25/11/2026. Cenário A (conservador), adotado pela equipe em 24/11/2026. Substitui o `reconhecimento.md` de 23/11.

> Exercício acadêmico. A classificação não é registro contábil oficial da UnB.

## 1. Fundamento

- Ativo é recurso controlado no presente pela entidade, como resultado de evento passado (NBC TSP Estrutura Conceitual).
- O item é reconhecido se for provável o fluxo de benefícios econômicos ou de potencial de serviços e se puder ser mensurado confiavelmente (NBC TSP 37, item 6).
- O bem do patrimônio cultural que satisfaz a definição de ativo, mas não a mensuração confiável, é divulgado em nota (NBC TSP 37, itens 7 e 77).
- Constar no portal não prova controle, e objetos de comunidades tradicionais não são mercadoria (regras do hackathon).
- As normas valem a partir de 1º/1/2027; a análise é prospectiva.

Esta etapa examina existência, controle e evidência de aquisição. A mensuração confiável é examinada na etapa III (`metodologia/memorial_mensuracao.md`).

## 2. Critérios e evidências

| Critério | Evidência no cadastro | Coluna |
|---|---|---|
| Existência do recurso | Metadado "Situação" e, quando há, o estado no SIPAC | `c1_existencia_do_recurso` |
| Controle e evento passado | Forma, procedência e data de aquisição | `c2_controle_evidencia_de_incorporacao` |
| Potencial de serviços | Acervo mantido para exposição, ensino, pesquisa e extensão | `c3_potencial_de_servicos` |
| Benefícios econômicos | Não evidenciados | `c4_beneficios_economicos` |

## 3. Regras de decisão

Aplicadas nesta ordem; o registro para na primeira que se aplica.

| Regra | Condição | Classificação | Registros |
|---|---|---|---|
| R1 | "Não localizado" no portal, sem registro patrimonial que o contradiga | Não reconhecimento fundamentado | 18 |
| R3 – P5 | "Não localizado" no portal, mas tombamento "Em uso" no SIPAC | Pendente de verificação | 21 |
| R3 – P1 | "Situação" vazia: existência física não conferida | Pendente de verificação | 798 |
| R3 – P2 | Emprestado, sem documento no cadastro | Pendente de verificação | 10 |
| R3 – P3 | Localizado, mas falta forma, procedência ou data de aquisição | Pendente de verificação | 135 |
| R3 – P6 | Localizado e com aquisição descrita, mas em coleção sem registro patrimonial (Galvão) | Pendente de verificação | 129 |
| R2 | Localizado, com forma, procedência e data de aquisição | Reconhecimento sustentado pelas evidências | 224 |

## 4. Resultado

| Coleção | Sustentado | Pendente | Não reconhecido | Total |
|---|---|---|---|---|
| Arte | 159 | 316 | 0 | 475 |
| Inicial | 65 | 266 | 18 | 349 |
| Galvão | 0 | 347 | 0 | 347 |
| Chocó | 0 | 163 | 0 | 163 |
| Sem coleção | 0 | 1 | 0 | 1 |
| **Total** | **224** | **1.093** | **18** | **1.335** |

Os 11 registros de arte contemporânea da Coleção de Arte estão todos pendentes. Como a Coleção Triangular ficou fora, não há obra contemporânea com reconhecimento sustentado; a lacuna é declarada.

## 5. Regra P5 e o arquivo do SIPAC

A separação entre R1 (18) e P5 (21) vem do cruzamento, feito em 24/11/2026, entre os 41 registros do portal com número de sete dígitos e o relatório de bens do SIPAC. O relatório bruto traz nomes de servidores e não é publicado.

O script lê o resultado desse cruzamento em `dados/vinculos_portal_sipac.csv`, que não contém dados pessoais. **Sem esse arquivo, a regra P5 não é aplicada e o `dados/reconhecimento.csv` mostra os 39 registros "Não localizado" em R1** (39 não reconhecidos e 1.072 pendentes). Os 224 sustentados e toda a mensuração não dependem dele.

## 6. Decisões e limites

- **Guarda e exposição não bastam como controle.** A Coleção Galvão foi recebida por transferência do IPHAN e não tem bem identificável no SIPAC; fica pendente até se conhecer o instrumento da transferência.
- **Não se presume existência pelo SIPAC.** Nos 21 casos de divergência, o registro fica pendente de conferência física.
- **O critério de controle apoia-se na aquisição descrita no próprio catálogo.** Só 22 registros têm tombamento identificado no SIPAC.
- **Coleções etnográficas:** o reconhecimento não torna o objeto mercadoria negociável nem autoriza presumir livre alienação.
- Não houve conferência física nem acesso a termos de doação.

## 7. Como reproduzir

```
python codigos/reconhecimento_cenario_a.py
```
