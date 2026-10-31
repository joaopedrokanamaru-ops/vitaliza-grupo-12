---
name: qualidade-de-base
description: "Faz o diagnóstico de qualidade de um arquivo do data room da Vitaliza pelos cinco critérios (completude, validade, consistência, unicidade e temporalidade), num notebook com tabela-resumo e decisões de tratamento propostas. Use quando pedirem para analisar, avaliar, conferir ou diagnosticar a qualidade de um arquivo ou tabela, ou perguntarem se um arquivo tem problema nos dados, mesmo sem citar os critérios. Aplicar as decisões e gerar a base limpa é outra tarefa: esta skill só diagnostica."
metadata:
  author: Fernanda Mori
  version: "1.1"
---

# Qualidade de base

Diagnóstico de **um arquivo por vez**, sempre no mesmo formato, para que o grupo compare arquivos e decisões lado a lado.
Os exemplos de referência são `notebooks/02_qualidade_eventos_assinatura.ipynb` (log de eventos) e
`notebooks/03_qualidade_pagamentos.ipynb` (log com valores): abra um deles quando tiver dúvida de forma.

O trabalho é **só diagnóstico**. Nada em `dados/brutos/` muda, e nenhum dado é corrigido. Cada problema sai com um
tratamento sugerido, e só vira regra no `decisoes.md` depois que a pessoa aprova.

## Passos

### 1. Reconhecer o arquivo

Leia, nesta ordem:

