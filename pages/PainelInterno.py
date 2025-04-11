import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2
import random
from datetime import datetime

st.set_page_config(page_title="Lamane - Indicadores IAF", layout="wide")
pagesAcess = st.session_state.get("pagesAcess",0)
if not pagesAcess:
    st.switch_page("loginScreen.py")
access = pagesAcess[0]
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {display: none;}
        .e14lo1l1  {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

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

    def getData(self, mes):
        if mes == "Acumulado":
            date_filter = ""
        else:
            mes_num = {
                "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03", "ABRIL": "04", "MAIO": "05",
                "JUNHO": "06", "JULHO": "07", "AGOSTO": "08", "SETEMBRO": "09", "OUTUBRO": "10",
                "NOVEMBRO": "11", "DEZEMBRO": "12"
            }.get(mes, "04")  # padrão abril

            date_filter = f"AND EXTRACT(MONTH FROM thv.history_date) = {mes_num}"

        query = f"""
        SELECT 
            c."customer_name",
            MAX(CASE WHEN t.name = 'INDICADOR_ALCANCE_PEF_VALOR' THEN thv.double_value END) AS alcance_valor,
            MAX(CASE WHEN t.name = 'INDICADOR_ALCANCE_META_PEF_PONTUACAO' THEN thv.double_value END) AS alcance_pontuacao
        FROM 
            public.tag_history_value thv
        JOIN 
            public.company_tag ct ON thv.company_tag_id = ct.id
        JOIN 
            public.company c ON ct.company_id = c.id
        JOIN 
            public.tag t ON ct.tag_id = t.id
        WHERE 
            t.name IN ('INDICADOR_ALCANCE_PEF_VALOR', 'INDICADOR_ALCANCE_META_PEF_PONTUACAO')
            {date_filter}
        GROUP BY 
            c.customer_name;
        """
        try:
            return pd.read_sql_query(query, self.connection)
        except Exception as e:
            st.error(f"Erro ao buscar dados do banco: {e}")
            return pd.DataFrame()

    def main(self):
        st.title("LAMANE - INDICADORES IAF")

        # Filtros visuais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_loja = st.text_input("Nº Loja")
        with col2:
            filtro_grupo = st.text_input("Grupo")
        with col3:
            meses = [
                "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
                "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO", "Acumulado"
            ]
            mes_atual = datetime.now().month
            filtro_mes = st.selectbox("Mês/Acum.", meses, index=mes_atual - 1)
        with col4:
            filtro_meta = st.selectbox("Meta", ["Todos", "Acima da Meta", "Meta Parcial", "Abaixo da Meta"])

        col5, col6 = st.columns(2)
        with col5:
            filtro_classificacao = st.selectbox("Classificação", ["Todos", "Diamante", "Ouro", "Prata", "Bronze", "Não Class."])
        with col6:
            filtro_marca = st.selectbox("Marca", ["Todos", "Boticário", "Quem Disse Berenice"])

        df = self.getData(filtro_mes)
        if df.empty:
            st.warning("Nenhum dado encontrado.")
            return

        df.rename(columns={"customer_name": "LOJAS", "alcance_valor": "ALCANCE META PEF", "alcance_pontuacao": "ALCANCE META PEF (PONTUAÇÃO)"}, inplace=True)

        if filtro_meta == "Abaixo da Meta":
            df = df[df["ALCANCE META PEF"] < 35]
        elif filtro_meta == "Meta Parcial":
            df = df[(df["ALCANCE META PEF"] >= 35) & (df["ALCANCE META PEF"] <= 70)]
        elif filtro_meta == "Acima da Meta":
            df = df[df["ALCANCE META PEF"] > 70]

        colunas_mock = {
            "NPS (Loja + Omni)": "89,1%",
            "Penetração de Boletos Fidelidade": "92%",
            "Resgate Fidelidade": "49%",
            "Penetração Boleto Promocional": "30%",
            "Penetração Boleto Turbinado": "73%",
            "Conversão Ação de Fluxo": "86%",
            "Gestão de Categorias": "1,8%",
            "Auditoria em Lojas": "50%",
            "Separação no Prazo": "98%",
            "Missões": "45%",
            "Loja DigitalAtivo - % de Atendimento": "90%",
            "Redes Sociais": "100%",
            "Receita Transacionada": "94%",
            "ID Cliente": "82%",
            "Quant. Serviços por Loja": "73",
            "Programa de Logística Reversa": "25"
        }

        def gerar_valor(indicador):
            if "Serviços" in indicador:
                return str(random.randint(5, 100))
            elif "Gestão de Categorias" in indicador:
                return f"{random.uniform(0.5, 3.5):.2f}%"
            elif "ID Cliente" in indicador:
                return f"{random.uniform(60, 95):.2f}%"
            else:
                return f"{random.uniform(10, 100):.2f}%"

        for coluna in colunas_mock.keys():
            df[coluna] = [gerar_valor(coluna) for _ in range(len(df))]

        colunas_ordenadas = ["LOJAS", "ALCANCE META PEF", "ALCANCE META PEF (PONTUAÇÃO)"] + list(colunas_mock.keys())
        df = df[colunas_ordenadas]

        def highlight_all_indicators(val):
            style = 'border: 1px solid black;color: black;'
            try:
                valor = float(str(val).replace('%', '').replace(',', '.'))
                if valor < 35:
                    style += ' background-color: #FF9999;'
                elif 35 <= valor <= 70:
                    style += ' background-color: #FFF79A;'
                else:
                    style += ' background-color: #B6F2A5;'
            except:
                pass
            return style

        colunas_indicadores = [col for col in df.columns if col != 'LOJAS']

        styled_df = df.style.map(highlight_all_indicators, subset=colunas_indicadores) \
                            .set_properties(**{'border': '1px solid black'}) \
                            .set_properties(subset=colunas_indicadores, **{'color': 'black'}) \
                            .set_properties(subset=['LOJAS'], **{'color': 'white'}) \
                            .set_table_styles([
                                {'selector': 'th', 'props': [('border', '1px solid black'), ('background-color', '#f0f0f0')]}
                            ])

        hoje = datetime.now()
        if filtro_mes != "Acumulado":
            mes_num = {
                "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5,
                "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10,
                "NOVEMBRO": 11, "DEZEMBRO": 12
            }.get(filtro_mes, 4)  # abril como padrão
            ano_atual = hoje.year
            primeiro_dia = datetime(ano_atual, mes_num, 1)
            st.markdown(f"### Período: {primeiro_dia.strftime('%d/%m')} a {hoje.strftime('%d/%m')}")
        else:
            st.markdown(f"### Período: Acumulado até {hoje.strftime('%d/%m')}")
        st.subheader("Tabela de Indicadores")
        st.dataframe(styled_df, use_container_width=True)

        st.subheader("Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Última Execução do Agente:** 26/02/2025 14:05")
        with col2:
            st.markdown("**Status Integração - Gestão Integrada:** 🟢 Verde")
        with col3:
            st.markdown("**Status Integração - Medallia:** :red_circle: Vermelho")

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
