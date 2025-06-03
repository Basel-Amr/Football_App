import streamlit as st
from streamlit_lottie import st_lottie
from utils.lottie_loader import load_lottie_url

def cup_view_player():
    st.markdown("## 🏆 The Cup")
    st.markdown("A future exciting tournament is coming soon... Stay tuned!")

    animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_puciaact.json")
    if animation:
        st_lottie(animation, height=250)
    else:
        st.info("🎮 Future Cup Matches Will Appear Here!")
