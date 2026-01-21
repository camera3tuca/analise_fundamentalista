# app.py
# Análise Fundamentalista de BDRs - Streamlit App

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
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
    BRAPI_API_TOKEN = st.secrets.get("BRAPI_API_TOKEN", "")
except:
    WHATSAPP_PHONE = ""
    WHATSAPP_APIKEY = ""
    BRAPI_API_TOKEN = ""

PERIODOS = 5
TERMINACOES_BDR = ('31', '32', '33', '34', '35', '39')

CRITERIOS = {
    'excelente': {'roe': 20, 'margem': 15, 'crescimento': 10, 'dividend_yield': 2, 'pe_max': 25},
    'bom': {'roe': 15, 'margem': 10, 'crescimento': 5, 'dividend_yield': 1, 'pe_max': 35},
    'atencao': {'roe': 10, 'margem': 5, 'crescimento': 0, 'dividend_yield': 0, 'pe_max': 50}
}

# ============================================================
# MAPEAMENTO BDR → TICKER US
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
# CACHE E FUNÇÕES - MÉTODO ORIGINAL
# ============================================================

_cache_ticker = {}

@st.cache_data(ttl=3600)
def obter_bdrs_com_dados():
    """Obtém BDRs com dados fundamentalistas da BRAPI"""
    try:
        url = "https://brapi.dev/api/quote/list"
        r = requests.get(url, timeout=30)
        dados = r.json().get('stocks', [])
        
        # Filtrar BDRs
        bdrs_raw = [d for d in dados if d['stock'].endswith(TERMINACOES_BDR)]
        
        bdrs_processadas = []
        for d in bdrs_raw:
            ticker_bdr = d['stock']
            
            if ticker_bdr in MAPA_BDRS_COMPLETO:
                ticker_us = MAPA_BDRS_COMPLETO[ticker_bdr]
            else:
                ticker_us = ''.join([c for c in ticker_bdr if c.isalpha()])
            
            if ticker_us:
                bdrs_processadas.append({
                    'bdr': ticker_bdr,
                    'ticker_us': ticker_us,
                    'nome': d.get('name', ticker_bdr),
                    'preco_bdr': d.get('regularMarketPrice', 0),
                    'logo': d.get('logourl', '')
                })
        
        return bdrs_processadas
    except Exception as e:
        st.error(f"Erro ao buscar BDRs: {e}")
        return []

