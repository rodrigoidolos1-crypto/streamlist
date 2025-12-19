# ======================================================
# STREAMLIT APP - RECEBIMENTOS E ESTOQUE COM SHAREPOINT
# ======================================================

# ====================== IMPORTS ======================
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import base64
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# ======================================================
# CONFIGURAÇÃO DE ACESSO AO SHAREPOINT
# ======================================================
# OBS: Configure os secrets no GitHub Codespaces ou no Streamlit Cloud
# Nomeie as chaves exatamente como abaixo:
# SHAREPOINT_SITE, SHAREPOINT_USER, SHAREPOINT_PASSWORD

SHAREPOINT_SITE = st.secrets["SHAREPOINT_SITE"]  # Ex.: "https://armarmazens.sharepoint.com/sites/OperaoSBM"
SHAREPOINT_USER = st.secrets["SHAREPOINT_USER"]  # Ex.: "rodrigo.silva@armlogistica.com"
SHAREPOINT_PASSWORD = st.secrets["SHAREPOINT_PASSWORD"]  # Ex.: "ARM@fg2025!@"

# Arquivos no SharePoint
RECEBIMENTOS_FILE = "recebimentos.xlsx"
ESTOQUE_FILE = "estoque.xlsx"
ABA_RECEBIMENTO = "Recebimento"

# ======================================================
# LOGO
# ======================================================
LOGO_PATH = "logo.png"  # O logo deve estar no mesmo diretório do projeto

def get_logo_base64(path):
    """Lê o arquivo de logo e retorna base64 para exibir no Streamlit"""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_base64 = get_logo_base64(LOGO_PATH)

def show_logo_centralizada():
    if logo_base64:
        st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{logo_base64}' width='300'></div>", unsafe_allow_html=True)

def show_logo_sidebar():
    if logo_base64:
        st.image(LOGO_PATH, width=150)

# ======================================================
# FUNÇÕES SHAREPOINT
# ======================================================
@st.cache_resource
def get_sharepoint_ctx():
    """Retorna contexto autenticado para acessar SharePoint"""
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(UserCredential(SHAREPOINT_USER, SHAREPOINT_PASSWORD))
    return ctx

def download_excel(file_name):
    """Faz download de um arquivo Excel do SharePoint e retorna BytesIO"""
    ctx = get_sharepoint_ctx()
    # Separar folder do site
    folder_url = "/sites/OperaoSBM/Documentos Compartilhados/Recebimento/Arquivo Morto/Arquivo - Morto/Backup - Rodrigo-recebimento"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    file = folder.files.get_by_name(file_name)
    ctx.load(file)
    ctx.execute_query()
    response = file.read()
    return BytesIO(response.content)

