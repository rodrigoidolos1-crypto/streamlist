import streamlit as st
import pandas as pd
from datetime import time, datetime
import base64
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ================= CHAT GLOBAL =================
@st.cache_resource
def chat_global():
    return {
        "mensagens": [],
        "digitando": {}
    }

CHAT_GLOBAL = chat_global()



# ================= CHAT =================
#if "chat_mensagens" not in st.session_state: ****** Chat somente local ******
#    CHAT_GLOBAL["mensagens"]
 



# ================= SESSION STATE =================
for key in ["log_acessos", "logado", "usuario", "perfil"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "log_acessos" else False if key == "logado" else ""

# ================= CONFIGURAÇÕES =================
CAMINHO_EXCEL = r"C:\Users\rodrigo.silva\OneDrive - ARM ARMAZENS GERAIS & LOGISTICA LTDA\Recebimento\Recebimento_base_python.xlsx"
ABA = "Recebimento"

LOGO_PATH = r"C:\Users\rodrigo.silva\OneDrive - ARM ARMAZENS GERAIS & LOGISTICA LTDA\Área de Trabalho\Pessoal\Python\logo png.png"

st.set_page_config(page_title="Recebimento SBM", layout="wide")
st.markdown(
    """
    <h1 style='text-align: center;'>📦 Sistema de Recebimento – SBM</h1>
    """,
    unsafe_allow_html=True
)

# ================= FUNÇÃO PARA CARREGAR LOGO =================
def get_logo_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        st.warning(f"⚠️ Logo não encontrada: {e}")
        return None

logo_base64 = get_logo_base64(LOGO_PATH)

def show_logo_centralizada():
    if logo_base64:
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src="data:image/png;base64,{logo_base64}" width="300">
            </div>
            """,
            unsafe_allow_html=True
        )

def show_logo_sidebar():
    if logo_base64:
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src="data:image/png;base64,{logo_base64}" width="150">
            </div>
            """,
            unsafe_allow_html=True
        )

# ================= ESTRUTURAS GLOBAIS =================
@st.cache_resource
def usuarios_online():
    return {}

@st.cache_resource
def log_acessos():
    return []

USUARIOS_ONLINE = usuarios_online()
LOG_ACESSOS = log_acessos()

# ================= USUÁRIOS =================
USUARIOS = {
    "admin": {"senha": "admin123", "perfil": "ADM"},
    "consulta": {"senha": "consulta123", "perfil": "Consulta"},
    "colab": {"senha": "colab123", "perfil": "Colaborador"},
}

