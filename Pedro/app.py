import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

st.title("Oficina: Análise de acidentes com Streamlit")
st.markdown("Vamos desenvolver o código passo a passo!")

# =============================================================================
# Sidebar: Upload de CSV e de Imagem
# =============================================================================

# Exibe a imagem na sidebar, se carregada

st.sidebar.header("Uploads")
logo = st.sidebar.file_uploader("Selecione uma imagem", type=["png", "jpg", "jpeg"])
if logo:
    st.sidebar.image(logo, caption="Imagem", use_container_width=True)


arquivo = st.sidebar.file_uploader("Selecione o arquivo CSV", type="csv")


# =============================================================================
# Passo 1: Carregar os Dados
# =============================================================================
if arquivo:
    try:
        # Ajuste o encoding e separador conforme necessário
        df = pd.read_csv(arquivo, sep=",")
        st.success("Dados carregados com sucesso!")
        st.write("Visualização dos 5 primeiros registros:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")

# =============================================================================
# Passo 2: Transformar Colunas
# =============================================================================
if arquivo:
    st.header("Passo 2: Transformar Colunas")
    st.markdown("Converter as colunas **latitude**, **longitude** e **km** de string para float e criar colunas derivadas.")

    if st.button("Executar transformação"):
        try:
            # Converter as colunas numéricas
            for col in ['km', 'latitude', 'longitude']:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float, errors='ignore')
            
            # Converter 'data_inversa' para datetime e extrair o ano
            df['data_inversa'] = pd.to_datetime(df['data_inversa'])
            df['year'] = df['data_inversa'].dt.year

            # Converter 'horario' para datetime e extrair a hora
            df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S', errors='coerce')
            df['HORA'] = df['horario'].dt.hour.fillna(-1).astype(int)

            # Criar coluna PERIODO_DIA com base na coluna 'HORA'
            bins = [-1, 4, 11, 17, 23]  # Limites para definir os períodos do dia
            labels = ['MADRUGADA', 'MANHÃ', 'TARDE', 'NOITE']
            df['PERIODO_DIA'] = pd.cut(df['HORA'], bins=bins, labels=labels, include_lowest=True, right=True)
            # Adiciona categoria 'DESCONHECIDO' para horas fora do intervalo esperado
            df['PERIODO_DIA'] = df['PERIODO_DIA'].cat.add_categories(['DESCONHECIDO'])
            df.loc[df['HORA'] < 0, 'PERIODO_DIA'] = 'DESCONHECIDO'
            df.loc[df['HORA'] >= 24, 'PERIODO_DIA'] = 'DESCONHECIDO'
            
            st.success("Colunas transformadas com sucesso!")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erro na transformação: {e}")

# =============================================================================
# Passo 3: Análise Exploratória
# =============================================================================
if arquivo:
    st.header("Passo 3: Análise Exploratória")
    st.markdown("""
    Vamos explorar os dados com análises relevantes, como:
    - Número total de acidentes
    - Acidentes com mortos (número de ocorrências e total de mortes)
    - Matriz de correlação entre variáveis numéricas
    """)

    if st.button("Executar análises exploratórias"):
        try:
            # Número total de acidentes
            total_acidentes = df.shape[0]
            st.write(f"**Número total de acidentes:** {total_acidentes}")

            # Filtrar acidentes com mortos
            if "mortos" in df.columns:
                df_mortos = df[df["mortos"] > 0]
                total_acidentes_mortos = df_mortos.shape[0]
                total_mortes = df_mortos["mortos"].sum()
                st.write(f"**Número de acidentes com mortos:** {total_acidentes_mortos}")
                st.write(f"**Número total de mortes:** {total_mortes}")
            else:
                st.write("Coluna 'mortos' não encontrada.")
            
            # Matriz de Correlação entre variáveis numéricas
            st.subheader("Matriz de Correlação")
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr()
                fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax_corr)
                ax_corr.set_title("Matriz de Correlação")
                st.pyplot(fig_corr)
            else:
                st.write("Poucas colunas numéricas para calcular a correlação.")
            
        except Exception as e:
            st.error(f"Erro na análise exploratória: {e}")

# =============================================================================
# Passo 4: Gráficos Adicionais
# =============================================================================
if arquivo:
    st.header("Passo 4: Gráficos Adicionais")
    st.markdown("Exibir gráficos relacionados aos acidentes:")

    # Gráfico: Acidentes por tipo
    if "tipo_acidente" in df.columns:
        contagem = df["tipo_acidente"].value_counts()
        st.subheader("Acidentes por Tipo")
        st.bar_chart(contagem)
    else:
        st.write("Coluna 'tipo_acidente' não encontrada.")

    # Gráfico: Top 10 cidades com mais acidentes
    if "municipio" in df.columns:
        top_cidades = df['municipio'].value_counts().head(10)
        st.subheader("Top 10 Cidades com Mais Acidentes")
        st.bar_chart(top_cidades)
    else:
        st.write("Coluna 'municipio' não encontrada.")

    # Gráfico: Distribuição da coluna 'classificacao_acidente'
    st.subheader("Distribuição da Coluna 'classificacao_acidente'")
    if 'classificacao_acidente' in df.columns:
        distrib = df['classificacao_acidente'].value_counts()
        st.bar_chart(distrib)
    else:
        st.write("Coluna 'classificacao_acidente' não encontrada.")
