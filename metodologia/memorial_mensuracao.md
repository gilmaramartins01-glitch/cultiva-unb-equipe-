# Memorial de cálculo da mensuração

Destino no repositório: `metodologia/memorial_mensuracao.md`
Arquivos: `dados/mensuracao.csv`, `dados/evidencias_mercado.csv`, `resultados/quadro_demonstrativo.csv`, `resultados/indicadores_mensuracao.csv`, `codigos/mensuracao_224.py`
Versão de 25/11/2026, após a revisão da equipe. Substitui o `mensuracao.md` de 23/11 e o memorial de 24/11.
A matriz de reconhecimento está em `dados/reconhecimento.csv` e em `metodologia/reconhecimento.md`.
Universo: 224 registros com reconhecimento sustentado no cenário A, conservador (159 da Coleção de Arte e 65 da Coleção Inicial; sem a Triangular).

> Exercício acadêmico. Estes números não são o valor do acervo da CAL nem registro contábil oficial da UnB.

## 1. Base e técnica

A base de mensuração e a técnica de estimativa são escolhas separadas.

| Escolha | Decisão | Fundamento |
|---|---|---|
| Base na entrada | Custo atribuído, porque as obras vieram por doação ou transferência | NBC TSP 37, item 12; NBC TSP 38, item 10 |
| Base posterior | Valor corrente operacional, porque o acervo é mantido pelo potencial de serviços | NBC TSP 37, item 27; NBC TSP 38, itens 23 a 25 |
| Técnica | Abordagem de mercado por lote | NBC TSP 38, item 42; critérios abaixo são decisão da equipe |
| Objetos etnográficos | Sem valor em reais; divulgação não financeira | Regras do hackathon; NBC TSP 37, itens 7 e 77 |

As referências normativas foram conferidas pela equipe. As normas aplicam-se a partir de 1º/1/2027; a aplicação aqui é prospectiva.

## 2. Critérios da abordagem de mercado (decisão da equipe)

1. **Só vendas realizadas (arremates) formam valor.** Preço de oferta, de anúncio e lance inicial não entram no cálculo nem no arquivo de evidências.
2. **Lote = mesmo autor + mesma técnica.**
3. **Mínimo de 3 vendas realizadas por lote**, para permitir mediana e faixa. É critério da equipe, não exigência de norma.
4. **Vendas de 2019 em diante.**
5. **Preço = martelo + comissão do comprador lida no edital.** Sem edital, a venda fica registrada, mas fora do cálculo.
6. **Atualização pelo IPCA** (Banco Central, SGS série 433), acumulado do mês seguinte ao da venda até outubro de 2026.
7. **Valor por obra = mediana** dos preços atualizados; faixa pelo menor e pelo maior.

Classificação resultante:

| Vendas realizadas no lote | Situação |
|---|---|
| 3 ou mais | Mensuração fundamentada |
| 2 | Valor indicativo (não fundamentado); não entra em total |
| 0 ou 1 | Pendente – evidência insuficiente |

## 3. Lote com mensuração fundamentada: Tarsila do Amaral, gravura em metal

Nove registros, CAL.1199 a CAL.1207, catalogados como água-forte sobre papel (técnica de gravura em metal). Vieram de doação do Banco Central em 25/09/1997.

| Obra comparável | Leilão / lote | Data | Martelo (R$) | Com 5% de comissão (R$) | Atualizado pelo IPCA até out/2026 (R$) |
|---|---|---|---|---|---|
| Crianças no vilarejo, gravura em metal, P/A, 16x16 cm | Acervo Leilões, leilão 37397, lote 108 | 30/08/2023 | 1.600,00 | 1.680,00 | 1.937,23 |
| Anjos (1972), gravura em metal, 45/100, 53x42 cm | Acervo Leilões, leilão 38749, lote 214 | 27/10/2023 | 7.000,00 | 7.350,00 | 8.433,18 |
| Carnaval em Madureira, gravura em metal, prova de estado II, 58x38 cm | Acervo Leilões, leilão 49334, lote 100 | 22/01/2025 | 7.900,00 | 8.295,00 | 8.988,67 |

Fontes:
- https://acervoleiloes.com.br/peca.asp?ID=18264246
- https://acervoleiloes.com.br/peca.asp?ID=18901735
- https://acervoleiloes.com.br/peca.asp?ID=24190524
- IPCA: https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json (consulta em 25/11/2026)

A equipe abriu as três páginas, confirmou que são arremates e confirmou a comissão de 5% nos editais.

Resultado:

| Item | Valor |
|---|---|
| Valor por obra (mediana) | R$ 8.433,18 |
| Faixa por obra | R$ 1.937,23 a R$ 8.988,67 |
| Total do lote (9 obras) | **R$ 75.898,62** |
| Grau de confiabilidade | Baixa |
| Situação | Mensuração fundamentada – abordagem de mercado por lote (mínimo atingido) |

