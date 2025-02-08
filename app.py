import streamlit as st
import pandas as pd
import numpy as np

def calcular_price(valor_imovel, entrada, taxa_juros_anual, prazo_meses):
    valor_financiado = valor_imovel - entrada
    taxa_juros_mensal = (1 + taxa_juros_anual) ** (1/12) - 1
    
    # Cálculo da parcela usando Sistema PRICE
    parcela = valor_financiado * (
        (taxa_juros_mensal * (1 + taxa_juros_mensal) ** prazo_meses) /
        ((1 + taxa_juros_mensal) ** prazo_meses - 1)
    )
    
    # Criando a tabela de amortização
    tabela = []
    saldo_devedor = valor_financiado
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_juros_mensal
        amortizacao = parcela - juros
        saldo_devedor -= amortizacao
        
        tabela.append({
            'Mês': mes,
            'Prestação': parcela,
            'Amortização': amortizacao,
            'Juros': juros,
            'Saldo Devedor': max(0, saldo_devedor)
        })
    
    return pd.DataFrame(tabela)

def calcular_sac(valor_imovel, entrada, taxa_juros_anual, prazo_meses):
    valor_financiado = valor_imovel - entrada
    taxa_juros_mensal = (1 + taxa_juros_anual) ** (1/12) - 1
    
    # Amortização constante
    amortizacao = valor_financiado / prazo_meses
    
    # Criando a tabela de amortização
    tabela = []
    saldo_devedor = valor_financiado
    
    for mes in range(1, prazo_meses + 1):
        juros = saldo_devedor * taxa_juros_mensal
        prestacao = amortizacao + juros
        saldo_devedor -= amortizacao
        
        tabela.append({
            'Mês': mes,
            'Prestação': prestacao,
            'Amortização': amortizacao,
            'Juros': juros,
            'Saldo Devedor': max(0, saldo_devedor)
        })
    
    return pd.DataFrame(tabela)

# Interface do Streamlit
st.set_page_config(page_title="Calculadora de Financiamento Imobiliário", layout="wide")

st.title("Calculadora de Financiamento Imobiliário")

# Seção de informações e notas explicativas
with st.expander("📚 Notas Explicativas e Dicas de Análise", expanded=False):
    st.markdown("""
    ### Entendendo os Sistemas de Amortização
    
    #### Sistema PRICE
    - Caracterizado por **prestações fixas** ao longo de todo o financiamento
    - No início, a maior parte da prestação é composta por juros
    - Com o tempo, a proporção se inverte: mais amortização e menos juros
    - Bom para quem precisa de previsibilidade no orçamento mensal
    
    #### Sistema SAC
    - Caracterizado por **amortização constante**
    - Prestações **decrescentes** ao longo do tempo
    - Prestações iniciais mais altas que no sistema PRICE
    - Total de juros pago é menor que no sistema PRICE
    - Bom para quem pode pagar mais no início e quer economizar no total
    
    ### Como Analisar sua Simulação
    
    1. **Comprometimento da Renda**
        - A prestação não deve ultrapassar 30% da renda familiar
        - Considere a prestação mais alta (primeira parcela no SAC)
        - Lembre-se de incluir condomínio, IPTU e seguros no planejamento
    
    2. **Valor da Entrada**
        - Quanto maior a entrada, menos juros você pagará no total
        - Entrada mínima geralmente é 20% do valor do imóvel
        - Considere usar FGTS para aumentar a entrada, se possível
    
    3. **Escolha do Sistema**
        - Compare o total de juros pagos em cada sistema
        - Analise sua capacidade de pagamento atual vs. futura
        - SAC: se puder pagar mais no início, economizará no total
        - PRICE: se precisar de prestações fixas para planejamento
    
    4. **Análise do Custo Total**
        - Some todas as prestações para ver o custo total
        - Compare com o valor do imóvel para ver o custo do financiamento
        - Avalie se vale a pena juntar mais entrada para reduzir juros
    
    ### Dicas Importantes
    
    - Compare simulações com diferentes prazos e valores de entrada
    - Considere a possibilidade de amortizações extraordinárias
    - Verifique se há seguros obrigatórios e outros custos
    - Pesquise as taxas de juros em diferentes bancos
    - Mantenha uma reserva de emergência para imprevistos
    """)

