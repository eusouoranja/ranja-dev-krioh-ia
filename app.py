import os
import json
import firebase_admin
from firebase_admin import credentials

firebase_cred_json = os.environ.get("FIREBASE_CREDENTIALS")

if not firebase_cred_json:
    raise ValueError("Variável de ambiente FIREBASE_CREDENTIALS está vazia ou não foi definida.")

cred_dict = json.loads(firebase_cred_json)  # <-- é aqui que está quebrando se for vazio
cred = credentials.Certificate(cred_dict)

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
