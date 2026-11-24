# Etapa III — Mensuração: modelo e memorial

**Arquivo gerado:** `dados/mensuracao.csv` (1.335 registros)
**Código:** `codigos/pipeline_reconhecimento_mensuracao.py`
**Posição em 23/11/2026:** nenhum registro tem mensuração monetária fundamentada. O modelo está aplicado a todos os registros como triagem; os valores dependem de evidências que a equipe ainda vai coletar.

## 1. Base de mensuração (o que se mede)

A escolha da base decorre da forma de aquisição e da finalidade para a qual o bem é mantido, e não da técnica disponível.

| Momento | Base indicada | Fundamento | Registros |
|---|---|---|---|
| Reconhecimento inicial | Custo atribuído | Aquisição sem contraprestação (doação ou transferência): NBC TSP 37, item 12; NBC TSP 38, itens 10 a 13 | 1.149 |
| Reconhecimento inicial | [INFORMAÇÃO PENDENTE] | Forma de aquisição não informada; não se sabe se há custo histórico | 186 |
| Mensuração subsequente, se adotado o modelo do valor corrente | Valor corrente operacional | Bem mantido pelo potencial de serviços, e não para retorno financeiro: NBC TSP 37, itens 24 e 27; NBC TSP 38, itens 23 a 25 | 1.335 |

- **Custo histórico** não se aplica aos registros de doação e transferência, porque não houve preço de transação. Só entra se algum termo de incorporação trouxer valor.
- **Valor justo** foi afastado como base corrente: a NBC TSP 37 (item 27) reserva essa base aos itens mantidos principalmente pela capacidade financeira, o que não é o caso de um acervo museológico.
- O custo atribuído é determinado por uma base de valor corrente (NBC TSP 38, item 10). Na prática, as duas linhas da tabela exigem a mesma estimativa, em datas-base diferentes.

Os itens foram lidos em reprodução das normas (legisweb.com.br) e devem ser conferidos no texto oficial do CFC. A NBC TSP 38 aplica-se a partir de 1º/1/2027.

## 2. Técnica de estimativa (como se estima)

A NBC TSP 38 (item 37) distingue técnica de base. As técnicas admitidas são a abordagem de mercado (item 42), a de custo (itens 43 e 44) e a de renda (item 45).

| Categoria | Técnica indicada | Situação em `mensuracao.csv` | Registros |
|---|---|---|---|
| Arte, com autoria e técnica, reconhecimento sustentado | Abordagem de mercado | Elegível – pesquisa de comparáveis pendente | 157 |
| Arte, com autoria e técnica, reconhecimento pendente | Abordagem de mercado | Condicionada ao reconhecimento | 288 |
| Arte, sem autoria ou sem técnica | Nenhuma aplicável; avaliação especializada | Impossibilidade de estimativa confiável | 19 |
| Obra contemporânea | Sem comparável direto; custo só com documentação | Impossibilidade de estimativa confiável | 11 |
| Etnográfica | Nenhuma aplicável; avaliação especializada com a comunidade de origem | Impossibilidade de estimativa confiável | 821 |
| Não reconhecidos | Não aplicável | Não aplicável | 39 |

A abordagem de renda não foi usada: os bens não geram fluxos de caixa identificáveis.

### 2.1 Arte: abordagem de mercado

Para cada registro elegível, a equipe deve registrar em `dados/evidencias_mercado.csv` cada comparável encontrado, com estes campos:

`numero_registro; autor; titulo_comparavel; tecnica; dimensoes; tiragem; conservacao; data_transacao; valor; moeda; natureza_evidencia; fonte; url; data_consulta; diferencas_para_o_bem`

