import streamlit as st

def footer_home():
    logo_url = "https://imgs.search.brave.com/cGlC_Kg4r8_YKflxnrNdPJZEejlLGHqYAIQmFqpgskg/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9sb2dv/cy5mbGFtaW5ndGV4/dC5jb20vTmFtZS1M/b2dvcy9LaXJhbi1k/ZXNpZ24tY2hpbmEt/bmFtZS5wbmc"
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:white;"> Created with ❤️ by </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)






def footer_dashboard():
    logo_url = "https://imgs.search.brave.com/cGlC_Kg4r8_YKflxnrNdPJZEejlLGHqYAIQmFqpgskg/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9sb2dv/cy5mbGFtaW5ndGV4/dC5jb20vTmFtZS1M/b2dvcy9LaXJhbi1k/ZXNpZ24tY2hpbmEt/bmFtZS5wbmc"
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:black;"> Created with ❤️ by </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)
