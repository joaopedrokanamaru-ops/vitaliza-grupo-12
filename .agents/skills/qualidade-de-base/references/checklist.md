# Checklist por critério

Ponto de partida do plano. Leia "Todas as formas" e a seção da forma do arquivo. Cada item aplicável vira uma ou mais
chamadas `achado()`; o que não se aplica vai para a linha "Não se aplica a este arquivo" do plano.

## Todas as formas

- **Completude**: vazios por coluna, inclusive disfarçados (`nan`, `null`, `-`); vazio cruzado com a categoria, para separar
  o vazio esperado do que falta; contas de teste (e-mail `@vitaliza.com.br`); registros que deveriam existir em outro arquivo,
  **nos dois sentidos**; valores que o dicionário ou o enunciado prometem e não aparecem (ex.: cupom).
- **Validade**: cada categoria contra a lista do dicionário (sem lista, registre a lista observada como "O dicionário não diz");
  maiúsculas e espaços; cada formato de data e de número converte sem falha; números dentro de limites plausíveis;
  identificadores no padrão e `user_id` existente em `usuarios.csv`.
- **Consistência**: regras entre colunas da mesma linha (soma de partes = total, sinal × status, preço × data do reajuste,
  valor × plano); comparação com o arquivo cruzado; colunas cujo uso real contraria o dicionário.
- **Unicidade**: identificador repetido; chave natural repetida (ex.: `user_id` + `mes`); linha inteira repetida.
- **Temporalidade**: período coberto contra o dicionário e o corte (30/09/2026); volume por mês, procurando mês vazio e salto
  acima de 50%, **comparado com o crescimento da base** (cadastros ou assinantes do mês) antes de chamar de falha.

## Log de eventos

`eventos_assinatura.csv`, `pagamentos.csv`, `atividades.parquet`.

- **Consistência**: formato × origem (ex.: UTC só nas lojas); sequência por usuário, acompanhando o estado (ativo/inativo)
  linha a linha; situação final contra o retrato de outro arquivo, com o número-prova.
- **Unicidade**: **a mesma coisa com identificador diferente** (`duplicated` com todas as colunas menos o id artificial, como
  `pagamento_id`); quase-duplicatas em janela curta (mesmo usuário e evento em menos de 24h; exatamente 3h sugere o mesmo
  registro em dois fusos).
- **Temporalidade**: quantas linhas mudam de dia ao converter o fuso; ritmo esperado (intervalo entre cobranças, duração do
  trial); formato que muda ao longo do tempo.

## Tabela e log agregado

`usuarios.csv`, `assinaturas.csv`, `amizades.csv`, `campanha_ago26.csv`, `uso_mensal.csv`.

- **Completude**: quem deveria ter linha e não tem (a população vem do arquivo cruzado); meses faltando no meio da sequência
  de cada usuário, num agregado mensal.
- **Consistência**: o agregado contra o detalhe (ex.: `uso_mensal` × `atividades.parquet` por usuário e mês); registro
  anterior à data de cadastro.
- **Unicidade**: numa tabela só de categorias, linhas iguais sem o id são naturais. A checagem "mesma coisa com identificador
  diferente" não se aplica.
- **Temporalidade**: mudança de universo (quem passa a ter linha a partir de certo mês); **colunas sem data** (ex.: abriu,
  clicou): não dá para saber se aconteceram antes do corte, e usá-las num modelo é risco de vazamento.

## Texto livre

`onboarding.csv`, `pesquisa_saida.csv`, `feed_posts.csv`, `tickets_suporte.csv`.

- **Completude**: respostas sem conteúdo, além do vazio (`nada`, `ok`, `x`, `.`, `asdf`, `kkkk`, `sla`, `nao sei`, só emoji),
  contadas como vazio disfarçado; taxa de vazio por ano, procurando mudança no formulário.
- **Validade**: "texto livre" que na prática é categoria (ex.: `dias_por_semana`: 7 valores em 23 grafias): cada grafia
  converte para o valor sem falha; variantes de acento e erros de digitação por resposta.
- **Consistência**: texto livre contra a categoria de outro arquivo (ex.: `como_conheceu` × `canal_aquisicao`).
- **Privacidade**: dado pessoal ou @ de terceiros no texto: conte, nunca imprima ao lado do `user_id`.
- **Unicidade**: com dois ids (`onboarding_id` e `user_id`), tire os dois no `duplicated`; respostas comuns no mesmo dia são naturais.

## Experimento

`campanha_ago26.csv`.

- **Consistência**: equilíbrio do sorteio (tamanho dos grupos com qui² calculado à mão; perfil por plano, canal e tempo de
  casa, entre os grupos); controle sem envio, mensagem, oferta nem engajamento; hierarquia do engajamento (clicou ⇒ abriu);
  oferta × plano **na data do envio** (pelo log, não pelo retrato).
- **Completude**: população do sorteio contra o número-prova (pagantes na data, reconstruídos pelo log).
- **Temporalidade**: janela entre o envio e o corte; engajamento sem data (risco de vazamento).
