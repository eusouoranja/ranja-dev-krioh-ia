import firebase_admin
from firebase_admin import credentials, firestore

# Carrega o arquivo de credenciais
cred = credentials.Certificate("firebase_credentials.json")

# Inicializa o Firebase, se ainda não estiver inicializado
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Acesso ao Firestore
db = firestore.client()
import streamlit as st
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

st.set_page_config(page_title="Assistente IA Krioh", page_icon="🤖")

cred_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🤖 Assistente IA da sua Marca")

prompt = st.text_area("Digite seu pedido:", placeholder="Ex: Crie uma legenda sobre o prato do dia")

if st.button("Gerar Conteúdo"):
    if prompt:
        with st.spinner("Gerando..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente de marketing que escreve com o tom da marca."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.success("Resultado:")
            st.markdown(response.choices[0].message.content)
    else:
        st.warning("Digite algo no campo acima para gerar o conteúdo.")
