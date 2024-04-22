import streamlit as st
from utils import st_def, tab_arbi
import requests, os, time
from requests.exceptions import HTTPError, Timeout
import pandas as pd, numpy as np
from scipy.signal import argrelextrema


st_def.st_logo(title='🚦Buy Sell Signal🚥', page_title="🚦Buy Sell Signal🚥",)
# #-----------------------------------------------
tab1, tab2, tab3 = st.tabs(["🔰Introduction", "Signals", "Conclusion🏅"])

with tab1: tab_arbi.introduction()
with tab2: tab_arbi.signals()


# https://stock-signal-generator-vps.streamlit.app/
# https://github.com/VirenPS/virenps.github.io
