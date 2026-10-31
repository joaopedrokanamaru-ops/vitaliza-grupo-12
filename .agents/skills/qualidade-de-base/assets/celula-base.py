# Células-base do notebook de qualidade. Cada bloco "# %% célula" vira uma célula de código.
# Ajuste antes de rodar:
#   - ARQUIVOS: o arquivo diagnosticado primeiro, depois os cruzados;
#   - LINHAS_DICIONARIO: o número de linhas do cabeçalho da seção do dicionário;
#   - INICIO_DADOS: a primeira data que o dicionário promete para o arquivo.
# para_brasilia() e casa_por_data() servem a arquivos com data e hora (logs); apague-as se o arquivo não usar.

# %% célula: configuração (logo depois do título)
import hashlib
from pathlib import Path

import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
BRUTOS = ROOT / "dados" / "brutos"
SAIDAS = ROOT / "saidas"
INICIO_DADOS = pd.Timestamp("2024-07-01")  # ex.: início do log de eventos; ajuste ao arquivo
CORTE = pd.Timestamp("2026-09-30")
FIM_CORTE = CORTE + pd.Timedelta(days=1)   # 01/10/2026 00:00, horário de Brasília
TZ_BR = "America/Sao_Paulo"

ARQUIVOS = ["<arquivo>.csv", "usuarios.csv"]
LINHAS_DICIONARIO = 0

def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()

hash_inicio = {f: sha1(BRUTOS / f) for f in ARQUIVOS}

achados = []

def achado(criterio, checagem, resultado, linhas, tratamento, status=None):
    """status: ok (nada encontrado), esperado (encontrado, mas é comportamento do negócio) ou atenção.
    Sem status explícito: ok quando nenhuma linha é afetada, atenção caso contrário."""
    if status is None:
        status = "ok" if linhas == 0 else "atenção"
    achados.append({"criterio": criterio, "checagem": checagem, "status": status,
                    "resultado": resultado, "linhas_afetadas": int(linhas), "tratamento_sugerido": tratamento})

def ler(nome, **kwargs):
    """Lê como gravado: tudo texto, vazio como "" (parquet mantém os tipos do arquivo)."""
    if nome.endswith(".parquet"):
        return pd.read_parquet(BRUTOS / nome, **kwargs)
    return pd.read_csv(BRUTOS / nome, dtype=str, keep_default_na=False, **kwargs)

def para_brasilia(texto):
    """Data e hora terminadas em Z estão em UTC; as demais, em horário de Brasília. Devolve Brasília sem fuso."""
    eh_utc = texto.str.endswith("Z")
    utc = pd.Series(pd.NaT, index=texto.index, dtype="datetime64[ns, UTC]")
    utc[eh_utc] = pd.to_datetime(texto[eh_utc], format="%Y-%m-%dT%H:%M:%SZ", errors="coerce", utc=True)
    utc[~eh_utc] = (pd.to_datetime(texto[~eh_utc], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                    .dt.tz_localize(TZ_BR).dt.tz_convert("UTC"))
    return utc.dt.tz_convert(TZ_BR).dt.tz_localize(None)

def casa_por_data(base, outro, tolerancia_dias=1):
    """Para cada linha de base (user_id, data_br), diz se outro tem linha do mesmo user_id a até N dias."""
    m = base[["user_id", "data_br"]].reset_index().merge(
        outro[["user_id", "data_br"]].rename(columns={"data_br": "data_outro"}), on="user_id", how="left")
    m["ok"] = (m["data_outro"] - m["data_br"]).dt.days.abs() <= tolerancia_dias
    return m.groupby("index")["ok"].any().reindex(base.index, fill_value=False)

# %% célula: leitura (seção 0)
df = ler(ARQUIVOS[0])
usuarios = ler("usuarios.csv", usecols=["user_id", "email", "data_cadastro"])
assert len(df) == LINHAS_DICIONARIO
N = len(df)
print(f"{ARQUIVOS[0]}: {N:,} linhas x {df.shape[1]} colunas -> {list(df.columns)}")
df.dtypes.to_frame("tipo").T  # em arquivo sem texto livre, troque por df.sample(5, random_state=0)

# %% célula: vazios por coluna (início da Completude)
VAZIOS_DISFARCADOS = {"nan", "null", "none", "na", "n/a", "-"}
texto = df.astype(str)
vazios = pd.DataFrame({
    "vazio": [(texto[c].str.strip() == "").sum() for c in df.columns],
    "vazio_disfarcado": [texto[c].str.strip().str.lower().isin(VAZIOS_DISFARCADOS).sum() for c in df.columns],
}, index=df.columns)
vazios["% vazio"] = (100 * vazios["vazio"] / N).round(1)
vazios

# %% célula: contas de teste
eh_teste = usuarios.set_index("user_id")["email"].str.strip().str.lower().str.endswith("@vitaliza.com.br")
linhas_teste = int(df["user_id"].map(eh_teste).eq(True).sum())
achado("Completude", "linhas de contas de teste (@vitaliza.com.br)", f"{linhas_teste:,}", linhas_teste,
       "Se houver: excluir, como em assinaturas.csv")

# %% célula: resumo (seção 6)
resumo = pd.DataFrame(achados)
resumo["% do arquivo"] = (100 * resumo["linhas_afetadas"] / N).round(2)
resumo.to_csv(SAIDAS / f"qualidade_{Path(ARQUIVOS[0]).stem}.csv", index=False)
print(resumo["status"].value_counts().to_dict())
resumo

# %% célula: integridade (última)
hash_fim = {f: sha1(BRUTOS / f) for f in ARQUIVOS}
assert hash_fim == hash_inicio
print("dados/brutos/ inalterado:", hash_fim == hash_inicio)
