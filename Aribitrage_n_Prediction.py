import streamlit as st

from utils import st_def, tab_arbi
st_def.st_logo(title='👋Arbitrage🎖️and🏅Prediction🥇', page_title="🏆Win🌟")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    ["🔰General", "🚦Buy Sell Signal🚥", "🍨Chunking➡️", "Embedding➡️", "Vector➡️", "Retrieval➡️", "Q&A➡️", "Evaluation🏅"])

with tab1:  tab_arbi.arbi_general()
with tab8:  tab_arbi.arbi_evaluation()