- **Natureza da evidência:** "preço de transação" (leilão realizado, venda efetiva), "preço anunciado" (galeria, anúncio) ou "estimativa de catálogo". Só o preço de transação sustenta a estimativa; preço anunciado é registrado como referência e não entra no cálculo.
- **Mínimo para estimar:** três transações do mesmo autor e da mesma técnica, com data conhecida.
- **Cálculo proposto:** valor por comparável corrigido para a data-base, ajustado por dimensões; estimativa central pela mediana; intervalo pelo mínimo e pelo máximo ajustados. [VERIFICAR: índice de correção a adotar e forma do ajuste por dimensão são decisões da equipe para 24/11.]
- **Sensibilidade:** recalcular excluindo o maior e o menor comparável.
- **Nível dos dados de entrada:** transações de obras similares em mercado pouco ativo correspondem ao Nível 2 da hierarquia da NBC TSP 38 (item 6).

### 2.2 Obras contemporâneas

Critério de identificação dentro da coleção Arte: denominação ou técnica com os termos do item 4.2 das regras (arte digital, performance, vídeo, instalação, postal, computacional, PVC, imagem projetada e similares). Resultado: 11 registros.

Dificuldades examinadas, conforme as regras:

| Dificuldade | O que o cadastro mostra |
|---|---|
| Autenticidade | Não há certificado nem número de edição em nenhum dos 11 registros |
| Documentação | Data de produção ausente nos 11; dimensões ausentes nos 11 |
| Materialidade | Suportes como PVC, papel fotográfico e impressão digital, reprodutíveis por natureza |
| Conservação | Estado de conservação informado em 2 dos 11 |
| Direitos associados | O portal informa apenas "direitos reservados" sobre as imagens; não há termo sobre exibição ou reprodução da obra |
| Comparáveis | Registros de performance e arte computacional não têm comparável direto identificado |

Conclusão: impossibilidade de estimativa confiável com as evidências disponíveis, para os 11 registros.

**Ressalva importante.** A coleção Triangular, excluída por decisão da equipe, reúne 162 registros de videoarte, instalação, videoinstalação, livro de artista e registro de performance, datados de 1995 a 2020. É onde está a maior parte do que as regras descrevem como obra contemporânea.

### 2.3 Coleções etnográficas

- A abordagem de mercado foi afastada: não há transações comparáveis identificadas, e as regras vedam tratar esses objetos como mercadoria livremente negociável.
- A abordagem de custo não tem base no cadastro: não há custo de aquisição, e a substituibilidade de cada objeto é questão cultural, a ser respondida por especialista e pela comunidade de origem.
- Tratamento proposto: divulgação não financeira (NBC TSP 37, itens 7 e 77), com quantidade, procedência, grupo de origem e as razões da impossibilidade de mensuração.

## 3. Grau de confiabilidade das evidências

Mede a completude dos fatores de comparabilidade do item 9.2 das regras que o cadastro traz: autoria, técnica, dimensões, data de produção e estado de conservação, mais a tiragem no caso das gravuras. Não é o grau de confiança de um valor, porque ainda não há valores.

| Índice (fatores presentes ÷ aplicáveis) | Grau |
|---|---|
| 0,8 ou mais | Alta |
| 0,6 a 0,79 | Média |
| 0,3 a 0,59 | Baixa |
| abaixo de 0,3 | Insuficiente |

Na categoria Arte (464 registros): 2 Alta, 12 Média, 432 Baixa e 18 Insuficiente. O principal motivo é a ausência de dimensões em 462 dos 464 registros. Sem medir as obras, o ajuste por tamanho não pode ser feito.

## 4. Indicadores desta etapa

| Indicador | Valor |
|---|---|
| Mensuração fundamentada | 0 |
| Mensuração pendente (elegível ou condicionada) | 445 |
| Impossibilidade de estimativa confiável | 851 |
| Não aplicável (não reconhecidos) | 39 |
| Valor agregado estimado | Não aplicável |

## 5. Limitações

- Nenhuma pesquisa de mercado foi feita nesta etapa; a coluna `valor_estimado` está integralmente como [INFORMAÇÃO PENDENTE].
- A elegibilidade à abordagem de mercado indica apenas que há dados para procurar comparáveis, e não que o autor tenha mercado ativo.
- Os resultados são acadêmicos e não constituem registro contábil oficial da UnB, nem "valor total do patrimônio cultural da CAL".
