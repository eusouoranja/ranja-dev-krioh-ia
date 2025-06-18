import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import openai
import streamlit_authenticator as stauth

load_dotenv()

if not firebase_admin._apps:
    import json
cred_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

openai.api_key = os.getenv("OPENAI_API_KEY")

users = db.collection("usuarios").stream()
usernames, names, passwords = [], [], []

for user in users:
    data = user.to_dict()
    usernames.append(data["email"])
    names.append(data["nome"])
    passwords.append(data["senha"])

hashed_passwords = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "krioh_dashboard", "abcdef", 30)
nome, autenticado, nome_usuario = authenticator.login("Login", "main")

if autenticado:
    st.sidebar.success(f"Bem-vindo, {nome}!")
    doc_ref = db.collection("usuarios").document(nome_usuario)
    doc = doc_ref.get()
    creditos = doc.to_dict().get("creditos", 10)
    st.sidebar.info(f"Créditos disponíveis: {creditos}")

    st.title("Assistente IA da sua Marca")
    prompt = st.text_area("Prompt", placeholder="Ex: Crie uma legenda para a parmegiana")

    if st.button("Gerar Conteúdo"):
        if creditos <= 0:
            st.error("Você não tem créditos disponíveis.")
        else:
            with st.spinner("Gerando..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é um assistente de marketing que escreve com o tom da marca."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.success(response.choices[0].message.content)
                doc_ref.update({"creditos": creditos - 1})
else:
    st.warning("Faça login para acessar a plataforma.")
