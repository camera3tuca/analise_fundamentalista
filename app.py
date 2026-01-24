import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="Análise BDRs - Fundamentalista",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e293b 0%, #1e3a8a 50%, #1e293b 100%);
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.5);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
    h1 {
        background: linear-gradient(to right, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Constantes
PERIODOS = 5
TERMINACOES_BDR = ('31', '32', '33', '34', '35', '39')

CRITERIOS = {
    'excelente': {'roe': 20, 'margem': 15, 'crescimento': 10, 'dividend_yield': 2, 'pe_max': 25},
    'bom': {'roe': 15, 'margem': 10, 'crescimento': 5, 'dividend_yield': 1, 'pe_max': 35},
    'atencao': {'roe': 10, 'margem': 5, 'crescimento': 0, 'dividend_yield': 0, 'pe_max': 50}
}

MAPA_BDRS_COMPLETO = {
    'AAPL34': 'AAPL', 'MSFT34': 'MSFT', 'GOGL34': 'GOOGL', 'AMZO34': 'AMZN',
    'NVDC34': 'NVDA', 'M1TA34': 'META', 'TSLA34': 'TSLA', 'NFLX34': 'NFLX',
    'A1MD34': 'AMD', 'ITLC34': 'INTC', 'ORCL34': 'ORCL', 'AVGO34': 'AVGO',
    'ADBE34': 'ADBE', 'CSCO34': 'CSCO', 'QCOM34': 'QCOM', 'TXAS34': 'TXN',
    'I2BM34': 'IBM', 'S2EA34': 'EA', 'U2NI34': 'U', 'ROXO34': 'RBLX',
    'C2OI34': 'COIN', 'P2LT34': 'PLTR', 'S2MP34': 'SMPL', 'M2RV34': 'MRVL',
    'MUTC34': 'MU', 'S2NO34': 'SNOW', 'D2OC34': 'DOCU', 'UBER34': 'UBER',
    'U1BE34': 'UBER', 'LYFT34': 'LYFT', 'SPOT34': 'SPOT', 'TWTR34': 'TWTR',
    'PINT34': 'PINS', 'SNAP34': 'SNAP', 'Z1M34': 'ZM', 'SHOP34': 'SHOP',
    'SQ1U34': 'SQ', 'HOOD34': 'HOOD', 'DKNG34': 'DKNG', 'DDOG34': 'DDOG',
    'VISA34': 'V', 'V2SA34': 'V', 'M2ST34': 'MA', 'PYPL34': 'PYPL',
    'CTGP34': 'C', 'B1AC34': 'BAC', 'J2PM34': 'JPM', 'W2FC34': 'WFC',
    'G2S34': 'GS', 'M2S34': 'MS', 'A1XP34': 'AXP', 'BERK34': 'BRK-B',
    'B1RO34': 'BRK.A', 'PAGS34': 'PAGS', 'NU34': 'NU', 'STOC34': 'STNE',
    'S1PW34': 'SPG', 'A1MG34': 'AMG', 'BLK34': 'BLK', 'SCHW34': 'SCHW',
    'WALM34': 'WMT', 'AMZN34': 'AMZN', 'COST34': 'COST', 'H0MC34': 'HD',
    'T1GT34': 'TGT', 'T2ND34': 'TGT', 'LOW34': 'LOW', 'M1CD34': 'MCD',
    'SBUB34': 'SBUX', 'NIKE34': 'NKE', 'COCA34': 'KO', 'P3EP34': 'PEP',
    'KO34': 'KO', 'PGCO34': 'PG', 'ULVR34': 'UL', 'WMT34': 'WMT',
    'NKE34': 'NKE', 'LULU34': 'LULU', 'ROST34': 'ROST', 'TJX34': 'TJX',
    'DISB34': 'DIS', 'CMCS34': 'CMCSA', 'NFLX34': 'NFLX', 'WBD34': 'WBD',
    'PARA34': 'PARA', 'SONY34': 'SONY', 'EA34': 'EA', 'TTWO34': 'TTWO',
    'JNJB34': 'JNJ', 'LILY34': 'LLY', 'ABBV34': 'ABBV', 'P1FE34': 'PFE',
    'UNH34': 'UNH', 'MRK34': 'MRK', 'A1BB34': 'ABT', 'T1MO34': 'TMO',
    'D1HU34': 'DHR', 'BMY34': 'BMY', 'AMGN34': 'AMGN', 'GILD34': 'GILD',
    'MDT34': 'MDT', 'CI34': 'CI', 'CVS34': 'CVS', 'HUM34': 'HUM',
    'B1AX34': 'BAX', 'ZTS34': 'ZTS', 'REGN34': 'REGN', 'VRTX34': 'VRTX',
    'EXXO34': 'XOM', 'CHVX34': 'CVX', 'SHEL34': 'SHEL', 'TOT34': 'TTE',
    'BP34': 'BP', 'COP34': 'COP', 'SLB34': 'SLB', 'OXY34': 'OXY',
    'HAL34': 'HAL', 'MPC34': 'MPC', 'PSX34': 'PSX', 'VLO34': 'VLO',
    'BOEI34': 'BA', 'C1AT34': 'CAT', 'D1EE34': 'DE', 'G1E34': 'GE',
    'H1ON34': 'HON', 'L1OC34': 'LMT', 'R1TH34': 'RTX', 'U1PS34': 'UPS',
    'U2PS34': 'UPS', 'F1DX34': 'FDX', 'GD34': 'GD', 'NOC34': 'NOC',
    'MMM34': 'MMM', 'EMR34': 'EMR', 'ETN34': 'ETN', 'ITW34': 'ITW',
    'FCXO34': 'FCX', 'N1VO34': 'NEM', 'F2NV34': 'FNV', 'NUE34': 'NUE',
    'DOW34': 'DOW', 'LYB34': 'LYB', 'APD34': 'APD', 'ECL34': 'ECL',
    'VALE34': 'VALE', 'RIO34': 'RIO', 'BHP34': 'BHP', 'SCCO34': 'SCCO',
    'TSMC34': 'TSM', 'ASML34': 'ASML', 'NVDA34': 'NVDA', 'AVGO34': 'AVGO',
    'AMD34': 'AMD', 'INTC34': 'INTC', 'QCOM34': 'QCOM', 'TXN34': 'TXN',
    'MU34': 'MU', 'MRVL34': 'MRVL', 'ADI34': 'ADI', 'KLAC34': 'KLAC',
    'BABA34': 'BABA', 'BIDU34': 'BIDU', 'JD34': 'JD', 'PDD34': 'PDD',
    'NIO34': 'NIO', 'XPEV34': 'XPEV', 'LI34': 'LI', 'TCEHY': 'TCEHY',
    'MELI34': 'MELI', 'GLOB34': 'GLOB', 'PBR34': 'PBR', 'ELET34': 'ELP',
    'T2T34': 'T', 'VZ34': 'VZ', 'TMUS34': 'TMUS', 'S2P34': 'S',
    'NEE34': 'NEE', 'DUK34': 'DUK', 'SO34': 'SO', 'D34': 'D',
    'A2RR34': 'ARR', 'AMT34': 'AMT', 'PLD34': 'PLD', 'EQIX34': 'EQIX',
    'RGTI34': 'RGTI', 'T2DH34': 'TDG', 'V1ST34': 'VST', 'F1MC34': 'FMC',
}

@st.cache_data(ttl=3600)
def obter_todas_bdrs():
    """Obtém lista de BDRs da B3 via BRAPI"""
    try:
        url = "https://brapi.dev/api/quote/list"
        r = requests.get(url, timeout=30)
        dados = r.json().get('stocks', [])
        
        bdrs_raw = [d for d in dados if d['stock'].endswith(TERMINACOES_BDR)]
        
        bdrs_processadas = []
        for bdr in bdrs_raw:
            ticker_bdr = bdr['stock']
            ticker_us = MAPA_BDRS_COMPLETO.get(ticker_bdr)
            
            if not ticker_us:
                ticker_us = ''.join([c for c in ticker_bdr if c.isalpha()])
            
            if ticker_us:
                bdrs_processadas.append({
                    'bdr': ticker_bdr,
                    'ticker_us': ticker_us,
                    'nome': bdr.get('name', ticker_bdr)
                })
        
        return bdrs_processadas
    except Exception as e:
        st.error(f"Erro ao buscar BDRs: {e}")
        return []

def calcular_indicadores_empresa_mae(ticker_us):
    """Busca dados fundamentalistas da empresa americana"""
    try:
        acao = yf.Ticker(ticker_us)
        info = acao.get_info()
        
        if not info or len(info) < 5:
            return None
        
        try:
            dre = acao.financials
            balanco = acao.balance_sheet
            
            if hasattr(dre, 'T'):
                dre = dre.T
            if hasattr(balanco, 'T'):
                balanco = balanco.T
        except:
            return None
        
        if dre is None or balanco is None or dre.empty or balanco.empty:
            return None
        
        dre = dre.head(PERIODOS)
        balanco = balanco.head(PERIODOS)
        
        # Tentar múltiplos nomes de colunas
        lucro = None
        for col in ["Net Income", "NetIncome", "Net Income Common Stockholders"]:
            if col in dre.columns:
                lucro = dre[col]
                break
        
        receita = None
        for col in ["Total Revenue", "TotalRevenue", "Total Revenues"]:
            if col in dre.columns:
                receita = dre[col]
                break
        
        patrimonio = None
        for col in ["Total Stockholder Equity", "Stockholders Equity", 
                    "StockholdersEquity", "Total Equity Gross Minority Interest"]:
            if col in balanco.columns:
                patrimonio = balanco[col]
                break
        
        ativo_total = None
        for col in ["Total Assets", "TotalAssets"]:
            if col in balanco.columns:
                ativo_total = balanco[col]
                break
        
        divida_total = None
        for col in ["Total Debt", "Long Term Debt", "TotalDebt"]:
            if col in balanco.columns:
                divida_total = balanco[col]
                break
        
        if lucro is None or receita is None or patrimonio is None:
            return None
        
        # Calcular indicadores
        roe = (lucro / patrimonio) * 100
        margem_liquida = (lucro / receita) * 100
        crescimento_receita = receita.pct_change() * 100
        roa = (lucro / ativo_total) * 100 if ativo_total is not None else pd.Series([np.nan])
        
        if divida_total is not None and patrimonio is not None:
            divida_pl = (divida_total / patrimonio) * 100
        else:
            divida_pl = pd.Series([np.nan])
        
        # Dados de mercado
        preco_atual = (info.get('currentPrice') or 
                      info.get('regularMarketPrice') or 
                      info.get('previousClose'))
        
        pe_ratio = (info.get('trailingPE') or info.get('forwardPE'))
        pb_ratio = info.get('priceToBook')
        
        dividend_yield = 0
        if info.get('dividendYield'):
            dividend_yield = info.get('dividendYield') * 100
        elif info.get('trailingAnnualDividendYield'):
            dividend_yield = info.get('trailingAnnualDividendYield') * 100
        
        market_cap = (info.get('marketCap') or info.get('enterpriseValue') or 0) / 1e9
        setor = info.get('sector') or info.get('industry') or 'N/A'
        
        # Médias dos indicadores
        return {
            'roe': roe.mean() if not roe.empty else 0,
            'margem': margem_liquida.mean() if not margem_liquida.empty else 0,
            'crescimento': crescimento_receita.mean() if not crescimento_receita.empty else 0,
            'dividapl': divida_pl.mean() if not divida_pl.empty else 0,
            'preco': preco_atual,
            'pe': pe_ratio,
            'pb': pb_ratio,
            'dividend_yield': dividend_yield,
            'market_cap': market_cap,
            'setor': setor
        }
    except Exception as e:
        return None

def classificar_tamanho(market_cap):
    """Classifica empresa por tamanho"""
    if market_cap >= 200:
        return 'Mega Cap'
    elif market_cap >= 10:
        return 'Large Cap'
    elif market_cap >= 2:
        return 'Mid Cap'
    else:
        return 'Small Cap'

def classificar_bdr(dados):
    """Classifica BDR baseado nos fundamentos"""
    score = 0
    max_score = 6
    alertas = []
    
    roe = dados.get('roe', 0)
    margem = dados.get('margem', 0)
    crescimento = dados.get('crescimento', 0)
    dividapl = dados.get('dividapl', 0)
    pe = dados.get('pe', 0)
    dividend_yield = dados.get('dividend_yield', 0)
    
    if roe >= CRITERIOS['excelente']['roe']:
        score += 1
    elif roe >= CRITERIOS['bom']['roe']:
        score += 0.5
    else:
        alertas.append('ROE baixo')
    
    if margem >= CRITERIOS['excelente']['margem']:
        score += 1
    elif margem >= CRITERIOS['bom']['margem']:
        score += 0.5
    else:
        alertas.append('Margem baixa')
    
    if crescimento >= CRITERIOS['excelente']['crescimento']:
        score += 1
    elif crescimento >= CRITERIOS['bom']['crescimento']:
        score += 0.5
    elif crescimento < 0:
        alertas.append('Receita em queda')
    
    if dividend_yield >= CRITERIOS['excelente']['dividend_yield']:
        score += 1
    elif dividend_yield >= CRITERIOS['bom']['dividend_yield']:
        score += 0.5
    
    if pe and pe > 0:
        if pe <= CRITERIOS['excelente']['pe_max']:
            score += 1
        elif pe <= CRITERIOS['bom']['pe_max']:
            score += 0.5
        elif pe > CRITERIOS['atencao']['pe_max']:
            alertas.append('P/E elevado')
    
    if not np.isnan(dividapl):
        if dividapl < 50:
            score += 1
        elif dividapl < 100:
            score += 0.5
        else:
            alertas.append('Endividamento alto')
    
    percentual = (score / max_score) * 100
    
    if percentual >= 80:
        status = '🟢 Excelente'
    elif percentual >= 60:
        status = '🟡 Bom'
    elif percentual >= 40:
        status = '🟠 Atenção'
    else:
        status = '🔴 Fraco'
    
    return status, score, alertas

# Interface Principal
st.title("📊 Análise Fundamentalista de BDRs")
st.markdown("**Análise completa baseada nos últimos 5 balanços das empresas-mãe americanas**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    limite_bdrs = st.slider(
        "Limite de BDRs para analisar",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
        help="Escolha quantas BDRs analisar (mais BDRs = mais tempo)"
    )
    
    st.info(f"⏱️ Tempo estimado: ~{limite_bdrs * 2 // 60} minutos")
    
    if st.button("🚀 Iniciar Análise", type="primary", use_container_width=True):
        st.session_state.analisar = True

# Análise
if 'analisar' in st.session_state and st.session_state.analisar:
    
    # Buscar BDRs
    with st.spinner("🔍 Buscando lista de BDRs..."):
        lista_bdrs = obter_todas_bdrs()
    
    if not lista_bdrs:
        st.error("❌ Não foi possível obter a lista de BDRs")
        st.stop()
    
    st.success(f"✅ {len(lista_bdrs)} BDRs encontradas!")
    
    # Limitar quantidade
    lista_bdrs = lista_bdrs[:limite_bdrs]
    
    # Processar BDRs
    progress_bar = st.progress(0)
    status_text = st.empty()
    stats_placeholder = st.empty()
    
    resultado = []
    sucesso = 0
    falhas = 0
    
    for idx, bdr_info in enumerate(lista_bdrs):
        bdr = bdr_info['bdr']
        ticker_us = bdr_info['ticker_us']
        nome = bdr_info['nome']
        
        status_text.text(f"🔄 Processando [{idx+1}/{len(lista_bdrs)}]: {bdr} → {ticker_us}")
        
        dados = calcular_indicadores_empresa_mae(ticker_us)
        
        if dados:
            status, score, alertas = classificar_bdr(dados)
            tamanho = classificar_tamanho(dados['market_cap'])
            
            resultado.append({
                'BDR': bdr,
                'Ticker US': ticker_us,
                'Empresa': nome.split()[0] if nome else ticker_us,
                'Setor': dados['setor'],
                'Tamanho': tamanho,
                'Status': status,
                'Score': round(score, 1),
                'ROE (%)': round(dados['roe'], 2),
                'Margem (%)': round(dados['margem'], 2),
                'Cresc (%)': round(dados['crescimento'], 2),
                'Dívida/PL (%)': round(dados['dividapl'], 2),
                'P/E': round(dados['pe'], 2) if dados['pe'] else np.nan,
                'P/B': round(dados['pb'], 2) if dados['pb'] else np.nan,
                'Div Yield (%)': round(dados['dividend_yield'], 2),
                'Market Cap (B)': round(dados['market_cap'], 2),
                'Alertas': ', '.join(alertas) if alertas else 'OK'
            })
            sucesso += 1
        else:
            falhas += 1
        
        progress_bar.progress((idx + 1) / len(lista_bdrs))
        
        # Mostrar stats parciais
        if (idx + 1) % 10 == 0:
            stats_placeholder.metric(
                "Progresso",
                f"{idx+1}/{len(lista_bdrs)}",
                f"✅ {sucesso} | ⚠️ {falhas}"
            )
        
        time.sleep(0.5)  # Delay para evitar rate limiting
    
    progress_bar.empty()
    status_text.empty()
    stats_placeholder.empty()
    
    if not resultado:
        st.warning("⚠️ Nenhuma BDR com dados suficientes encontrada")
        st.stop()
    
    # Criar DataFrame
    df = pd.DataFrame(resultado)
    df = df.sort_values(
        by=['Score', 'ROE (%)', 'Div Yield (%)'],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    
    st.session_state.df_resultado = df
    st.session_state.analisar = False
    st.rerun()

# Exibir resultados
if 'df_resultado' in st.session_state:
    df = st.session_state.df_resultado
    
    # Estatísticas
    st.header("📈 Estatísticas Gerais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total BDRs", len(df))
    with col2:
        excelentes = len(df[df['Status'] == '🟢 Excelente'])
        st.metric("🟢 Excelente", excelentes)
    with col3:
        bons = len(df[df['Status'] == '🟡 Bom'])
        st.metric("🟡 Bom", bons)
    with col4:
        atencao = len(df[df['Status'] == '🟠 Atenção'])
        st.metric("🟠 Atenção", atencao)
    with col5:
        fracos = len(df[df['Status'] == '🔴 Fraco'])
        st.metric("🔴 Fraco", fracos)
    
    # Gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pizza - Status
        fig_pizza = px.pie(
            df, 
            names='Status', 
            title='Distribuição por Status',
            color='Status',
            color_discrete_map={
                '🟢 Excelente': '#10b981',
                '🟡 Bom': '#f59e0b',
                '🟠 Atenção': '#f97316',
                '🔴 Fraco': '#ef4444'
            }
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col2:
        # Pizza - Tamanho
        fig_tamanho = px.pie(
            df,
            names='Tamanho',
            title='Distribuição por Tamanho',
            color='Tamanho',
            color_discrete_map={
                'Mega Cap': '#8b5cf6',
                'Large Cap': '#3b82f6',
                'Mid Cap': '#10b981',
                'Small Cap': '#f59e0b'
            }
        )
        st.plotly_chart(fig_tamanho, use_container_width=True)
    
    # Top ROE
    st.subheader("🏆 Top 15 BDRs por ROE")
    top_roe = df.nlargest(15, 'ROE (%)')
    fig_roe = px.bar(
        top_roe,
        x='ROE (%)',
        y='BDR',
        orientation='h',
        title='Top 15 por ROE',
        color='ROE (%)',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_roe, use_container_width=True)
    
    # Setores
    st.subheader("🏢 Distribuição por Setor")
    setor_count = df['Setor'].value_counts().head(10)
    fig_setor = px.bar(
        x=setor_count.values,
        y=setor_count.index,
        orientation='h',
        title='Top 10 Setores',
        labels={'x': 'Quantidade', 'y': 'Setor'}
    )
    st.plotly_chart(fig_setor, use_container_width=True)
    
    # Filtros
    st.header("🔍 Filtros e Tabela")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_status = st.multiselect(
            "Status",
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )
    
    with col2:
        filtro_setor = st.multiselect(
            "Setor",
            options=sorted(df['Setor'].unique()),
            default=sorted(df['Setor'].unique())
        )
    
    with col3:
        filtro_tamanho = st.multiselect(
            "Tamanho",
            options=df['Tamanho'].unique(),
            default=df['Tamanho'].unique()
        )
    
    with col4:
        busca = st.text_input("🔎 Buscar BDR/Ticker/Empresa")
    
    # Aplicar filtros
    df_filtrado = df[
        (df['Status'].isin(filtro_status)) &
        (df['Setor'].isin(filtro_setor)) &
        (df['Tamanho'].isin(filtro_tamanho))
    ]
    
    if busca:
        df_filtrado = df_filtrado[
            df_filtrado['BDR'].str.contains(busca, case=False) |
            df_filtrado['Ticker US'].str.contains(busca, case=False) |
            df_filtrado['Empresa'].str.contains(busca, case=False)
        ]
    
    st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df)} BDRs")
    
    # Tabela
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=600,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                format="%.1f",
                min_value=0,
                max_value=6,
            ),
            "ROE (%)": st.column_config.NumberColumn(
                "ROE (%)",
                format="%.2f%%",
            ),
            "Market Cap (B)": st.column_config.NumberColumn(
                "Market Cap (B)",
                format="$%.2fB",
            ),
        }
    )
    
    # Download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"bdrs_analise_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Legenda
    with st.expander("📖 Legenda e Critérios", expanded=False):
        st.markdown("""
        ### Classificação por Status:
        
        **🟢 Excelente (Score ≥ 80%)**
        - ROE > 20%, Margem > 15%, Crescimento > 10%
        - Dividend Yield > 2%, P/E ≤ 25
        - Dívida/PL < 50%
        
        **🟡 Bom (Score ≥ 60%)**
        - ROE > 15%, Margem > 10%, Crescimento > 5%
        - Dividend Yield > 1%, P/E ≤ 35
        - Dívida/PL < 100%
        
        **🟠 Atenção (Score ≥ 40%)**
        - ROE > 10%, Margem > 5%, Crescimento > 0%
        - Fundamentos medianos
        
        **🔴 Fraco (Score < 40%)**
        - Fundamentos abaixo dos critérios mínimos
        
        ---
        
        ### Classificação por Tamanho (Market Cap):
        
        - **💜 Mega Cap**: > $200B (Apple, Microsoft, etc.)
        - **💙 Large Cap**: $10B - $200B
        - **💚 Mid Cap**: $2B - $10B
        - **💛 Small Cap**: < $2B
        
        ---
        
        ### Indicadores Analisados:
        
        - **ROE**: Retorno sobre Patrimônio Líquido
        - **Margem**: Margem Líquida
        - **Crescimento**: Crescimento de Receita
        - **Dívida/PL**: Endividamento
        - **P/E**: Preço/Lucro (valuation)
        - **P/B**: Preço/Valor Patrimonial
        - **DY**: Dividend Yield
        - **M.Cap**: Market Cap em Bilhões USD
        
        *Análise baseada nos últimos 5 balanços das empresas-mãe via Yahoo Finance*
        """)

else:
    st.info("👈 Clique em 'Iniciar Análise' na barra lateral para começar!")
    
    st.markdown("""
    ## 🎯 Sobre esta ferramenta
    
    Esta aplicação realiza uma análise fundamentalista completa de **todas as BDRs** 
    negociadas na B3, baseando-se nos dados das empresas-mãe americanas.
    
    ### ✨ Recursos:
    
    - 📊 Análise de **centenas de BDRs**
    - 📈 Dados dos **últimos 5 balanços**
    - 🎯 Classificação por **Status**, **Setor** e **Tamanho**
    - 📉 Múltiplos **indicadores fundamentalistas**
    - 🔍 **Filtros avançados** e busca
    - 📥 **Exportação** para CSV
    - 📊 **Gráficos interativos**
    
    ### 🚀 Como usar:
    
    1. Ajuste o limite de BDRs na barra lateral
    2. Clique em "Iniciar Análise"
    3. Aguarde o processamento (pode levar alguns minutos)
    4. Explore os resultados com filtros e gráficos
    5. Exporte os dados se desejar
    
    ---
    
    **⚠️ Importante**: Esta análise é apenas informativa e não constitui 
    recomendação de investimento. Sempre faça sua própria pesquisa!
    """)