# Inputs do usuário
col1, col2 = st.columns(2)

with col1:
    valor_imovel = st.number_input(
        "Valor do Imóvel (R$)", 
        min_value=50000.0,
        value=300000.0,
        step=10000.0,
        format="%.2f"
    )
    
    entrada = st.number_input(
        "Valor da Entrada (R$)",
        min_value=0.0,
        max_value=valor_imovel,
        value=valor_imovel * 0.20,  # 20% de entrada como padrão
        step=10000.0,
        format="%.2f"
    )

with col2:
    taxa_juros_anual = st.number_input(
        "Taxa de Juros Anual (%)",
        min_value=0.1,
        max_value=30.0,
        value=10.0,
        step=0.1,
        format="%.2f"
    ) / 100
    
    prazo_meses = st.number_input(
        "Prazo (meses)",
        min_value=12,
        max_value=420,  # 35 anos
        value=240,      # 20 anos
        step=12
    )

# Calcular porcentagem de entrada
porcentagem_entrada = (entrada / valor_imovel) * 100
if porcentagem_entrada < 20:
    st.warning("⚠️ Atenção: A entrada está abaixo de 20% do valor do imóvel, o que pode dificultar a aprovação do financiamento.")

sistema = st.radio(
    "Sistema de Amortização",
    ["PRICE", "SAC"],
    horizontal=True,
    help="PRICE: parcelas fixas | SAC: parcelas decrescentes"
)

if st.button("Calcular"):
    # Calcular financiamento
    if sistema == "PRICE":
        df = calcular_price(valor_imovel, entrada, taxa_juros_anual, prazo_meses)
        titulo_sistema = "Sistema PRICE"
    else:
        df = calcular_sac(valor_imovel, entrada, taxa_juros_anual, prazo_meses)
        titulo_sistema = "Sistema SAC"
    
    # Calcular métricas importantes
    total_pago = df['Prestação'].astype(float).sum()
    total_juros = df['Juros'].astype(float).sum()
    custo_efetivo = (total_pago / (valor_imovel - entrada) - 1) * 100
    
    # Formatar valores monetários
    for coluna in ['Prestação', 'Amortização', 'Juros', 'Saldo Devedor']:
        df[coluna] = df[coluna].map('R$ {:,.2f}'.format)
    
    # Mostrar resultados
    st.subheader(f"Resultados do Financiamento - {titulo_sistema}")
    
    # Informações gerais em duas linhas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valor Financiado", f"R$ {valor_imovel - entrada:,.2f}")
        st.metric("Total de Juros", f"R$ {total_juros:,.2f}")
    with col2:
        st.metric("Primeira Parcela", df.iloc[0]['Prestação'])
        st.metric("Custo Efetivo Total", f"{custo_efetivo:.1f}%")
    with col3:
        st.metric("Última Parcela", df.iloc[-1]['Prestação'])
        st.metric("Total Pago", f"R$ {total_pago:,.2f}")
    
    # Tabela de amortização
    st.subheader("Tabela de Amortização")
    st.dataframe(df, use_container_width=True)
    
    # Download da tabela
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download da Tabela (CSV)",
        csv,
        "tabela_financiamento.csv",
        "text/csv",
        key='download-csv'
    )

    # Análise adicional
    st.subheader("Análise do Financiamento")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        💰 **Análise de Custos**
        - Valor do imóvel: R$ {valor_imovel:,.2f}
        - Entrada: R$ {entrada:,.2f} ({porcentagem_entrada:.1f}%)
        - Total de juros: R$ {total_juros:,.2f}
        - Valor total pago: R$ {total_pago:,.2f}
        """)
    
    with col2:
        st.info(f"""
        📊 **Informações Importantes**
        - Sistema escolhido: {sistema}
        - Taxa de juros: {taxa_juros_anual*100:.2f}% ao ano
        - Prazo: {prazo_meses} meses ({prazo_meses//12} anos e {prazo_meses%12} meses)
        - Custo efetivo total: {custo_efetivo:.1f}%
        """)
