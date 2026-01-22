# app.py
# Análise Fundamentalista de BDRs - MÉTODO COLAB QUE FUNCIONA

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from datetime import datetime
import time

# ============================================================
# CONFIGURAÇÕES
# ============================================================

st.set_page_config(
    page_title="Análise Fundamentalista BDRs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Secrets (configurar no Streamlit Cloud)
try:
    WHATSAPP_PHONE = st.secrets["WHATSAPP_PHONE"]
    WHATSAPP_APIKEY = st.secrets["WHATSAPP_APIKEY"]
except:
    WHATSAPP_PHONE = ""
    WHATSAPP_APIKEY = ""

PERIODOS = 5
TERMINACOES_BDR = ('31', '32', '33', '34', '35', '39')

CRITERIOS = {
    'excelente': {'roe': 20, 'margem': 15, 'crescimento': 10, 'dividend_yield': 2, 'pe_max': 25},
    'bom': {'roe': 15, 'margem': 10, 'crescimento': 5, 'dividend_yield': 1, 'pe_max': 35},
    'atencao': {'roe': 10, 'margem': 5, 'crescimento': 0, 'dividend_yield': 0, 'pe_max': 50}
}

# ============================================================
# MAPEAMENTO BDR → TICKER US (IGUAL AO COLAB)
# ============================================================

MAPA_BDRS_COMPLETO = {
    'AAPL34': 'AAPL', 'MSFT34': 'MSFT', 'GOGL34': 'GOOGL', 'AMZO34': 'AMZN',
    'NVDC34': 'NVDA', 'M1TA34': 'META', 'TSLA34': 'TSLA', 'NFLX34': 'NFLX',
    'A1MD34': 'AMD', 'ITLC34': 'INTC', 'ORCL34': 'ORCL', 'AVGO34': 'AVGO',
    'ADBE34': 'ADBE', 'CSCO34': 'CSCO', 'QCOM34': 'QCOM', 'TXAS34': 'TXN',
    'I2BM34': 'IBM', 'S2EA34': 'EA', 'ROXO34': 'RBLX', 'C2OI34': 'COIN',
    'P2LT34': 'PLTR', 'MUTC34': 'MU', 'M2RV34': 'MRVL', 'VISA34': 'V',
    'V2SA34': 'V', 'M2ST34': 'MA', 'PYPL34': 'PYPL', 'BERK34': 'BRK-B',
    'CTGP34': 'C', 'PAGS34': 'PAGS', 'STOC34': 'STNE', 'WALM34': 'WMT',
    'COCA34': 'KO', 'P3EP34': 'PEP', 'PGCO34': 'PG', 'NIKE34': 'NKE',
    'M1CD34': 'MCD', 'H0MC34': 'HD', 'DISB34': 'DIS', 'JNJB34': 'JNJ',
    'LILY34': 'LLY', 'ABBV34': 'ABBV', 'P1FE34': 'PFE', 'EXXO34': 'XOM',
    'CHVX34': 'CVX', 'BOEI34': 'BA', 'C1AT34': 'CAT', 'D1EE34': 'DE',
    'U2PS34': 'UPS', 'FCXO34': 'FCX', 'N1VO34': 'NEM', 'F2NV34': 'FNV',
    'A2RR34': 'ARR', 'BABA34': 'BABA', 'BIDU34': 'BIDU', 'MELI34': 'MELI',
    'REGN34': 'REGN', 'BKNG34': 'BKNG', 'CMCS34': 'CMCSA', 'EQIX34': 'EQIX',
    'A1MT34': 'AMT', 'P1LD34': 'PLD', 'MDLZ34': 'MDLZ', 'SCHW34': 'SCHW',
    'RGTI34': 'RGTI', 'T2DH34': 'TDG', 'DUOL34': 'DUOL', 'B1AX34': 'BAX',
    'TSMC34': 'TSM', 'ASML34': 'ASML', 'N1VS34': 'NVS', 'D1HI34': 'DHI',
    'GPRK34': 'GPRK', 'C1NS34': 'CNS', 'T2ER34': 'TER', 'F1MC34': 'FMC',
    'G1LO34': 'GLOB', 'T1RI34': 'TRI', 'R1MD34': 'RMD', 'S2NA34': 'SNA',
    'A1MP34': 'AMP', 'G1SK34': 'GSK',
}

# ============================================================
# FUNÇÕES - EXATAMENTE COMO NO COLAB
# ============================================================

@st.cache_data(ttl=3600)
def obter_bdrs():
    """Obtém lista de BDRs via BRAPI - MÉTODO ORIGINAL DO COLAB"""
    try:
        url = "https://brapi.dev/api/quote/list"
        r = requests.get(url, timeout=30)
        dados = r.json().get('stocks', [])
        
        bdrs_raw = [d for d in dados if d['stock'].endswith(TERMINACOES_BDR)]
        lista_tickers = [d['stock'] for d in bdrs_raw]
        mapa_nomes = {d['stock']: d.get('name', d['stock']) for d in bdrs_raw}
        
        bdrs_processadas = []
        for ticker_bdr in lista_tickers:
            if ticker_bdr in MAPA_BDRS_COMPLETO:
                ticker_us = MAPA_BDRS_COMPLETO[ticker_bdr]
            else:
                ticker_us = ''.join([c for c in ticker_bdr if c.isalpha()])
            
            if ticker_us:
                bdrs_processadas.append((
                    ticker_bdr, 
                    ticker_us, 
                    mapa_nomes.get(ticker_bdr, ticker_bdr)
                ))
        
        return bdrs_processadas
    except Exception as e:
        st.error(f"Erro ao buscar BDRs: {e}")
        return []

def calcular_indicadores_empresa_mae(ticker_us):
    """Busca dados fundamentalistas - EXATAMENTE COMO NO COLAB"""
    try:
        acao = yf.Ticker(ticker_us)
        
        # Obter demonstrativos
        dre = acao.financials
        balanco = acao.balance_sheet
        info = acao.info
        
        # Validar dados básicos
        if dre.empty or balanco.empty:
            return None
        
        # Transpor e limitar períodos
        if hasattr(dre, 'T'):
            dre = dre.T
        if hasattr(balanco, 'T'):
            balanco = balanco.T
            
        dre = dre.head(PERIODOS)
        balanco = balanco.head(PERIODOS)
        
        # Extrair métricas - buscar em múltiplos nomes de colunas
        lucro = None
        for col_name in ["Net Income", "NetIncome", "Net Income Common Stockholders"]:
            if col_name in dre.columns:
                lucro = dre[col_name]
                break
        
        receita = None
        for col_name in ["Total Revenue", "TotalRevenue", "Total Revenues"]:
            if col_name in dre.columns:
                receita = dre[col_name]
                break
        
        patrimonio = None
        for col_name in ["Total Stockholder Equity", "Stockholders Equity", 
                        "StockholdersEquity", "Total Equity Gross Minority Interest"]:
            if col_name in balanco.columns:
                patrimonio = balanco[col_name]
                break
        
        ativo_total = None
        for col_name in ["Total Assets", "TotalAssets"]:
            if col_name in balanco.columns:
                ativo_total = balanco[col_name]
                break
        
        divida_total = None
        for col_name in ["Total Debt", "Long Term Debt", "TotalDebt"]:
            if col_name in balanco.columns:
                divida_total = balanco[col_name]
                break
        
        # Validação
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
        
        # DataFrame de indicadores
        df_indicadores = pd.DataFrame({
            "ROE (%)": roe,
            "ROA (%)": roa,
            "Margem Líquida (%)": margem_liquida,
            "Crescimento Receita (%)": crescimento_receita,
            "Dívida/PL (%)": divida_pl,
        })
        
        df_limpo = df_indicadores.replace([np.inf, -np.inf], np.nan).dropna(how='all')
        
        if df_limpo.empty or len(df_limpo) < 2:
            return None
        
        # Dados de mercado
        preco_atual = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        pe_ratio = info.get('trailingPE') or info.get('forwardPE')
        pb_ratio = info.get('priceToBook')
        
        dividend_yield = 0
        if info.get('dividendYield'):
            dividend_yield = info.get('dividendYield') * 100
        
        market_cap = info.get('marketCap') or info.get('enterpriseValue') or 0
        setor = info.get('sector') or info.get('industry') or 'N/A'
        
        return {
            'indicadores': df_limpo.round(2),
            'preco': preco_atual,
            'pe': pe_ratio,
            'pb': pb_ratio,
            'dividend_yield': round(dividend_yield, 2),
            'market_cap': market_cap,
            'setor': setor
        }
        
    except Exception as e:
        return None

def classificar_bdr(df_indicadores, valuation_data):
    """Classifica BDR - IGUAL AO COLAB"""
    score = 0
    max_score = 6
    alertas = []
    
    roe_medio = df_indicadores["ROE (%)"].mean()
    margem_media = df_indicadores["Margem Líquida (%)"].mean()
    crescimento_medio = df_indicadores["Crescimento Receita (%)"].mean()
    divida_pl = df_indicadores["Dívida/PL (%)"].mean()
    
    pe = valuation_data.get('pe')
    dividend_yield = valuation_data.get('dividend_yield', 0)
    
    if roe_medio >= CRITERIOS['excelente']['roe']:
        score += 1
    elif roe_medio >= CRITERIOS['bom']['roe']:
        score += 0.5
    else:
        alertas.append("ROE baixo")
    
    if margem_media >= CRITERIOS['excelente']['margem']:
        score += 1
    elif margem_media >= CRITERIOS['bom']['margem']:
        score += 0.5
    else:
        alertas.append("Margem baixa")
    
    if crescimento_medio >= CRITERIOS['excelente']['crescimento']:
        score += 1
    elif crescimento_medio >= CRITERIOS['bom']['crescimento']:
        score += 0.5
    elif crescimento_medio < 0:
        alertas.append("Receita em queda")
    
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
            alertas.append("P/E elevado")
    
    if not np.isnan(divida_pl):
        if divida_pl < 50:
            score += 1
        elif divida_pl < 100:
            score += 0.5
        else:
            alertas.append("Endividamento alto")
    
    percentual = (score / max_score) * 100
    
    if percentual >= 80:
        status = "🟢 Excelente"
    elif percentual >= 60:
        status = "🟡 Bom"
    elif percentual >= 40:
        status = "🟠 Atenção"
    else:
        status = "🔴 Fraco"
    
    return status, score, alertas

# ============================================================
# INTERFACE STREAMLIT
# ============================================================

def main():
    st.title("📊 Análise Fundamentalista de BDRs")
    st.markdown("**Análise baseada em dados REAIS das empresas-mãe americanas (Yahoo Finance)**")
    
    st.warning("""
    ⚠️ **IMPORTANTE**: 
    - Dados obtidos diretamente dos **demonstrativos financeiros** via Yahoo Finance
    - **ROE, Margem e Crescimento** são calculados a partir de DRE e Balanço Patrimonial REAIS
    - Recomendado: **30-50 BDRs** por análise (~2-3 minutos)
    - Delay de 2s entre requisições para evitar bloqueio
    """)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        limite_bdrs = st.number_input(
            "Número de BDRs para analisar",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            help="Máximo recomendado: 50 BDRs"
        )
        
        filtro_status = st.multiselect(
            "Filtrar por Status",
            ["🟢 Excelente", "🟡 Bom", "🟠 Atenção", "🔴 Fraco"],
            default=["🟢 Excelente", "🟡 Bom"]
        )
        
        min_roe = st.slider("ROE Mínimo (%)", 0, 50, 0)
        min_dividend = st.slider("Dividend Yield Mínimo (%)", 0.0, 10.0, 0.0)
        
        if st.button("🔄 Limpar Cache"):
            st.cache_data.clear()
            st.success("Cache limpo!")
        
        st.markdown("---")
        st.markdown("### 📖 Legenda")
        st.markdown("""
        - 🟢 **Excelente**: Score ≥ 80%
        - 🟡 **Bom**: Score ≥ 60%
        - 🟠 **Atenção**: Score ≥ 40%
        - 🔴 **Fraco**: Score < 40%
        """)
    
    # Buscar BDRs
    with st.spinner("Buscando BDRs da B3..."):
        bdrs = obter_bdrs()
    
    if not bdrs:
        st.error("❌ Não foi possível obter a lista de BDRs")
        return
    
    st.success(f"✅ {len(bdrs)} BDRs encontradas na B3")
    
    # Mostrar exemplos de mapeamento
    with st.expander("📋 Ver Exemplos de Mapeamento BDR → US"):
        exemplos = bdrs[:10]
        for bdr, us, nome in exemplos:
            st.text(f"{bdr} → {us} ({nome})")
    
    # Mostrar exemplos de mapeamento
    with st.expander("📋 Ver Exemplos de Mapeamento BDR → US"):
        exemplos = bdrs[:10]
        for bdr, us, nome in exemplos:
            st.text(f"{bdr} → {us} ({nome})")
    
    # Botão de análise
    if st.button("🚀 Iniciar Análise Fundamentalista", type="primary"):
        
        bdrs_analise = bdrs[:limite_bdrs]
        
        st.info(f"🔄 Analisando {len(bdrs_analise)} BDRs... Tempo estimado: ~{len(bdrs_analise)*2//60} minutos")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_container = st.empty()
        log_container = st.expander("📝 Log Detalhado", expanded=False)
        
        resultado = []
        total = len(bdrs_analise)
        sucesso = 0
        falhas = 0
        logs = []
        
        for idx, (bdr, ticker_us, nome) in enumerate(bdrs_analise, 1):
            progress = idx / total
            progress_bar.progress(progress)
            status_text.text(f"[{idx}/{total}] {bdr} → {ticker_us}")
            stats_container.info(f"✅ Sucesso: {sucesso} | ⚠️ Sem dados: {falhas}")
            
            # DELAY CRÍTICO para evitar rate limit (2 segundos)
            time.sleep(2)
            
            log_msg = f"[{idx}] Buscando {ticker_us}..."
            logs.append(log_msg)
            
            try:
                dados = calcular_indicadores_empresa_mae(ticker_us)
                
                if dados and dados['indicadores'] is not None:
                    df_ind = dados['indicadores']
                    
                    # Verificar se tem dados válidos
                    if len(df_ind) > 0:
                        media = df_ind.mean()
                        status, score, alertas = classificar_bdr(df_ind, dados)
                        
                        resultado.append({
                            "BDR": bdr,
                            "Ticker US": ticker_us,
                            "Empresa": nome.split()[0] if nome else ticker_us,
                            "Setor": dados.get('setor', 'N/A'),
                            "Status": status,
                            "Score": round(score, 1),
                            "ROE (%)": round(media.get("ROE (%)", np.nan), 2),
                            "Margem (%)": round(media.get("Margem Líquida (%)", np.nan), 2),
                            "Cresc (%)": round(media.get("Crescimento Receita (%)", np.nan), 2),
                            "P/E": round(dados.get('pe'), 2) if dados.get('pe') else np.nan,
                            "Div Yield (%)": dados.get('dividend_yield', 0),
                            "Market Cap (B)": round(dados.get('market_cap', 0) / 1e9, 2),
                            "Alertas": ", ".join(alertas) if alertas else "OK"
                        })
                        sucesso += 1
                        logs.append(f"  ✅ Sucesso: {len(df_ind)} períodos")
                    else:
                        falhas += 1
                        logs.append(f"  ⚠️ DataFrame vazio")
                else:
                    falhas += 1
                    logs.append(f"  ⚠️ Sem dados")
                    
            except Exception as e:
                falhas += 1
                logs.append(f"  ❌ Erro: {str(e)[:100]}")
            
            # Atualizar log
            with log_container:
                st.text("\n".join(logs[-20:]))  # Últimas 20 linhas
        
        progress_bar.empty()
        status_text.empty()
        stats_container.empty()
        
        if not resultado:
            st.error("❌ Nenhuma BDR com dados suficientes")
            return
        
        df = pd.DataFrame(resultado)
        df = df.sort_values(by=["Score", "ROE (%)", "Div Yield (%)"], ascending=[False, False, False]).reset_index(drop=True)
        
        st.session_state['df_analise'] = df
        st.success(f"✅ Análise concluída! {sucesso} BDRs analisadas")
    
    # Exibir resultados
    if 'df_analise' in st.session_state:
        df = st.session_state['df_analise']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("🟢 Excelentes", len(df[df['Status'].str.contains('Excelente')]))
        with col3:
            st.metric("🟡 Bons", len(df[df['Status'].str.contains('Bom')]))
        with col4:
            st.metric("ROE Médio", f"{df['ROE (%)'].mean():.1f}%")
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["📊 Ranking", "📈 Gráficos", "💾 Download"])
        
        with tab1:
            st.subheader("🏆 Ranking")
            
            df_filtrado = df.copy()
            if filtro_status:
                df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
            if min_roe > 0:
                df_filtrado = df_filtrado[df_filtrado['ROE (%)'] >= min_roe]
            if min_dividend > 0:
                df_filtrado = df_filtrado[df_filtrado['Div Yield (%)'] >= min_dividend]
            
            st.dataframe(df_filtrado, use_container_width=True, height=600)
        
        with tab2:
            st.subheader("📈 Visualizações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df['Status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                            title="Distribuição por Status")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                top_roe = df.nlargest(10, 'ROE (%)')
                fig = px.bar(top_roe, x='ROE (%)', y='BDR', orientation='h',
                            title="Top 10 por ROE")
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            fig = px.scatter(df, x='ROE (%)', y='Cresc (%)', size='Market Cap (B)',
                           color='Score', hover_data=['BDR', 'Empresa'],
                           title="ROE vs Crescimento")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                f"bdrs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()