Alertas:
- São só 3 vendas, todas de uma única casa de leilões.
- Não há ajuste por tiragem nem por dimensões, porque o portal não informa esses dados para as obras da CAL.
- A gravura de 16x16 cm é bem menor que as demais.
- "Anjos" é o comparável mais próximo (série de 1972, tiragem de 100) e coincide com a mediana.

Foram retiradas do cálculo a venda de 2016 (Galeria Alphaville), por ser anterior a 2019, e as ofertas da Forma Arte, por não serem preço de transação.

## 4. Sensibilidade

| Cenário | Valor por obra (R$) | Total das 9 obras (R$) |
|---|---|---|
| Menor comparável | 1.937,23 | 17.435,07 |
| **Mediana (adotado)** | **8.433,18** | **75.898,62** |
| Sem a gravura de 16x16 cm (média das duas restantes; fica abaixo do mínimo de 3) | 8.710,93 | 78.398,37 |
| Maior comparável | 8.988,67 | 80.898,03 |

O resultado depende sobretudo de aceitar ou não a gravura pequena como comparável. Com ela, a mediana recai sobre "Anjos".

## 5. Registros sem mensuração fundamentada (215)

| Grupo | Registros | Situação | Motivo |
|---|---|---|---|
| Tarsila do Amaral, serigrafia (CAL.1198) | 1 | Pendente – evidência insuficiente | Desde 2019 só a venda de um álbum de 4 pranchas, não comparável |
| Tomás Sánchez, serigrafia (CAL.1208) | 1 | Valor indicativo (não fundamentado) | 2 vendas, abaixo do mínimo; indicativo de R$ 18.591,70 (faixa de R$ 14.478,41 a R$ 22.704,99), só como informação |
| Maciej Babinski, gravura em metal | 21 | Pendente – evidência insuficiente | Só ofertas e 1 venda desde 2019 (R$ 300,00 em 2021, RM Gouvêa) |
| Milan Dusek, gravuras | 21 | Pendente – evidência insuficiente | Nenhuma venda localizada |
| Demais obras de arte | 22 | Pendente – evidência insuficiente | Autores com uma ou duas obras; nenhum lote com 3 vendas |
| Zeila Navarro Swain (doação de 2008) | 81 | Pendente – valor escriturado apenas informativo | Sem mercado observável; ver seção 6 |
| Johann Georg Scheuermann, desenho (CAL.1000) | 1 | Pendente – valor escriturado apenas informativo | Ver seção 6 |
| Cadastro incompleto (CAL.1272 e CAL.0854) | 2 | Pendente – cadastro incompleto | Sem autoria ou sem técnica |
| Objetos etnográficos (Coleção Inicial) | 65 | Não monetária | Limite ético; sem mercado legítimo nem custo de reposição |
| **Total** | **215** | | |

## 6. Valores escriturados no SIPAC: informação, não mensuração

- **Zeila Navarro Swain:** o SIPAC registra R$ 8.050,00 para um conjunto de 81 bens. A ligação com as 81 obras do portal é só por contagem, e o processo de doação de 2008 não foi localizado. O valor é informado como "valor escriturado no SIPAC para o conjunto, não confirmado" e não é atribuído às obras.
- **CAL.1000:** R$ 100,00 escriturados. É valor administrativo, não mensuração.
- Os valores do SIPAC são escriturados ou administrativos, e não custo histórico documentado. Nenhum deles entra em total de valor.

## 7. Indicadores

| Indicador | Valor |
|---|---|
| Registros com reconhecimento sustentado | 224 |
| Mensuração fundamentada pelo valor corrente operacional | 9 registros; R$ 75.898,62 |
| Valor indicativo, não fundamentado | 1 registro |
| Mensuração pendente | 149 registros |
| Não monetária (etnográficos) | 65 registros |
| Reconhecidos sem mensuração fundamentada | 215 registros |
| Evidências de mercado registradas / usadas | 3 / 3 |

## 8. Limitações

1. Valor fundamentado só para 9 gravuras, com 3 vendas de uma única casa.
2. Sem dimensões, tiragem e estado de conservação das obras da CAL, não há ajuste dos comparáveis.
3. Não foi verificado se as gravuras da CAL são da mesma série ou tiragem dos comparáveis.
4. O valor indicativo de Tomás Sánchez vem do relatório de mensuração da equipe, de 24/11/2026.
5. O processo de doação de 2008 (Navarro Swain) não foi localizado.
6. Não há laudo de especialista para nenhum grupo.
7. Nenhuma obra contemporânea está entre os 224 reconhecidos; a Coleção Triangular ficou fora por decisão da equipe.
8. A cobertura é do acervo digital público, não do acervo físico.

## 9. Como reproduzir

```
python codigos/reconhecimento_cenario_a.py
python codigos/mensuracao_224.py
python codigos/gerar_dashboard.py
```

Só a biblioteca padrão do Python é necessária. Para incluir um novo lote, acrescente as vendas à lista `EVIDENCIAS` do script e a regra do lote à função `grupo`.
