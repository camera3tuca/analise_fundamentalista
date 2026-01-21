# 📊 Análise Fundamentalista de BDRs

Aplicação web para análise fundamentalista completa de todas as BDRs (Brazilian Depositary Receipts) listadas na B3, baseada nos dados das empresas-mãe americanas.

## 🚀 Deploy no Streamlit Cloud

### Passo 1: Criar Repositório no GitHub

1. Crie um novo repositório no GitHub (ex: `analise-bdrs`)
2. Adicione os arquivos:
   - `app.py` (código principal)
   - `requirements.txt` (dependências)
   - `README.md` (este arquivo)

### Passo 2: Configurar Secrets (Opcional)

No Streamlit Cloud, vá em **App settings → Secrets** e adicione:

```toml
# WhatsApp (opcional - para envio de notificações)
WHATSAPP_PHONE = "+556299755774"
WHATSAPP_APIKEY = "sua_chave_aqui"

# BRAPI Token (opcional - funciona sem também)
BRAPI_API_TOKEN = "seu_token_aqui"
```

**Nota**: Os secrets são opcionais. O app funciona perfeitamente sem eles!

### Passo 3: Deploy no Streamlit

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Clique em "New app"
4. Selecione:
   - **Repository**: seu repositório (ex: `usuario/analise-bdrs`)
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Clique em "Deploy!"

🎉 Pronto! Seu app estará online em alguns minutos!

## 📋 Funcionalidades

### ✅ Análise Completa
- Busca automática de **TODAS as BDRs** da B3 via BRAPI
- Análise fundamentalista das empresas-mãe americanas
- Sistema de classificação inteligente (Excelente, Bom, Atenção, Fraco)

### 📊 Indicadores Analisados
- **ROE** (Return on Equity)
- **Margem Líquida**
- **Crescimento de Receita**
- **P/E Ratio** (Valuation)
- **Dividend Yield**
- **Dívida/Patrimônio**

### 🎯 Recursos do App
- **Ranking Geral**: Tabela interativa com todas as BDRs analisadas
- **Gráficos Dinâmicos**: 
  - Distribuição por status
  - Top 10 por ROE
  - ROE vs Crescimento (scatter)
  - Distribuição por setores
- **Filtros Avançados**:
  - Por status (Excelente, Bom, Atenção, Fraco)
  - Por setor
  - ROE mínimo
  - Dividend Yield mínimo
- **Análise Detalhada**: View completa de cada BDR
- **Download**: Exportação em CSV dos resultados

## 🛠️ Estrutura dos Arquivos

```
analise-bdrs/
│
├── app.py              # Aplicação Streamlit
├── requirements.txt    # Dependências Python
└── README.md          # Documentação
```

## 📈 Como Usar

1. **Acesse o app** (URL do Streamlit Cloud após deploy)
2. **Clique em "🚀 Iniciar Análise Completa"**
3. Aguarde o processamento (pode levar alguns minutos)
4. **Explore os resultados**:
   - Veja o ranking completo
   - Analise os gráficos
   - Filtre por critérios
   - Faça download dos dados

## 🎨 Interface

### Tela Principal
- Métricas resumidas (Total, Excelentes, Bons, ROE Médio)
- 4 abas principais: Ranking, Gráficos, Detalhes, Download

### Sidebar
- Filtros configuráveis
- Botão de atualização
- Legenda explicativa

## 🔧 Tecnologias Utilizadas

- **Streamlit**: Framework web
- **yfinance**: Dados financeiros
- **Pandas/Numpy**: Análise de dados
- **Plotly**: Gráficos interativos
- **BRAPI**: Lista de BDRs da B3

## 📊 Sistema de Classificação

| Status | Critério | Score |
|--------|----------|-------|
| 🟢 Excelente | Score ≥ 80% | 5.0-6.0 |
| 🟡 Bom | Score ≥ 60% | 4.0-4.9 |
| 🟠 Atenção | Score ≥ 40% | 2.5-3.9 |
| 🔴 Fraco | Score < 40% | 0-2.4 |

### Critérios de Pontuação (max 6 pontos)

1. **ROE** > 20% (Excelente) ou > 15% (Bom)
2. **Margem** > 15% (Excelente) ou > 10% (Bom)
3. **Crescimento** > 10% (Excelente) ou > 5% (Bom)
4. **Dividend Yield** > 2% (Excelente) ou > 1% (Bom)
5. **P/E** < 25 (Excelente) ou < 35 (Bom)
6. **Dívida/PL** < 50% (Excelente) ou < 100% (Bom)

## ⚠️ Observações

- **Rate Limiting**: O app usa delays de 1-3 segundos entre requisições para evitar bloqueio do Yahoo Finance
- **Tempo de Análise**: 
  - 50 BDRs: ~2-3 minutos
  - 150 BDRs: ~10-15 minutos
  - 400 BDRs: ~30-40 minutos
- **Cache**: Dados são armazenados em cache por 1 hora
- **Secrets**: WhatsApp e BRAPI são opcionais - o app funciona sem eles
- **BRAPI**: Usa o método original (sem autenticação) que funciona perfeitamente

## 🤝 Contribuições

Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Fazer fork e criar pull requests

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 👨‍💻 Autor

Desenvolvido para análise de investimentos em BDRs na B3.

---

**⚠️ Disclaimer**: Esta aplicação é apenas para fins educacionais e informativos. Não constitui recomendação de investimento. Consulte sempre um profissional certificado antes de tomar decisões de investimento.