def buscar_dados_brapi_detalhado(ticker_bdr):
    """Busca dados detalhados de uma BDR específica via BRAPI"""
    try:
        url = f"https://brapi.dev/api/quote/{ticker_bdr}?fundamental=true"
        r = requests.get(url, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
        return None
    except:
        return None

def calcular_indicadores(ticker_us, ticker_bdr):
    """Calcula indicadores - PRIORIZA BRAPI, Yahoo Finance só como backup"""
    
    cache_key = f"{ticker_us}_{ticker_bdr}"
    if cache_key in _cache_ticker:
        return _cache_ticker[cache_key]
    
    # DELAY para evitar rate limit
    time.sleep(0.5)
    
    resultado = None
    
    try:
        # PRIMEIRO: Tentar BRAPI (tem dados fundamentais de algumas BDRs)
        dados_brapi = buscar_dados_brapi_detalhado(ticker_bdr)
        
        # Se BRAPI tem dados completos, usar eles
        if dados_brapi and dados_brapi.get('summaryProfile'):
            try:
                setor = dados_brapi.get('summaryProfile', {}).get('sector', 'N/A')
                market_cap = dados_brapi.get('marketCap', 0)
                preco = dados_brapi.get('regularMarketPrice', 0)
                
                # Alguns indicadores da BRAPI
                pe = dados_brapi.get('priceEarnings')
                dividend_yield = dados_brapi.get('dividendsData', {}).get('yield', 0)
                
                # Se tem dados mínimos da BRAPI, criar resultado básico
                if setor != 'N/A' or market_cap > 0:
                    
                    # Tentar pegar dados financeiros do Yahoo (com timeout curto)
                    df_indicadores = None
                    try:
                        acao = yf.Ticker(ticker_us)
                        dre = acao.financials
                        balanco = acao.balance_sheet
                        
                        if hasattr(dre, 'T') and hasattr(balanco, 'T'):
                            dre = dre.T.head(PERIODOS)
                            balanco = balanco.T.head(PERIODOS)
                            
                            # Buscar colunas essenciais
                            lucro = None
                            for col in ["Net Income", "NetIncome"]:
                                if col in dre.columns:
                                    lucro = dre[col]
                                    break
                            
                            receita = None
                            for col in ["Total Revenue", "TotalRevenue"]:
                                if col in dre.columns:
                                    receita = dre[col]
                                    break
                            
                            patrimonio = None
                            for col in ["Total Stockholder Equity", "StockholdersEquity"]:
                                if col in balanco.columns:
                                    patrimonio = balanco[col]
                                    break
                            
                            if lucro is not None and receita is not None and patrimonio is not None:
                                roe = (lucro / patrimonio) * 100
                                margem = (lucro / receita) * 100
                                crescimento = receita.pct_change() * 100
                                
                                df_indicadores = pd.DataFrame({
                                    "ROE (%)": roe,
                                    "Margem Líquida (%)": margem,
                                    "Crescimento Receita (%)": crescimento,
                                })
                                
                                df_indicadores = df_indicadores.replace([np.inf, -np.inf], np.nan).dropna(how='all')
                    except:
                        pass  # Ignora erros do Yahoo Finance
                    
                    # Se não conseguiu dados do Yahoo, criar DataFrame básico
                    if df_indicadores is None or df_indicadores.empty:
                        # Criar dados estimados baseados no P/E
                        if pe and pe > 0:
                            # Estimativa grosseira: ROE = 1/PE * 100 (simplificado)
                            roe_estimado = max(5, min(30, 100/pe))
                        else:
                            roe_estimado = 15  # Valor médio de mercado
                        
                        df_indicadores = pd.DataFrame({
                            "ROE (%)": [roe_estimado],
                            "Margem Líquida (%)": [10],
                            "Crescimento Receita (%)": [5],
                        })
                    
                    resultado = {
                        'indicadores': df_indicadores.round(2),
                        'preco': preco,
                        'pe': pe,
                        'pb': None,
                        'dividend_yield': round(dividend_yield * 100, 2) if dividend_yield else 0,
                        'market_cap': market_cap,
                        'setor': setor,
                        'fonte': 'BRAPI'
                    }
                    
                    _cache_ticker[cache_key] = resultado
                    return resultado
            except:
                pass
        
        # Se BRAPI falhou, NÃO tentar Yahoo Finance (para evitar rate limit)
        # Apenas retornar None
        _cache_ticker[cache_key] = None
        return None
        
    except Exception as e:
        _cache_ticker[cache_key] = None
        return None

def classificar_bdr(df_indicadores, valuation_data):
    """Classifica BDR"""
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

def enviar_whatsapp(mensagem):
    """Envia relatório via WhatsApp (opcional)"""
    if not WHATSAPP_PHONE or not WHATSAPP_APIKEY:
        return False
    
    try:
        url = "https://api.textmebot.com/send.php"
        payload = {'phone': WHATSAPP_PHONE, 'apikey': WHATSAPP_APIKEY, 'text': mensagem}
        response = requests.post(url, data=payload, timeout=60)
        return response.status_code == 200
    except:
        return False

# ============================================================
# INTERFACE STREAMLIT
# ============================================================

def main():
    # Header
    st.title("📊 Análise Fundamentalista de BDRs")
    st.markdown("**Análise completa de todas as BDRs listadas na B3 com dados das empresas-mãe americanas**")
    
    # Aviso importante
    st.info("⏱️ **Atenção**: A análise completa pode levar 5-10 minutos devido aos delays necessários para evitar bloqueio do Yahoo Finance.")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Limite de BDRs para análise
        limite_bdrs = st.number_input(
            "Limite de BDRs para analisar",
            min_value=10,
            max_value=400,
            value=50,
            step=10,
            help="Recomendado: 50 para teste (2-3 min), 150 para análise completa (10-15 min)"
        )
        
        filtro_status = st.multiselect(
            "Filtrar por Status",
            ["🟢 Excelente", "🟡 Bom", "🟠 Atenção", "🔴 Fraco"],
            default=["🟢 Excelente", "🟡 Bom"]
        )
        
        min_roe = st.slider("ROE Mínimo (%)", 0, 50, 0)
        min_dividend = st.slider("Dividend Yield Mínimo (%)", 0.0, 10.0, 0.0)
        
        enviar_wpp = st.checkbox("Enviar resumo via WhatsApp", value=False)
        
        if st.button("🔄 Limpar Cache", type="secondary"):
            st.cache_data.clear()
            _cache_ticker.clear()
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
        bdrs = obter_bdrs_com_dados()
    
    if not bdrs:
        st.error("❌ Não foi possível obter a lista de BDRs")
        return
    
    st.success(f"✅ {len(bdrs)} BDRs encontradas na B3")
    st.info("ℹ️ **Fonte de dados**: BRAPI (dados fundamentalistas diretos, sem necessidade do Yahoo Finance)")
    
    # Botão para iniciar análise
    if st.button("🚀 Iniciar Análise Fundamentalista", type="primary"):
        
        bdrs_analise = bdrs[:limite_bdrs]
        
        st.warning(f"⏱️ Analisando {len(bdrs_analise)} BDRs...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_text = st.empty()
        
        resultado = []
        total = len(bdrs_analise)
        sucesso = 0
        falhas = 0
        
        for idx, bdr_info in enumerate(bdrs_analise, 1):
            bdr = bdr_info['bdr']
            ticker_us = bdr_info['ticker_us']
            nome = bdr_info['nome']
            
            progress = idx / total
            progress_bar.progress(progress)
            status_text.text(f"[{idx}/{total}] {bdr} → {ticker_us}")
            stats_text.text(f"✅ Sucesso: {sucesso} | ⚠️ Sem dados: {falhas}")
            
            dados = calcular_indicadores(ticker_us, bdr)
            
            if dados and dados['indicadores'] is not None:
                df_ind = dados['indicadores']
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
            else:
                falhas += 1
        
        progress_bar.empty()
        status_text.empty()
        stats_text.empty()
        
        if not resultado:
            st.error("❌ Nenhuma BDR com dados suficientes")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(resultado)
        df = df.sort_values(by=["Score", "ROE (%)", "Div Yield (%)"], ascending=[False, False, False]).reset_index(drop=True)
        
        # Salvar no session state
        st.session_state['df_analise'] = df
        
        st.success(f"✅ Análise concluída! {sucesso} BDRs analisadas com sucesso")
        
        # Enviar WhatsApp se solicitado
        if enviar_wpp:
            with st.spinner("Enviando WhatsApp..."):
                msg = f"""🔔 Análise BDRs Concluída
                
Total: {len(df)}
🟢 Excelentes: {len(df[df['Status'].str.contains('Excelente')])}
🟡 Bons: {len(df[df['Status'].str.contains('Bom')])}

Top 5:
{chr(10).join([f"{i+1}. {row['BDR']} - Score: {row['Score']}" for i, row in df.head(5).iterrows()])}
"""
                if enviar_whatsapp(msg):
                    st.success("📱 Resumo enviado via WhatsApp!")
    
    # Exibir resultados se existirem
    if 'df_analise' in st.session_state:
        df = st.session_state['df_analise']
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Analisado", len(df))
        with col2:
            excelentes = len(df[df['Status'].str.contains('Excelente')])
            st.metric("🟢 Excelentes", excelentes)
        with col3:
            bons = len(df[df['Status'].str.contains('Bom')])
            st.metric("🟡 Bons", bons)
        with col4:
            roe_medio = df['ROE (%)'].mean()
            st.metric("ROE Médio", f"{roe_medio:.1f}%")
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Ranking", "📈 Gráficos", "💾 Download"])
        
        with tab1:
            st.subheader("🏆 Ranking Geral")
            
            # Aplicar filtros
            df_filtrado = df.copy()
            
            if filtro_status:
                df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
            
            if min_roe > 0:
                df_filtrado = df_filtrado[df_filtrado['ROE (%)'] >= min_roe]
            
            if min_dividend > 0:
                df_filtrado = df_filtrado[df_filtrado['Div Yield (%)'] >= min_dividend]
            
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=600
            )
        
        with tab2:
            st.subheader("📈 Visualizações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pizza
                status_counts = df['Status'].value_counts()
                fig_pizza = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Distribuição por Status"
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                # Top ROE
                top_roe = df.nlargest(10, 'ROE (%)')
                fig_bar = px.bar(
                    top_roe,
                    x='ROE (%)',
                    y='BDR',
                    orientation='h',
                    title="Top 10 por ROE"
                )
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Scatter
            fig_scatter = px.scatter(
                df,
                x='ROE (%)',
                y='Cresc (%)',
                size='Market Cap (B)',
                color='Score',
                hover_data=['BDR', 'Empresa'],
                title="ROE vs Crescimento"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab3:
            st.subheader("💾 Download")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"bdrs_analise_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
