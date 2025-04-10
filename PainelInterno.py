import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2

st.set_page_config(layout="wide")

class Main:
    def __init__(self):
        load_dotenv()
        dbHost = os.getenv('DBHOST')
        dbName = os.getenv('DBNAME')
        dbUser = os.getenv('DBUSER')
        dbPassword = os.getenv('DBPASSWORD')
        dbPort = os.getenv('DBPORT')
        self.connection = psycopg2.connect(
            database=dbName,
            host=dbHost,
            user=dbUser,
            password=dbPassword,
            port=dbPort
        )

    def main(self):
        st.title("LAMANE - INDICADORES IAF")

        # Filtros (Cabeçalho)
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                loja_num = st.text_input("Nº Loja")
                grupo = st.text_input("Grupo")
            with col2:
                loja_nome = st.text_input("Loja")
                mes_acum = st.selectbox("Mês/Acum.", ["JANEIRO", "FEVEREIRO", "MARÇO", "ACUMULADO"])
            with col3:
                indicadores = st.multiselect("Indicador", ["NPS", "Fidelidade", "Gestão de Categorias", "Digital", "Treinamento"])
                meta = st.selectbox("Meta", ["Abaixo da Meta", "Meta Parcial", "Acima da Meta"])
            with col4:
                classificacao = st.selectbox("Classificação", ["Diamante", "Ouro", "Prata", "Bronze", "Não Class."])
                marca = st.selectbox("Marca", ["Boticário", "Quem Disse Berenice"])  

        # Período
        st.markdown("### Período: 01/03 a D-1")

        # Tabela de Indicadores
        st.subheader("Tabela de Indicadores")
        data = {
            'Loja': ['Big Shopping', 'Carrefour', 'Itaú Power Shopping', 'Shopping Contagem', 'Atacadão', 'Assaí', 'Só Marcas'],
            'NPS (Loja + Omni)': [81.5, 80.0, 0.0, 100.0, 100.0, 100.0, 90.5],
            'Resgate Fidelidade': [32.07, 49.12, 36.02, 0.0, 51.43, 44.66, 49.38],
            'Penetração Boletos Fidelidade': [25.71, 30.71, 22.05, 27.45, 35.25, 27.27, 24.59],
            'Penetração Boleto Turbinado': [22.95, 26.51, 16.81, 0.0, 25.74, 17.72, 23.52],
            'Conversão Ação de Fluxo': [9.72, 9.72, 8.0, 0.0, 10.25, 5.32, 9.5],
            'Gestão de Categorias': [0.96, 0.98, 0.96, 0.0, 1.77, 0.96, 0.58],
            'Loja Digital Ativo - % de Atendimento': [76.53, 56.92, 60.0, 84.85, 60.0, 56.41, 0.0],
            'ID Cliente': [76.53, 86.06, 83.34, 57.31, 95.7, 95.0, 0.0],
            'Treinamentos Força de Vendas': [91.2, 96.06, 98.18, 100.0, 91.0, 100.0, 70.0],
            'PONTUAÇÃO': [206.00, 261.00, 206.00, 289.00, 318.00, 289.00, 234.00],
        }

        df = pd.DataFrame(data)

        def highlight_and_border(val):
            style = 'border: 1px solid black;'
            if isinstance(val, (int, float)):
                if val < 35:
                    style += ' background-color: #FF9999;'
                elif 35 <= val <= 70:
                    style += ' background-color: #FFF79A;'
                else:
                    style += ' background-color: #B6F2A5;'
            return style

        styled_df = df.style.map(highlight_and_border, subset=pd.IndexSlice[:, df.columns[1:]])\
                            .set_properties(**{'border': '3px solid black'}) \
                            .set_table_styles([
                                {'selector': 'th', 'props': [('border', '3px solid black'), ('background-color', '#f0f0f0')]}
                            ])

        st.dataframe(styled_df, use_container_width=True)

        # Status
        st.subheader("Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Última Execução do Agente:** 26/02/2025 14:05")
        with col2:
            st.markdown("**Status Integração - Gestão Integrada:**")
            st.markdown(":green_circle: Verde")
        with col3:
            st.markdown("**Status Integração - Medallia:**")
            st.markdown(":red_circle: Vermelho")

        # Logs
        st.subheader("Últimos Logs")
        st.markdown("""
        - **Indicador NPS** - Erro na obtenção dos dados  
        - **Indicador Alcance da Meta** - Calculado com sucesso  
        - **Indicador Auditoria em Lojas** - Calculado com sucesso  
        - **Indicador Missões** - Calculado com sucesso
        """)

if __name__ == "__main__":
    run = Main()
    run.main()
