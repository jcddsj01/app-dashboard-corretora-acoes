# Importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# Obter a data atual YYYY-MM-DD
data_atual = date.today()

# Configuração do Streamlit
st.set_page_config(page_title="App - Dashboard de Corretora de Ações", layout="centered")

# Criar as funções de carregamento de dados
    # Cotações do Itaú - ITUB4 - 2010 a 2024
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period='1d', start='2010-01-01', end=data_atual)
    cotacoes_acao = cotacoes_acao['Close']
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV.csv', sep=';')
    tickers = list(base_tickers['Código'])
    tickers = [item + '.SA' for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)

# Criar a interface do streamlit
st.write("""
# App - Dashboard de Corretora de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo do ano.
""") # markdown

# Prepara as visualizações
st.sidebar.header("Filtros")

# Filtros de ações
lista_acoes = st.sidebar.multiselect(
    "Escolha as ações para visualizar",
    options=dados.columns,
    default=dados.columns[:6] # Seleciona os 6 primeiros por padrão
)

# Se nenhuma ação for selecionada, exibir aviso e parar execução
if not lista_acoes:
    st.warning("Nenhuma ação selecionada. Por favor, selecione pelo menos uma para exibir o gráfico.")
    st.stop()

# Se houver seleção, filtrar os dados normalmente
dados = dados[lista_acoes]

if len(lista_acoes) == 1:
    acao_unica = lista_acoes[0]
    dados = dados.rename(columns={acao_unica: "Close"})

# Filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()

intervalo_data = st.sidebar.slider("Selecione o período:", min_value=None, max_value=data_final, value=(data_inicial, data_final), step=timedelta(days=1), format="DD/MM/YYYY")

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# Criar o gráfico
st.line_chart(dados)

# Calcular e exibir a performance de cada ativo
texto_performance_ativos = ""
texto_performance_carteira = ""

if len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1 # preço final / preço inicial - 1
    performance_ativo = float(performance_ativo)

    carteira[i] *= (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos += f"  \n{acao}: :green[{performance_ativo:.2%}]"
    elif performance_ativo < 0:
        texto_performance_ativos += f"  \n{acao}: :red[{performance_ativo:.2%}]"
    else:
        texto_performance_ativos += f"  \n{acao}: {performance_ativo:.2%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f"  \n:green[{performance_carteira:.2%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"  \n:red[{performance_carteira:.2%}]"
else:
    texto_performance_carteira = f"  \n{performance_carteira:.2%}"

st.write(f"""
# Performance dos Ativos
Essa foi performance de cada ativo no período selecionado
{texto_performance_ativos}

Performance da Carteira com todos os ativos
{texto_performance_carteira}
""") # markdown