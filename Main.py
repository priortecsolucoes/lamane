import streamlit as st

class Main:
    def __init__(self):
        pass

    def main(self):
        st.set_page_config(page_title="LAMANE - INDICADORES - CONFIGURAÇÕES", layout="wide")

        st.title("LAMANE - INDICADORES - CONFIGURAÇÕES")

        # Marca
        st.subheader("Marca")
        marca = st.selectbox("Selecione a Marca:", ["O Boticário", "Quem Disse Berenice"])

        # Layout em colunas
        col1, col2, col3 = st.columns([1.5, 1.5, 1])

        # Metas por Indicador
        with col1:
            st.subheader("Metas por Indicador")

            indicador = st.selectbox("Indicador", [
                "Alcance Meta PEP",  # Substitua pelos nomes reais dos indicadores disponíveis
                "Indicador X", 
                "Indicador Y"
            ])

            pontuacao_maxima = st.number_input("Valor Pontuação Máxima", min_value=0, value=70)
            pontuacao_parcial = st.number_input("Valor Pontuação Parcial", min_value=0, max_value=pontuacao_maxima-1, value=35)
            zero_pontuacao = st.number_input("Valor Zero Pontuação", min_value=0, max_value=pontuacao_parcial-1, value=0)

        # Atingimento
        with col2:
            st.subheader("Atingimento")

            classificacao = st.selectbox("Classificação", ["Diamante", "Ouro", "Prata", "Bronze", "Não Class."])
            acima_inclusive = st.number_input("Acima de - Inclusive (%)", min_value=0, max_value=100, value=80)
            abaixo_exclusive = st.number_input("Abaixo de - Exclusive (%)", min_value=0, max_value=100, value=90)

        # Ação de Fluxo
        with col3:
            st.subheader("Ação de Fluxo")

            campanha_vigente = st.text_input("Campanha Vigente", value="Clash - Bot")
if __name__ == "__main__":
    run = Main()
    run.main()
