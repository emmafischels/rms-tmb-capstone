import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Rhabdomyosarcoma TMB Analysis",
    page_icon="🧬",
    layout="wide"
)

st.title("Rhabdomyosarcoma TMB & Survival Analysis Tool")

st.write(
    """
    This interactive tool allows users to explore clinical and genomic
    data from pediatric rhabdomyosarcoma patients. Users can examine
    patient characteristics, visualize relationships between variables,
    and perform survival analyses.
    """
)

st.header("Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("Dataset successfully loaded!")

    st.subheader("Dataset Preview")

    st.dataframe(df.head())

    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Number of Patients",
            df.shape[0]
        )

    with col2:
        st.metric(
            "Number of Variables",
            df.shape[1]
        )

    st.subheader("Variables")

    st.write(df.columns.tolist())
