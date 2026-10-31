# Registro de decisões

| Data | Arquivo | Problema | Decisão | Critério | Linhas afetadas | Quem |
|------|---------|----------|---------|----------|-----------------|------|
| 2026-10-31 | assinaturas.csv | O arquivo é um retrato de 01/10/2026, não do corte (30/09/2026) | Usar `status_atual` do retrato como situação no corte, sem reconstruir por eventos_assinatura.csv | Nenhuma assinatura tem `inicio` ou `data_fim` depois de 30/09/2026, então nada mudou entre o corte e o retrato | 0 | Fernanda (Claude Code) |
| 2026-10-31 | assinaturas.csv | 29 assinaturas expiraram exatamente em 30/09/2026 | Remover da contagem de ativos no corte | `status_atual == "expirada"`: no fim do dia do corte já não estavam pagando | 29 | Fernanda (Claude Code) |
| 2026-10-31 | assinaturas.csv + usuarios.csv | Contas de teste da própria Vitaliza; são as 60 assinaturas de plano `cortesia`, canal `interno`, que o dicionário não descreve | Remover | E-mail termina em `@vitaliza.com.br` | 60 | Fernanda (Claude Code) |