1. **Dicionário** (`docs/Vitaliza - Dicionário de dados.pdf`): só a página da seção do arquivo, pela [tabela de seções](#seções-do-dicionário).
   A contagem de linhas vem do cabeçalho da seção (a tabela "Visão geral" sai desalinhada na extração).
2. **Enunciado** (`docs/Vitaliza - Enunciado do case.pdf`): procure o nome do arquivo e o tema dele (`pdftotext ... - | grep -i`).
   O enunciado traz números que servem de prova (ex.: 14.120 assinantes sorteados na campanha) e promessas (cupons, preços).
3. **`decisoes.md`** e os resumos já em `saidas/qualidade_*.csv`: decisões que valem para este arquivo e perguntas deixadas em aberto.
4. **O próprio arquivo**, em scripts rápidos: tamanho, `value_counts` das categorias, vazios por coluna, identificadores contra o
   padrão (`u_[0-9a-f]{8}`), e os **padrões de formato** de datas e números (troque cada dígito por `9` e conte:
   `s.str.replace(r"\d", "9", regex=True).value_counts()`). Rode também a checagem que revele um sinal estrutural grande
   (mudança de volume, regra entre colunas): o reconhecimento termina quando os sinais estão listados, sem notebook.

Escolha os arquivos cruzados. Entra só o que uma checagem precisa:

- `usuarios.csv`, sempre: existência do `user_id`, contas de teste, data de cadastro;
- o arquivo que registra **o mesmo acontecimento por outro sistema** (eventos × pagamentos; uso mensal × treinos);
- o arquivo que diz **quem deveria estar** na tabela (a população), quando nenhum outro registra o mesmo acontecimento.
  Para uma data passada, a situação vem do log `eventos_assinatura.csv`, não do retrato `assinaturas.csv`.

Defina o **número-prova**: um total do dicionário ou do enunciado que a reconstrução deve reproduzir (14.753 ativos no corte;
14.120 pagantes em 10/08/2026). Bater esse número prova que o cruzamento está certo.

Quando o dicionário for omisso ou se contradisser (fuso não informado, lista de valores ausente, coluna "opcional" num
lugar e obrigatória em outro), não suponha: anote o ponto em "O dicionário não diz" no plano e trate como hipótese a testar
contra os dados ou pergunta ao dono do dado.

Pronto quando você tem os sinais observados (com números), os arquivos cruzados (cada um com o motivo), o número-prova
(ou "não há") e a lista do que o dicionário não diz.

### 2. Apresentar o plano e esperar a aprovação

Descubra a branch com `git branch --show-current`. Se for `main`, proponha no plano criar a branch pessoal (`teste-<nome>`).

Mostre o plano neste formato e pare:

```markdown
## O que já vi do arquivo
- <sinal com número, ex.: datas em dois padrões: 186.323 em UTC e 89.242 em horário de Brasília>

**O dicionário não diz:** <pontos omissos ou contraditórios, ou "nada a apontar">

## Plano de checagens
| Critério | O que vou checar |
|---|---|
| **Completude** | ... |
| **Validade** | ... |
| **Consistência** | ... |
| **Unicidade** | ... |
| **Temporalidade** | ... |

**Não se aplica a este arquivo:** <checagens do checklist que ficaram de fora e por quê>

## Como vou trabalhar
- notebook `notebooks/<NN>_qualidade_<arquivo>.ipynb`, resumo em `saidas/qualidade_<arquivo>.csv`, hash dos brutos conferido no início e no fim;
- arquivos cruzados: <arquivo: motivo>; número-prova: <total ou "não há">;
- decisões já registradas que valem aqui: <lista, ou "nenhuma">;
- só diagnóstico; decisões propostas no fim e registradas só com aprovação;
- branch `<branch>`, sem commit até pedirem.
```

Monte as checagens a partir de [references/checklist.md](references/checklist.md): leia a seção "Todas as formas" e a da
forma do arquivo (o dicionário classifica cada um como tabela, log de eventos ou texto e imagem; a campanha é também experimento).

Pronto quando a pessoa aprovou o plano (ou pediu ajuste, e você reapresentou).

### 3. Escrever e rodar o notebook

- `<NN>` é o próximo número livre em `notebooks/` (ex.: `04`); `<arquivo>` é o nome sem extensão (ex.: `qualidade_onboarding`).
- Comece pelas células de [assets/celula-base.py](assets/celula-base.py) e siga o cabeçalho dele para ajustá-las.
- Estrutura fixa: título com a tabela dos cinco critérios e o aviso de "só diagnóstico" → `0. Leitura` (com `assert` do
  número de linhas do dicionário e as colunas derivadas) → `1. Completude` … `5. Temporalidade` → `6. Resumo`.
- Toda checagem do plano termina numa chamada `achado(...)`, inclusive as que dão zero: o resumo mostra o que foi checado,
  não só o que falhou. Vazio estrutural (o controle sem mensagem, o trial sem plano) leva `status="esperado"` explícito.
- Cada seção abre com uma frase em markdown dizendo o que se espera ver. Hipótese testada ganha markdown próprio antes da célula que a testa.
- Texto livre aparece só como contagem e respostas mais frequentes, nunca como amostra ao lado do `user_id`.

Monte o `.ipynb` com um script `nbformat` guardado **fora do projeto** (no scratchpad) e rode a partir de `notebooks/`:

```bash
../.venv/Scripts/python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 <NN>_qualidade_<arquivo>.ipynb
```

(`.venv/bin/python` no macOS.) Ao imprimir as saídas no terminal do Windows, use `PYTHONIOENCODING=utf-8`.

Pronto quando o notebook roda inteiro com **0 erros e 0 avisos** (`grep -c '"ename"'` e `grep -c 'Warning'` no `.ipynb`),
o resumo foi salvo em `saidas/` e a última célula imprime `dados/brutos/ inalterado: True`.

### 4. Investigar os sinais

Antes de reportar, todo achado que não deu `ok` precisa de causa testada. Investigue num script à parte e devolva ao
notebook a hipótese (markdown) e a célula que a confirma:

- **O mesmo número em várias checagens é uma causa só.** Quase sempre é uma regra sua classificando errado, e não um defeito
  do dado. Exemplo: 6.734 apareceu como "plano vazio", "assinante sem início" e "divergência com o retrato"; eram
  desligamentos de renovação **durante o teste grátis**.
- **Coluna pode não significar o que o dicionário diz.** Teste o significado contra a sequência de acontecimentos.
  Exemplo: `tentativa` em `pagamentos.csv` não marca a nova tentativa após uma recusa.
- **Bater por dia não é bater em quantidade.** Depois do casamento por data, compare também as contagens por usuário.
- **Salto de volume não é falha até ser comparado com a base.** Compare com o crescimento de cadastros ou de assinantes no mesmo mês.
- Pergunta em aberto de um diagnóstico anterior que este arquivo responde: responda aqui e cite de onde veio.
- Problema que é do **arquivo cruzado**, e não deste: fica fora do resumo e vai como nota no relatório, para o diagnóstico daquele arquivo.

Classifique cada achado:

| Status | Quando |
|---|---|
| `ok` | nenhuma linha afetada |
| `esperado` | há linhas, mas é comportamento do negócio, explicado e testado |
| `atenção` | afeta análise e pede tratamento, ou o significado precisa ser confirmado com o dono do dado |

Pronto quando todo achado `esperado` ou `atenção` tem a causa testada no notebook ou está escrito como "hipótese a
confirmar com `<arquivo ou dono do dado>`", e o notebook rodou de novo sem erros nem avisos.

### 5. Reportar e propor decisões

Responda neste formato:

```markdown
O `<arquivo>` está **<veredito em poucas palavras>**. Das N checagens, X deram ok, Y são comportamento esperado e Z pedem atenção.
<links para o notebook e para o resumo; brutos inalterados>

## O que está bem
- <o que foi checado e bateu, com números; o número-prova, se houver>

## O que pede atenção
1. **<problema>:** <números e impacto na análise, em reais quando houver dinheiro>.

## O que parecia problema e não é
- <achado esperado e a explicação>

## Notas sobre outros arquivos
- <problema achado num arquivo cruzado; omita a seção se não houver>

## Decisões propostas para o `decisoes.md`
1. <regra de tratamento>
```

Pronto quando a pessoa respondeu sobre as decisões.

### 6. Registrar as decisões aprovadas

Só as aprovadas, uma linha cada, no fim da tabela do `decisoes.md`:

```markdown
| AAAA-MM-DD | <arquivo> | <problema> | <decisão> | <regra exata e o observado, ex.: até 24h após a expiração (observado: 0 a 16,6h)> | <linhas afetadas, e R$ quando houver> | <Nome> (Claude Code) |
```

Pergunta que ficou em aberto com o dono do dado vai escrita no critério da decisão que depende dela.

Pronto quando cada decisão aprovada tem linha com critério verificável e número de linhas, e nenhuma não aprovada entrou.

### 7. Commit e push, quando pedirem

Na branch pessoal de quem pediu, nunca na `main`. Antes do commit:

- adicione os arquivos pelo nome (notebook, resumo, `decisoes.md`), e não com `git add .`;
- confirme que nada de `dados/` entrou (`git diff --cached --name-only | grep -c '^dados/'` dá 0);
- confirme que as saídas do notebook não têm e-mail nem texto livre ao lado de `user_id`;
- se o git não tiver identidade configurada, passe-a só no commit (`git -c user.name=... -c user.email=... commit`).

Mensagem em português: título "Diagnostica a qualidade de <arquivo>", um parágrafo com a contagem ok/esperado/atenção e a
lista do que entrou.

Pronto quando `git status -sb` mostra a branch igual à remota.

## Referência

### Seções do dicionário

Leia só a página da seção: `pdftotext -layout -f <pág> -l <pág> "docs/Vitaliza - Dicionário de dados.pdf" -`
(o `pdftotext` vem com o Git Bash; o `.venv` não tem biblioteca de PDF). A ferramenta de leitura de PDF com `pages` também serve.

| Arquivo | Seção | Página | Forma |
|---|---|---|---|
| usuarios.csv | 02 | 3 | tabela |
| assinaturas.csv | 03 | 3-4 | tabela (retrato de 01/10/2026) |
| amizades.csv | 04 | 4 | tabela |
| campanha_ago26.csv | 05 | 5 | tabela, experimento |
| eventos_assinatura.csv | 06 | 5-6 | log de eventos |
| pagamentos.csv | 07 | 6 | log de eventos |
| uso_mensal.csv | 08 | 7 | log agregado por usuário e mês |
| atividades.parquet | 09 | 7-8 | log de eventos (`pd.read_parquet`) |
| onboarding.csv | 10 | 8 | texto |
| pesquisa_saida.csv | 11 | 9 | texto |
| feed_posts.csv | 12 | 9 | texto |
| tickets_suporte.csv | 13 | 10 | texto |
| heatmaps_90d/ | 14 | 11 | imagem |

### Pegadinhas

- **Fuso.** Em `eventos_assinatura.csv` e `pagamentos.csv`, data terminada em `Z` está em UTC e sem `Z` em horário de Brasília.
  Converta para Brasília (`America/Sao_Paulo`) antes de contar por dia ou mês: lendo só o texto, eventos da noite de 30/09
  parecem ser de 01/10. Em outro arquivo, a regra só vale se o dicionário disser ou se você testar contra outra fonte.
- **Leitura.** `dtype=str, keep_default_na=False` em todo CSV: o arquivo chega como gravado, e vazio fica `""`.
  Converta tipos em colunas derivadas, nunca sobre a original.
- **Ordem.** Ordene por usuário e data (com desempate pelo tipo de evento) antes de `groupby().shift()`, `diff()` ou `cumsum()`.
  Depois de reordenar, filtre com `.loc[mascara]`: a máscara criada antes da ordenação dispara aviso de reindexação.
- **Retrato × log.** `assinaturas.csv` é um retrato de 01/10/2026. A situação numa data vem dos logs. Reconstruído pelos
  eventos, o log dá os mesmos 14.753 ativos no corte.
- **Python.** Use o `.venv` do projeto (Python 3.11, apesar do 3.9 do `AGENTS.md`). No Windows os executáveis ficam em `.venv/Scripts/`.
  `scipy` não está instalado: teste estatístico simples (qui² de tamanho dos grupos) se calcula à mão com pandas; instalar pacote novo pede aprovação.
