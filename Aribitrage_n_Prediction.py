import streamlit as st

from utils import st_def, tab_arbi
st_def.st_logo(title='👋Arbitrage🎖️and🏅Prediction🥇', page_title="🏆Win🌟")
st.warning('''
           # Disclaimer:
           
           This is not financial advice! Use forecast data to inform your own investment research. No guarantee of trading performance.
           
           Before delving into the details, it’s important to emphasize that the information provided by this app is for educational and demonstration purposes only. It should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions as past performance is not indicative of future results.
           
           This dashboard is not personal advice. It does not constitute a personal recommendation to buy, sell, or otherwise trade all or any of the investments which may be referred to. Data represented on charts is purely an illustration of dashboarding capabilities.
           
           ''')
st.image('./images/zhang.gif', use_column_width=True)
