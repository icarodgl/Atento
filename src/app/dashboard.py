import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Analytics do Jogo", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None


# ---------- Login ----------
if not st.session_state.token:
    st.title("Login")
    with st.form("login"):
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            r = requests.post(
                f"{API_URL}/auth/token",
                data={"username": user, "password": pwd},
                timeout=10,
            )
            if r.ok:
                st.session_state.token = r.json()["access_token"]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
    st.stop()


# ---------- Dados ----------
@st.cache_data(ttl=30)
def load_events(token: str) -> pd.DataFrame:
    r = requests.get(
        f"{API_URL}/events",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    if not df.empty:
        df["occurred_at"] = pd.to_datetime(df["occurred_at"], utc=True).dt.tz_convert(
            "America/Sao_Paulo"
        )
    return df


try:
    df = load_events(st.session_state.token)
except requests.HTTPError as e:
    if e.response.status_code in (401, 403):
        st.session_state.token = None
        st.rerun()
    st.error(f"Erro ao buscar dados: {e}")
    st.stop()

st.title("Analytics do Jogo")

with st.sidebar:
    if st.button("Sair"):
        st.session_state.token = None
        st.rerun()
    if st.button("Atualizar dados"):
        load_events.clear()
        st.rerun()

if df.empty:
    st.info("Ainda não há eventos registrados.")
    st.stop()

# ---------- Filtros ----------
with st.sidebar:
    categories = st.multiselect(
        "Categoria", sorted(df["category"].unique()), default=list(df["category"].unique())
    )
    sessions = st.multiselect("Sessão (partida)", sorted(df["session_id"].unique()))

view = df[df["category"].isin(categories)]
if sessions:
    view = view[view["session_id"].isin(sessions)]

# ---------- Métricas ----------
c1, c2, c3 = st.columns(3)
c1.metric("Eventos", len(view))
c2.metric("Partidas", view["session_id"].nunique())
c3.metric("Pulos duplos", int((view["event_type"] == "double_jump").sum()))

# ---------- Gráficos ----------
left, right = st.columns(2)

by_type = view["event_type"].value_counts().reset_index()
by_type.columns = ["event_type", "quantidade"]
left.plotly_chart(
    px.bar(by_type, x="event_type", y="quantidade", title="Eventos por tipo")
)

objs = view[view["object_name"].notna()]["object_name"].value_counts().head(15).reset_index()
objs.columns = ["object_name", "quantidade"]
right.plotly_chart(
    px.bar(objs, x="quantidade", y="object_name", orientation="h",
           title="Objetos mais interagidos")
)

st.plotly_chart(
    px.scatter(
        view, x="game_time_seconds", y="event_type", color="category",
        hover_data=["object_name", "session_id"],
        title="Linha do tempo das ações (segundos desde o início do jogo)",
    )
)

st.subheader("Dados brutos")
st.dataframe(view)