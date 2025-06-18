import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import openai
import streamlit_authenticator as stauth
import json

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar Firebase usando secret
cred_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Autenticação de usuário
users = db.collection("usuarios").stream()
usernames = []
names = []
passwords = []

for user in users:
    data = user.to_dict()
    usernames.append(data["email"])
    names.append(data["nome"])
    passwords.append(data["senha"])

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "krioh_dashboard",
    "abcdef",
    cookie_expiry_days=30
)

nome, autenticado, nome_usuario = authenticator.login("Login", "main")

if autenticado:
    st.sidebar.success(f"Bem-vindo, {nome}!")

    st.title("Assistente IA da sua Marca")
    st.write("Digite abaixo o que deseja gerar:")

    prompt = st.text_area("Prompt", placeholder="Ex: Crie uma legenda para a parmegiana de mignon")

    if st.button("Gerar Conteúdo"):
        with st.spinner("Gerando..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente de marketing que escreve com o tom da marca."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.markdown("### Resultado:")
            st.success(response.choices[0].message.content)

    st.markdown("---")
    st.subheader("Ações rápidas")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Criar Post"):
            st.session_state["prompt"] = "Crie um post sobre os diferenciais da empresa"
    with col2:
        if st.button("Roteiro de Reels"):
            st.session_state["prompt"] = "Crie um roteiro de vídeo de 30s para o Instagram Reels sobre nosso produto destaque"

    if "prompt" in st.session_state:
        st.text_area("Prompt rápido", st.session_state["prompt"], key="rapido")

elif nome_usuario == "admin@krioh.com":
    st.title("Painel Administrativo - Krioh IA")
    st.subheader("Usuários Ativos")

    usuarios = db.collection("usuarios").stream()
    for u in usuarios:
        dados = u.to_dict()
        creditos = dados.get('creditos', 0)
        st.markdown(f"**{dados['nome']}** ({dados['email']}) — Créditos: {creditos}")
        doc_ref = db.collection("usuarios").document(u.id)
        if st.sidebar.button("Adicionar Créditos", key=f"add_creditos_{u.id}"):
            novo_credito = st.sidebar.number_input("Quantos créditos adicionar?", min_value=1, step=1, key=f"num_creditos_{u.id}")
            if st.sidebar.button("Confirmar Adição", key=f"confirm_add_{u.id}"):
                doc_ref.update({"creditos": creditos + int(novo_credito)})
                st.sidebar.success(f"{novo_credito} créditos adicionados!")

    st.markdown("---")
    st.subheader("Histórico de Ações")

    usuarios_email = [u.to_dict().get("email") for u in db.collection("usuarios").stream()]
    usuario_selecionado = st.selectbox("Filtrar por usuário", options=["Todos"] + usuarios_email)

    query = db.collection("logs_admin")
    if usuario_selecionado != "Todos":
        query = query.where("usuario", "==", usuario_selecionado)
    logs = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()

    for log in logs:
        l = log.to_dict()
        ts = l.get("timestamp")
        data_hora = ts.strftime("%d/%m/%Y %H:%M") if ts else "(sem data)"
        st.markdown(f"🕒 {data_hora} — **{l['admin']}** {l['acao']} {l['quantidade']} crédito(s) de **{l['usuario']}**")
else:
    st.warning("Faça login para acessar a plataforma.")