# ================= LOGIN =================
if not st.session_state.logado:
    show_logo_centralizada()  # Logo centralizada no login
    st.subheader("🔐 Login")

    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["senha"] == s:
            st.session_state.logado = True
            st.session_state.usuario = u
            st.session_state.perfil = USUARIOS[u]["perfil"]

            USUARIOS_ONLINE[u] = {
                "perfil": USUARIOS[u]["perfil"],
                "login": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            LOG_ACESSOS.append({
                "Usuário": u,
                "Perfil": USUARIOS[u]["perfil"],
                "Evento": "LOGIN",
                "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })

            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")
    st.stop()

# ================= STATUS LOGIN =================
st.success(f"🟢 Usuário logado: **{st.session_state.usuario}** | Perfil: **{st.session_state.perfil}**")

# ================= SIDEBAR =================
with st.sidebar:
    show_logo_sidebar()  # Logo centralizada no sidebar
    
    st.subheader("👥 Usuários Online")
    if USUARIOS_ONLINE:
        for u, info in USUARIOS_ONLINE.items():
            st.markdown(
                f"🟢 **{u}**  \n"
                f"<small>Perfil: {info['perfil']} | Login: {info['login']}</small>",
                unsafe_allow_html=True
            )
    else:
        st.caption("Nenhum usuário online")
    
    st.divider()
    
    # Menu de navegação
    pagina = st.radio("📂 Menu", ["Formulário", "Consulta", "Dashboard", "Estoque", "Histórico de Acessos", "Chat"])
    
    st.divider()
    
    if st.button("🚪 Sair"):
        LOG_ACESSOS.append({
            "Usuário": st.session_state.usuario,
            "Perfil": st.session_state.perfil,
            "Evento": "LOGOUT",
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        USUARIOS_ONLINE.pop(st.session_state.usuario, None)
        st.session_state.clear()
        st.rerun()

#======= APARÊNCIA WHATSAPP =======
st.markdown("""
<style>
.chat-container {
    max-height: 420px;
    overflow-y: auto;
    padding: 10px;
    background-color: #ece5dd;
    border-radius: 10px;
}

.msg {
    max-width: 65%;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.4;
    word-wrap: break-word;
}

.msg-user {
    background-color: #dcf8c6;
    margin-left: auto;
    text-align: left;
}

.msg-other {
    background-color: #ffffff;
    margin-right: auto;
    text-align: left;
}

.msg-header {
    font-size: 11px;
    color: #555;
    margin-bottom: 2px;
}

.msg-time {
    font-size: 10px;
    color: #999;
    text-align: right;
}
.digitando {
    font-size: 11px;
    color: #555;
    margin: 4px;
}
</style>
""", unsafe_allow_html=True)

# ================= CHAT =================
if pagina == "Chat":
    st.subheader("💬 Chat entre usuários")
    usuario = st.session_state.usuario
    perfil = st.session_state.get("perfil", "Usuário")

    # Inicializa variáveis de sessão
    if "nova_msg" not in st.session_state:
        st.session_state["nova_msg"] = ""
    if "novas_mensagens" not in st.session_state:
        st.session_state["novas_mensagens"] = 0
    if "ultima_msg_vista" not in st.session_state:
        st.session_state["ultima_msg_vista"] = len(CHAT_GLOBAL["mensagens"])

    # Zera contador ao entrar no chat
    st.session_state["novas_mensagens"] = 0
    st.session_state["ultima_msg_vista"] = len(CHAT_GLOBAL["mensagens"])

    # ----- CHAT -----
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

    if CHAT_GLOBAL["mensagens"]:
        for msg in CHAT_GLOBAL["mensagens"][-50:]:
            classe = "msg-user" if msg["usuario"] == usuario else "msg-other"
            st.markdown(
                f"""
                <div class="msg {classe}">
                    <div class="msg-header">{msg['usuario']} ({msg['perfil']})</div>
                    <div>{msg['texto']}</div>
                    <div class="msg-time">{msg['hora']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.caption("Nenhuma mensagem ainda")

    st.markdown('</div>', unsafe_allow_html=True)

    # ----- DIGITANDO -----
    for u, p in CHAT_GLOBAL["digitando"].items():
        if u != usuario:
            st.markdown(
                f"<div class='digitando'>✍️ {u} ({p}) está digitando...</div>",
                unsafe_allow_html=True
            )

    st.markdown('<div class="chat-input-bar">', unsafe_allow_html=True)

    # ----- FORMULÁRIO -----
    with st.form(key=f"chat_form_{usuario}_principal", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state["nova_msg"] = st.text_input(
                "Digite sua mensagem",
                value=st.session_state["nova_msg"],
                label_visibility="collapsed"
            )
            # Atualiza digitando
            if st.session_state["nova_msg"]:
                CHAT_GLOBAL["digitando"][usuario] = perfil
            else:
                CHAT_GLOBAL["digitando"].pop(usuario, None)

        with col2:
            enviar = st.form_submit_button("📨")

        # ----- ENVIO DE MENSAGEM -----
        if enviar and st.session_state["nova_msg"].strip():
            CHAT_GLOBAL["mensagens"].append({
                "usuario": usuario,
                "perfil": perfil,
                "hora": datetime.now().strftime("%H:%M:%S"),
                "texto": st.session_state["nova_msg"].strip()
            }) 
            st.session_state["nova_msg"] = ""  # limpa input após enviar
            CHAT_GLOBAL["digitando"].pop(usuario, None)
            # Reseta contador ao enviar
            st.session_state["novas_mensagens"] = 0
            st.session_state["ultima_msg_vista"] = len(CHAT_GLOBAL["mensagens"])
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== CSS =====
    st.markdown("""
  <style>
.chat-wrapper {
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
}
.chat-messages {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.msg {
    padding: 8px 12px;
    border-radius: 12px;
    max-width: 70%;
    word-wrap: break-word;
    color: #000080; /* Azul marinho */
}
.msg-user {
    align-self: flex-end;
    background-color: #dcf8c6;
}
.msg-other {
    align-self: flex-start;
    background-color: #ffffff;
    border: 1px solid #ddd;
}
.msg-header {
    font-size: 0.75rem;
    font-weight: bold;
    margin-bottom: 4px;
}
.msg-time {
    font-size: 0.65rem;
    color: #888;
    text-align: right;
    margin-top: 4px;
}
.digitando {
    font-style: italic;
    color: #555;
    margin-bottom: 4px;
}
.chat-input-bar {
    margin-top: 10px;
    display: flex;
    gap: 8px;
}
</style>
    """, unsafe_allow_html=True)

   
    # ----- DIGITANDO -----
    if CHAT_GLOBAL["digitando"]:
        for u, p in CHAT_GLOBAL["digitando"].items():
            if u != usuario:
                st.markdown(
                    f"<div class='digitando'>✍️ {u} ({p}) está digitando...</div>",
                    unsafe_allow_html=True
                )

   
try:
    df_base = pd.read_excel(CAMINHO_EXCEL, sheet_name=ABA)
except Exception as e:
    st.error(f"❌ Erro ao ler base: {e}")
    st.stop()

df_base.columns = df_base.columns.str.strip()

COLUNAS_HORA = [
    "HOR. DE CHEGADA NA PORTARIA",
    "HOR. DE CHEGADA NO IFS",
    "HOR. DE SAÍDA DO IFS/WMS",
    "HOR. LIBERAÇÃO PARA OPERAÇÃO",
    "HOR. DE CHEGADA NA OPERAÇÃO",
    "HOR. DE SAÍDA DA OPERAÇÃO",
]

for col in COLUNAS_HORA:
    if col in df_base.columns:
        df_base[col] = df_base[col].astype(str)

if "ID" not in df_base.columns:
    st.error("❌ A planilha não possui a coluna ID.")
    st.stop()

# Garantir que ID seja numérico
df_base["ID"] = pd.to_numeric(df_base["ID"], errors="coerce")

# Calcular próximo ID corretamente
if df_base.empty or df_base["ID"].dropna().empty:
    novo_id = 1
else:
    novo_id = int(df_base["ID"].max()) + 1

st.info(f"🆔 Próximo ID automático: **{novo_id}**")

# ================= FUNÇÕES =================
def hora_padrao():
    return time(0, 0)

def campo_sugestao(label, df, coluna):
    if coluna not in df.columns:
        return st.text_input(label)
    opcoes = sorted(df[coluna].dropna().astype(str).str.strip().unique().tolist())
    opcoes.insert(0, "")
    opcoes.append("✏️ Digitar novo")
    escolha = st.selectbox(label, opcoes)
    if escolha == "✏️ Digitar novo":
        return st.text_input(f"Novo {label}")
    return escolha

# ================= FORMULÁRIO =================
if pagina == "Formulário" and st.session_state.perfil in ["ADM", "Colaborador"]:
    with st.form("form_recebimento"):
        st.subheader("🗓️ Datas e Horários")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            data = st.date_input("DATA", format="DD/MM/YYYY")
            data_emissao = st.date_input("DATA DE EMISSÃO", format="DD/MM/YYYY")
        with c2:
            h_portaria = st.time_input("HOR. CHEGADA PORTARIA", value=hora_padrao())
            h_ifs = st.time_input("HOR. CHEGADA IFS", value=hora_padrao())
        with c3:
            h_saida_ifs = st.time_input("HOR. SAÍDA IFS/WMS", value=hora_padrao())
            h_lib_oper = st.time_input("HOR. LIBERAÇÃO OPERAÇÃO", value=hora_padrao())
        with c4:
            h_chegada_oper = st.time_input("HOR. CHEGADA OPERAÇÃO", value=hora_padrao())
            h_saida_oper = st.time_input("HOR. SAÍDA OPERAÇÃO", value=hora_padrao())

        st.subheader("🚚 Documento e Transporte")
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            placa = campo_sugestao("PLACA VEÍCULO", df_base, "PLACA VEÍCULO")
            transportadora = campo_sugestao("TRANSPORTADORA", df_base, "TRANSPORTADORA")
        with c6:
            po = campo_sugestao("PO", df_base, "PO")
            incoterms = campo_sugestao("INCOTERMS", df_base, "INCOTERMS")
        with c7:
            nota_fiscal = campo_sugestao("NOTA FISCAL", df_base, "NOTA FISCAL")
            fornecedor = campo_sugestao("FORNECEDOR", df_base, "FORNECEDOR")
        with c8:
            qtd_sku = st.number_input("Qtd. SKU", min_value=0)
            natureza = campo_sugestao("NATUREZA DA OPERAÇÃO", df_base, "NATUREZA DA OPERAÇÃO")

        st.subheader("⚙️ Operação")
        c9, c10, c11, c12 = st.columns(4)
        with c9:
            tipo_operacao = campo_sugestao("TIPO DE OPERAÇÃO", df_base, "TIPO DE OPERAÇÃO")
            barco = campo_sugestao("BARCO", df_base, "BARCO")
        with c10:
            projeto = campo_sugestao("PROJETO", df_base, "PROJETO")
            repetro = st.selectbox("REPETRO", ["", "SIM", "NÃO"])
        with c11:
            quimicos = st.selectbox("QUIMICOS", ["", "SIM", "NÃO"])
            fds = st.selectbox("FDS", ["", "SIM", "NÃO"])
        with c12:
            agendamento = st.selectbox("AGENDAMENTO", ["", "SIM", "NÃO"])
            entrega = st.selectbox("ENTREGA", ["", "SIM", "NÃO"])

        observacao = st.text_input("OBSERVAÇÃO")
        responsavel = st.text_input("RESPONSÁVEL")
        salvar = st.form_submit_button("💾 Salvar Recebimento")

    if salvar:
        nova_linha = {
            "ID": novo_id,
            "DATA": data,
            "DATA DE EMISSÃO": data_emissao,
            "HOR. DE CHEGADA NA PORTARIA": str(h_portaria),
            "HOR. DE CHEGADA NO IFS": str(h_ifs),
            "HOR. DE SAÍDA DO IFS/WMS": str(h_saida_ifs),
            "HOR. LIBERAÇÃO PARA OPERAÇÃO": str(h_lib_oper),
            "HOR. DE CHEGADA NA OPERAÇÃO": str(h_chegada_oper),
            "HOR. DE SAÍDA DA OPERAÇÃO": str(h_saida_oper),
            "PLACA VEÍCULO": placa,
            "TRANSPORTADORA": transportadora,
            "PO": po,
            "INCOTERMS": incoterms,
            "Qtd. SKU": qtd_sku,
            "NOTA FISCAL": nota_fiscal,
            "FORNECEDOR": fornecedor,
            "QUIMICOS": quimicos,
            "FDS": fds,
            "NATUREZA DA OPERAÇÃO": natureza,
            "TIPO DE OPERAÇÃO": tipo_operacao,
            "BARCO": barco,
            "PROJETO": projeto,
            "REPETRO": repetro,
            "ENTREGA": entrega,
            "AGENDAMENTO": agendamento,
            "OBSERVAÇÃO": observacao,
            "RESPONSÁVEL": responsavel,
        }

        df_base = pd.concat([df_base, pd.DataFrame([nova_linha])], ignore_index=True)

        with pd.ExcelWriter(CAMINHO_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_base.to_excel(writer, sheet_name=ABA, index=False)

        st.success(f"✅ Registro salvo com sucesso! ID {novo_id}")
        st.rerun()

# ================= CONSULTA =================
if pagina == "Consulta":
    st.divider()
    st.subheader("🔎 Consulta de Recebimentos")

    f1, f2, f3 = st.columns(3)
    with f1:
        filtro_id = st.number_input("ID", min_value=0)
    with f2:
        filtro_po = st.text_input("PO").upper()
    with f3:
        filtro_nf = st.text_input("NOTA FISCAL").upper()

    df_filtro = df_base.copy()
    if filtro_id > 0:
        df_filtro = df_filtro[df_filtro["ID"] == filtro_id]
    if filtro_po:
        df_filtro = df_filtro[df_filtro["PO"].astype(str).str.contains(filtro_po)]
    if filtro_nf:
        df_filtro = df_filtro[df_filtro["NOTA FISCAL"].astype(str).str.contains(filtro_nf)]

    df_filtro_exibir = df_filtro.copy()
    if "DATA" in df_filtro_exibir.columns:
        df_filtro_exibir["DATA"] = pd.to_datetime(df_filtro_exibir["DATA"], errors="coerce").dt.strftime("%d/%m/%Y")

    st.markdown(f"📌 **{len(df_filtro_exibir)} registros encontrados**")
    st.dataframe(df_filtro_exibir.sort_values("ID", ascending=False), width="stretch", hide_index=True)

# ================= DASHBOARD =================
if pagina == "Dashboard":
    st.divider()
    st.subheader("📊 Dashboard de Recebimentos")

    df_dash = df_base.copy()
    df_dash["DATA"] = pd.to_datetime(df_dash["DATA"], errors="coerce")

    col_horarios = [
        "HOR. DE CHEGADA NA PORTARIA",
        "HOR. DE CHEGADA NO IFS",
        "HOR. DE SAÍDA DO IFS/WMS",
        "HOR. LIBERAÇÃO PARA OPERAÇÃO",
        "HOR. DE CHEGADA NA OPERAÇÃO",
        "HOR. DE SAÍDA DA OPERAÇÃO",
    ]

    for col in col_horarios:
        if col in df_dash.columns:
            df_dash[col] = pd.to_datetime(
                df_dash["DATA"].astype(str) + " " + df_dash[col].astype(str),
                errors="coerce",
                utc=True
            ).dt.tz_convert(None)

    if "HOR. DE CHEGADA NA PORTARIA" in df_dash.columns and "HOR. DE CHEGADA NA OPERAÇÃO" in df_dash.columns:
        df_dash["TEMPO_PORTARIA_OP"] = (
            df_dash["HOR. DE CHEGADA NA OPERAÇÃO"] - df_dash["HOR. DE CHEGADA NA PORTARIA"]
        ).dt.total_seconds() / 60
    else:
        df_dash["TEMPO_PORTARIA_OP"] = None

    if df_dash.empty:
        st.warning("⚠️ Não há dados suficientes para gerar o dashboard.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            data_ini = st.date_input("Data inicial (YYYY-MM-DD)", value=df_dash["DATA"].min().date())
        with f2:
            data_fim = st.date_input("Data final (YYYY-MM-DD)", value=df_dash["DATA"].max().date())
        with f3:
            filtro_transportadora = st.multiselect(
                "Transportadora",
                sorted(df_dash["TRANSPORTADORA"].dropna().astype(str).unique())
            )

        df_dash = df_dash[(df_dash["DATA"] >= pd.to_datetime(data_ini)) & (df_dash["DATA"] <= pd.to_datetime(data_fim))]
        if filtro_transportadora:
            df_dash = df_dash[df_dash["TRANSPORTADORA"].isin(filtro_transportadora)]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📦 Total de Recebimentos", len(df_dash))
        tempo_medio = df_dash["TEMPO_PORTARIA_OP"].mean()
        k2.metric("⏱️ Tempo médio Portaria → Operação (min)", round(tempo_medio, 1) if pd.notna(tempo_medio) else "—")
        k3.metric("🚚 Transportadoras", df_dash["TRANSPORTADORA"].nunique())
        k4.metric("🏷️ Tipos de Operação", df_dash["TIPO DE OPERAÇÃO"].nunique())

        st.subheader("📅 Recebimentos Detalhados")
        st.dataframe(df_dash.sort_values("DATA", ascending=False), width="stretch", hide_index=True)

# ================= ESTOQUE =================
if pagina == "Estoque":
    st.divider()
    st.subheader("📦 Estoque Atual")

    CAMINHO_ESTOQUE = r"C:\Users\rodrigo.silva\OneDrive - ARM ARMAZENS GERAIS & LOGISTICA LTDA\Área de Trabalho\Pessoal\Python\API Estoque Versão Customizada - SBM.xlsx"

    try:
        df_estoque = pd.read_excel(CAMINHO_ESTOQUE)

        if df_estoque.empty:
            st.warning("⚠️ Nenhum dado de estoque encontrado.")
            st.stop()

        # Padronizar colunas
        df_estoque.columns = df_estoque.columns.str.strip()

        # Garantir numéricos
        df_estoque["Qtde"] = pd.to_numeric(
            df_estoque["Qtde"], errors="coerce"
        ).fillna(0)

        df_estoque["Qtde Reservada"] = pd.to_numeric(
            df_estoque.get("Qtde Reservada", 0), errors="coerce"
        ).fillna(0)

        # Filtros
        f1, f2, f3 = st.columns(3)
        with f1:
            filtro_sku = st.text_input("SKU")
        with f2:
            filtro_categoria = st.text_input("Categoria")
        with f3:
            filtro_endereco = st.text_input("Endereço")

        df_filtrado = df_estoque.copy()

        if filtro_sku:
            df_filtrado = df_filtrado[
                df_filtrado["SKU"].astype(str).str.contains(filtro_sku, case=False)
            ]

        if filtro_categoria:
            df_filtrado = df_filtrado[
                df_filtrado["Categoria"].astype(str).str.contains(filtro_categoria, case=False)
            ]

        if filtro_endereco:
            df_filtrado = df_filtrado[
                df_filtrado["Endereço"].astype(str).str.contains(filtro_endereco, case=False)
            ]

        # Resumo
        df_resumo = (
            df_filtrado
            .groupby(["SKU", "Descrição"], as_index=False)
            .agg({
                "Qtde": "sum",
                "Qtde Reservada": "sum"
            })
        )

        df_resumo["Estoque Disponível"] = (
            df_resumo["Qtde"] - df_resumo["Qtde Reservada"]
        )

        st.markdown(f"📌 **{len(df_resumo)} SKUs encontrados**")

        st.dataframe(
            df_resumo.sort_values("Estoque Disponível", ascending=False),
            hide_index=True,
            width="stretch"
        )

    except FileNotFoundError:
        st.error("❌ Arquivo Estoque.xlsx não encontrado.")
    except Exception as e:
        st.error(f"❌ Erro ao carregar estoque: {e}")



# ================= HISTÓRICO DE ACESSOS =================
if pagina == "Histórico de Acessos" and st.session_state.perfil == "ADM":
    st.subheader("📜 Histórico Completo de Acessos")
    if LOG_ACESSOS:
        df_log = pd.DataFrame(LOG_ACESSOS)
        st.dataframe(df_log.sort_values("Data/Hora", ascending=False), width="stretch", hide_index=True)
    else:
        st.caption("Sem registros de acessos")

        # ---------------- FILTROS ----------------
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            filtro_sku = st.text_input("SKU").upper()
        with c2:
            filtro_endereco = st.text_input("ENDEREÇO").upper()
        with c3:
            filtro_depositante = st.text_input("DEPOSITANTE").upper()
        with c4:
            filtro_destinatario = st.text_input("DESTINATÁRIO").upper()
        with c5:
            filtro_situacao = st.selectbox(
                "Situação Validade",
                options=["", "Validade", "Atenção", "A vencer", "Vencido"]
            )

        df_filtrado = df_base.copy()

        # Aplicar filtros
        if filtro_sku and "SKU" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["SKU"].astype(str).str.contains(filtro_sku)]
        if filtro_endereco and "ENDEREÇO" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["ENDEREÇO"].astype(str).str.contains(filtro_endereco)]
        if filtro_depositante and "DEPOSITANTE" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["DEPOSITANTE"].astype(str).str.contains(filtro_depositante)]
        if filtro_destinatario and "DESTINATÁRIO" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["DESTINATÁRIO"].astype(str).str.contains(filtro_destinatario)]

        # ---------------- CORES E SITUAÇÃO VALIDADE ----------------
        if "DATA DE VALIDADE" in df_filtrado.columns:
            df_filtrado["DATA DE VALIDADE"] = pd.to_datetime(
                df_filtrado["DATA DE VALIDADE"], errors="coerce"
            )

            def situacao_val(val):
                if pd.isna(val):
                    return ""
                dias = (val - pd.Timestamp.now()).days
                if dias < 0:
                    return "Vencido"
                elif dias <= 30:
                    return "A vencer"
                elif 31 <= dias <= 100:
                    return "Atenção"
                else:
                    return "Validade"

            df_filtrado["SITUAÇÃO VALIDADE"] = df_filtrado["DATA DE VALIDADE"].apply(situacao_val)

            # Aplicar filtro da coluna Situação Validade
            if filtro_situacao:
                df_filtrado = df_filtrado[df_filtrado["SITUAÇÃO VALIDADE"] == filtro_situacao]

        # ---------------- FORMATAR DATAS ----------------
        if "DATA OPERAÇÃO" in df_filtrado.columns:
            df_filtrado["DATA OPERAÇÃO"] = pd.to_datetime(
                df_filtrado["DATA OPERAÇÃO"], errors="coerce"
            ).dt.strftime("%d/%m/%Y")

        # ---------------- OCULTAR COLUNAS VAZIAS ----------------
        df_filtrado = df_filtrado.dropna(axis=1, how='all')

        # ---------------- EXIBIÇÃO ----------------
        st.markdown(f"📌 **{len(df_filtrado)} registros encontrados no estoque**")

        colunas_exibir = ["ID", "NOTA FISCAL", "SKU", "DESCRIÇÃO",
                          "ENDEREÇO", "DEPOSITANTE", "DESTINATÁRIO",
                          "LOTE", "DATA OPERAÇÃO", "VR. TOTAL",
                          "DATA DE VALIDADE", "SITUAÇÃO VALIDADE"]

        colunas_existentes = [c for c in colunas_exibir if c in df_filtrado.columns]

        # Colorir situação validade
        def color_situacao_html(val):
            cores = {
                "Validade": "green",
                "Atenção": "orange",
                "A vencer": "orange",
                "Vencido": "darkred",
                "": ""
            }
            if val in cores and cores[val]:
                return f'<span style="color:{cores[val]}; font-weight:bold;">{val}</span>'
            return val

        if "SITUAÇÃO VALIDADE" in colunas_existentes:
            df_filtrado["SITUAÇÃO VALIDADE"] = df_filtrado["SITUAÇÃO VALIDADE"].apply(color_situacao_html)

        # Centralizar texto via CSS
        st.markdown(
            """
            <style>
            .dataframe tbody td {
                text-align: center;
            }
            .dataframe thead th {
                text-align: center;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Exibir no Streamlit
        st.write(df_filtrado[colunas_existentes].to_html(escape=False, index=False), unsafe_allow_html=True)