def upload_excel(file_name, df, aba):
    """Faz upload de um DataFrame como Excel para o SharePoint"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=aba, index=False)
    output.seek(0)
    ctx = get_sharepoint_ctx()
    folder_url = "/sites/OperaoSBM/Documentos Compartilhados/Recebimento/Arquivo Morto/Arquivo - Morto/Backup - Rodrigo-recebimento"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    folder.upload_file(file_name, output.read()).execute_query()

# ======================================================
# CHAT GLOBAL
# ======================================================
@st.cache_resource
def chat_global():
    """Mantém mensagens de chat durante a sessão"""
    return {"mensagens": [], "digitando": {}}

CHAT_GLOBAL = chat_global()

# ======================================================
# SESSION STATE
# ======================================================
for key in ["log_acessos", "logado", "usuario", "perfil", "nova_msg"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key=="log_acessos" else False if key=="logado" else ""

# ======================================================
# USUÁRIOS
# ======================================================
USUARIOS = {
    "admin": {"senha": "admin123", "perfil": "ADM"},
    "consulta": {"senha": "consulta123", "perfil": "Consulta"},
    "colab": {"senha": "colab123", "perfil": "Colaborador"},
}

# ======================================================
# LOGIN
# ======================================================
if not st.session_state.logado:
    show_logo_centralizada()
    st.subheader("🔐 Login")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["senha"] == s:
            st.session_state.logado = True
            st.session_state.usuario = u
            st.session_state.perfil = USUARIOS[u]["perfil"]
            st.session_state.log_acessos.append({
                "Usuário": u,
                "Perfil": USUARIOS[u]["perfil"],
                "Evento": "LOGIN",
                "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
            st.success("✅ Login realizado!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")
    st.stop()

show_logo_sidebar()
st.success(f"🟢 Logado: **{st.session_state.usuario}** | Perfil: **{st.session_state.perfil}**")

# ======================================================
# CARREGAR RECEBIMENTOS
# ======================================================
try:
    df_base = pd.read_excel(download_excel(RECEBIMENTOS_FILE), sheet_name=ABA_RECEBIMENTO)
except:
    df_base = pd.DataFrame()
    st.warning("Planilha de recebimentos não encontrada. Será criada ao salvar o primeiro registro.")

df_base.columns = df_base.columns.str.strip()
if "ID" not in df_base.columns:
    df_base["ID"] = pd.Series(dtype=int)

novo_id = int(df_base["ID"].max()) + 1 if not df_base.empty else 1

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.subheader("📂 Menu")
pagina = st.sidebar.radio("Escolha a página", ["Formulário", "Consulta", "Dashboard", "Estoque", "Histórico de Acessos", "Chat"])
if st.sidebar.button("🚪 Sair"):
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.perfil = ""
    st.rerun()
# ======================================================
# FORMULÁRIO DE RECEBIMENTO
# ======================================================
if pagina == "Formulário" and st.session_state.perfil in ["ADM", "Colaborador"]:
    st.subheader("🗓️ Formulário de Recebimento Completo")
    
    # Criação do formulário usando st.form
    with st.form("form_recebimento"):
        data = st.date_input("DATA", value=datetime.now())
        hora = st.time_input("HORA", value=datetime.now().time())
        placa = st.text_input("PLACA VEÍCULO")
        transportadora = st.text_input("TRANSPORTADORA")
        po = st.text_input("PO")
        projeto = st.text_input("PROJETO")
        repetro = st.text_input("REPETRO")
        qtd_sku = st.number_input("Qtd. SKU", min_value=0)
        responsavel = st.text_input("RESPONSÁVEL")
        obs = st.text_area("OBSERVAÇÕES")
        salvar = st.form_submit_button("💾 Salvar Recebimento")
    
    # Ao salvar o formulário
    if salvar:
        nova_linha = {
            "ID": novo_id,
            "DATA": data,
            "HORA": hora.strftime("%H:%M:%S"),
            "PLACA VEÍCULO": placa,
            "TRANSPORTADORA": transportadora,
            "PO": po,
            "PROJETO": projeto,
            "REPETRO": repetro,
            "Qtd. SKU": qtd_sku,
            "RESPONSÁVEL": responsavel,
            "OBSERVAÇÕES": obs
        }
        # Adiciona a nova linha no DataFrame
        df_base = pd.concat([df_base, pd.DataFrame([nova_linha])], ignore_index=True)
        # Faz upload para o SharePoint
        upload_excel(RECEBIMENTOS_FILE, df_base, ABA_RECEBIMENTO)
        st.success(f"✅ Registro salvo! ID {novo_id}")
        st.rerun()

# ======================================================
# CONSULTA AVANÇADA
# ======================================================
if pagina == "Consulta":
    st.subheader("🔎 Consulta Avançada")
    
    # Filtros
    filtro_po = st.text_input("Filtrar por PO").upper()
    filtro_placa = st.text_input("Filtrar por Placa").upper()
    
    df_filtro = df_base.copy()
    
    if filtro_po:
        df_filtro = df_filtro[df_filtro["PO"].astype(str).str.contains(filtro_po)]
    if filtro_placa:
        df_filtro = df_filtro[df_filtro["PLACA VEÍCULO"].astype(str).str.contains(filtro_placa)]
    
    st.dataframe(df_filtro)

# ======================================================
# DASHBOARD
# ======================================================
if pagina == "Dashboard":
    st.subheader("📊 Dashboard")
    st.metric("Total de Recebimentos", len(df_base))
    
    if not df_base.empty:
        # Gráfico de histogramas de recebimentos por data
        fig = px.histogram(df_base, x="DATA", title="Recebimentos por Data")
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ESTOQUE
# ======================================================
if pagina == "Estoque":
    st.subheader("📦 Estoque Atual")
    try:
        df_estoque = pd.read_excel(download_excel(ESTOQUE_FILE))
        st.dataframe(df_estoque)
    except:
        st.warning("Planilha de estoque não encontrada.")

# ======================================================
# HISTÓRICO DE ACESSOS
# ======================================================
if pagina == "Histórico de Acessos" and st.session_state.perfil == "ADM":
    st.subheader("📜 Histórico de Acessos")
    df_log = pd.DataFrame(st.session_state.log_acessos)
    st.dataframe(df_log)

# ======================================================
# CHAT GLOBAL
# ======================================================
if pagina == "Chat":
    st.subheader("💬 Chat Global")
    
    usuario = st.session_state.usuario
    st.session_state["nova_msg"] = st.text_input("Digite sua mensagem", value=st.session_state["nova_msg"])
    
    if st.button("Enviar"):
        if st.session_state["nova_msg"].strip():
            CHAT_GLOBAL["mensagens"].append({
                "usuario": usuario,
                "hora": datetime.now().strftime("%H:%M:%S"),
                "texto": st.session_state["nova_msg"].strip()
            })
            st.session_state["nova_msg"] = ""
            st.rerun()
    
    # Exibe as mensagens
    for msg in CHAT_GLOBAL["mensagens"]:
        st.markdown(f"**{msg['usuario']}** ({msg['hora']}): {msg['texto']}")
