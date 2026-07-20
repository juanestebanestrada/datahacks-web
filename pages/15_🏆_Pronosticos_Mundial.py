"""pages/15_🏆_Pronosticos_Mundial.py — Redirige al nuevo Bracket de 32 Equipos"""
import streamlit as st
from utils.style_loader import load_css

st.set_page_config(page_title="Bracket Mundial 2026", page_icon="🏆", layout="wide")
load_css()

st.markdown("""
<div style="text-align:center; padding:60px 20px;
            background: radial-gradient(ellipse at center, #6B0D20, #1A0207);
            border-radius:16px; border: 2px solid rgba(255,215,0,0.3);
            box-shadow: 0 0 40px rgba(255,215,0,0.15);">
    <div style="font-size:4rem;">🏆</div>
    <h2 style="color:#FFD700; font-size:1.8rem; font-weight:900;
               text-transform:uppercase; letter-spacing:3px; margin:12px 0 6px;">
        Bracket del Mundial 2026
    </h2>
    <p style="color:rgba(255,255,255,0.6); font-size:1rem; margin-bottom:20px;">
        Esta sección fue reemplazada por el nuevo <strong style="color:#FFD700;">Bracket Completo de 32 Equipos</strong>.
    </p>
    <p style="color:rgba(255,255,255,0.4); font-size:0.9rem;">
        👈 Navega a <strong>🏆 Visual Bracket</strong> en el menú lateral para acceder al bracket completo con<br>
        dieciseisavos → octavos → cuartos → semis → final → campeón.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:30px;"></div>', unsafe_allow_html=True)
st.info("💡 El nuevo bracket soporta los **32 clasificados** del Mundial 2026: "
        "2 por grupo × 12 grupos + 8 mejores terceros. "
        "Puedes llenarlo con los resultados de tu **Simulador WhatIf**.")
