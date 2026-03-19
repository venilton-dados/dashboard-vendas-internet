import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Visão Geral de Vendas", layout="wide", page_icon="📡")

META_POR_VENDA = 120.0
ROXO_ESCURO    = "#0e0b1a"
ROXO_CARD      = "#1a1230"
ROXO_BORDA     = "#3d2b6b"
ROXO_TEXTO     = "#c9b8f0"
ROXO_DESTAQUE  = "#a855f7"

st.markdown(f"""
<style>
  .stApp {{ background-color: {ROXO_ESCURO}; }}

  [data-testid="stSidebar"] {{
    background-color: {ROXO_CARD} !important;
    border-right: 1px solid {ROXO_BORDA};
  }}
  [data-testid="stSidebar"] * {{ color: {ROXO_TEXTO} !important; }}

  [data-baseweb="popover"],
  [data-baseweb="menu"],
  [role="listbox"],
  [role="option"],
  ul[role="listbox"],
  li[role="option"] {{
    background-color: #1a1230 !important;
    color: #e8d5ff !important;
  }}
  [role="option"]:hover,
  li[role="option"]:hover {{
    background-color: #2d1b5e !important;
    color: #ffffff !important;
  }}

  [data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: #2d1b5e !important;
    border: 1px solid #5b2d9e !important;
    border-radius: 8px !important;
    color: #e8d5ff !important;
  }}

  [data-baseweb="tag"] {{
    background-color: #4c1d95 !important;
    color: #e8d5ff !important;
  }}
  [data-baseweb="tag"] span {{ color: #e8d5ff !important; }}

  [data-testid="stFileUploader"] {{
    background-color: #2d1b5e !important;
    border: 1px solid #5b2d9e !important;
    border-radius: 12px !important;
    padding: 8px !important;
  }}
  [data-testid="stFileUploader"] button {{
    background: linear-gradient(135deg, #7c3aed, #4c1d95) !important;
    color: #ffffff !important;
    border: 1px solid #a855f7 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 10px !important;
  }}
  [data-testid="stFileUploaderDropzone"] {{
    background-color: #2d1b5e !important;
    border: 1px dashed #5b2d9e !important;
    border-radius: 10px !important;
  }}
  [data-testid="stFileUploaderDropzoneInstructions"] {{
    display: none !important;
  }}

  h1,h2,h3,h4 {{ color: #e8d5ff !important; }}
  p, label, span {{ color: {ROXO_TEXTO}; }}
  hr {{ border-color: {ROXO_BORDA}; }}

  [data-testid="stMetricValue"] {{ color: #ffffff !important; font-size:1.9rem !important; font-weight:800 !important; }}
  [data-testid="stMetricLabel"] {{ color: #a78bd4 !important; font-size:0.8rem !important; text-transform:uppercase; letter-spacing:1px; }}

  .kpi-purple {{ background:linear-gradient(135deg,#4c1d95,#2d1b5e); border:1px solid #7c3aed; border-radius:14px; padding:20px; text-align:center; }}
  .kpi-pink   {{ background:linear-gradient(135deg,#831843,#4a0e2e); border:1px solid #db2777; border-radius:14px; padding:20px; text-align:center; }}
  .kpi-green  {{ background:linear-gradient(135deg,#064e3b,#022c22); border:1px solid #10b981; border-radius:14px; padding:20px; text-align:center; }}
  .kpi-val    {{ font-size:2rem; font-weight:900; color:#ffffff; margin:8px 0 4px; }}
  .kpi-label  {{ font-size:0.75rem; text-transform:uppercase; letter-spacing:2px; color:rgba(255,255,255,0.7); }}
  .kpi-delta  {{ font-size:0.85rem; margin-top:4px; }}
  .delta-up   {{ color:#4ade80; }}
  .delta-down {{ color:#f87171; }}

  .vendor-row {{ display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid {ROXO_BORDA}; }}
  .vendor-rank {{ font-size:1.2rem; width:28px; text-align:center; }}
  .vendor-name {{ color:#e8d5ff; font-weight:600; font-size:0.9rem; }}
  .vendor-val  {{ color:#a78bd4; font-size:0.8rem; }}
  .header-box {{ background:{ROXO_CARD}; border-bottom:1px solid {ROXO_BORDA}; padding:14px 20px; margin-bottom:16px; border-radius:14px; display:flex; align-items:center; gap:16px; }}
</style>
""", unsafe_allow_html=True)

def plot_cfg(fig, h=320):
    fig.update_layout(
        plot_bgcolor=ROXO_CARD, paper_bgcolor=ROXO_CARD,
        font_color=ROXO_TEXTO, height=h,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="#2d1b5e", showgrid=True, tickfont=dict(color=ROXO_TEXTO)),
        yaxis=dict(gridcolor="#2d1b5e", showgrid=True, tickfont=dict(color=ROXO_TEXTO)),
        legend=dict(font=dict(color=ROXO_TEXTO))
    )
    return fig

def avatar_url(nome):
    seed = nome.replace(" ", "+")
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}&backgroundColor=4c1d95&radius=50"

# ── SIDEBAR ────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Filtros")
st.sidebar.divider()

arquivo = st.sidebar.file_uploader("📂  Subir Arquivo", type=["xlsx","csv"])

if arquivo:
    df = pd.read_excel(arquivo) if arquivo.name.endswith(".xlsx") else pd.read_csv(arquivo)
    df["Data"]    = pd.to_datetime(df["Data"], dayfirst=True)
    df["Ano"]     = df["Data"].dt.year
    df["MesNum"]  = df["Data"].dt.month
    df["MesNome"] = df["Data"].dt.strftime("%B")
    df["Linha"]   = df["Plano"].apply(lambda x: "Fibra" if "Fibra" in x else "Internet")
    df["Meta"]    = META_POR_VENDA

    st.sidebar.markdown(f"<p style='font-size:12px; color:#a78bd4; text-align:center'>✅ {arquivo.name}</p>", unsafe_allow_html=True)
    st.sidebar.divider()

    anos_disp = sorted(df["Ano"].unique().tolist())
    ano_sel   = st.sidebar.multiselect("Ano", anos_disp, default=anos_disp)

    meses_disp = ["Todos"] + list(df["MesNome"].unique())
    mes_sel    = st.sidebar.selectbox("Mês", meses_disp)

    linhas_disp = ["Todos"] + sorted(df["Linha"].unique().tolist())
    linha_sel   = st.sidebar.selectbox("Linha de Produto", linhas_disp)

    planos_disp = ["Todos"] + sorted(df["Plano"].unique().tolist())
    plano_sel   = st.sidebar.selectbox("Grupo de Produto", planos_disp)

    # ── APLICA FILTROS ─────────────────────────────────────
    df_f = df[df["Ano"].isin(ano_sel)] if ano_sel else df.copy()
    if mes_sel   != "Todos": df_f = df_f[df_f["MesNome"] == mes_sel]
    if linha_sel != "Todos": df_f = df_f[df_f["Linha"]   == linha_sel]
    if plano_sel != "Todos": df_f = df_f[df_f["Plano"]   == plano_sel]

    # ── CABEÇALHO ──────────────────────────────────────────
    st.markdown(f"""
    <div class="header-box">
      <span style="font-size:2rem">📡</span>
      <span style="font-size:1.4rem; font-weight:900; color:#e8d5ff; letter-spacing:2px">
        VISÃO GERAL DE <b style="color:#a855f7">VENDAS</b>
      </span>
      <span style="margin-left:auto; color:#a78bd4; font-size:0.85rem">
        {", ".join(str(a) for a in ano_sel) if ano_sel else "—"} &nbsp;|&nbsp; {mes_sel} &nbsp;|&nbsp; {linha_sel}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ───────────────────────────────────────────────
    fat_total  = df_f["Valor (R$)"].sum()
    fat_meta   = df_f["Meta"].sum()
    ating_meta = (fat_total / fat_meta * 100) if fat_meta > 0 else 0
    ticket_med = df_f["Valor (R$)"].mean() if len(df_f) > 0 else 0
    fat_ref    = df["Valor (R$)"].mean() * 100
    delta_fat  = ((fat_total - fat_ref) / fat_ref * 100) if fat_ref > 0 else 0
    delta_tick = ((ticket_med - META_POR_VENDA) / META_POR_VENDA * 100)

    k1, k2, k3, _ = st.columns([1,1,1,1])

    with k1:
        st.markdown(f"""
        <div class="kpi-purple">
          <div class="kpi-label">💰 Faturamento</div>
          <div class="kpi-val">R$ {fat_total:,.0f}</div>
          <div class="kpi-delta {'delta-up' if delta_fat>=0 else 'delta-down'}">
            {'▲' if delta_fat>=0 else '▼'} {abs(delta_fat):.0f}% vs referência
          </div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-pink">
          <div class="kpi-label">🎯 Atingimento Meta</div>
          <div class="kpi-val">{ating_meta:.1f}%</div>
          <div class="kpi-delta {'delta-up' if ating_meta>=80 else 'delta-down'}">
            {'▲' if ating_meta>=80 else '▼'} meta: 80%
          </div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-green">
          <div class="kpi-label">📈 Ticket Médio</div>
          <div class="kpi-val">R$ {ticket_med:,.2f}</div>
          <div class="kpi-delta {'delta-up' if delta_tick>=0 else 'delta-down'}">
            {'▲' if delta_tick>=0 else '▼'} {abs(delta_tick):.0f}% vs meta
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── EVOLUÇÃO + DONUT + BARRAS POR GRUPO ───────────────
    col_ev, col_donut, col_grp = st.columns([2,1,1])

    with col_ev:
        st.markdown("#### 📊 Evolução de Vendas")
        evolucao = df_f.groupby(df_f["Data"].dt.to_period("M").astype(str)).agg(
            Faturamento=("Valor (R$)", "sum"),
            Meta=("Meta", "sum")
        ).reset_index().rename(columns={"Data":"Período"})
        fig_ev = go.Figure()
        fig_ev.add_trace(go.Bar(
            x=evolucao["Período"], y=evolucao["Faturamento"],
            name="Faturamento", marker_color="#7c3aed"))
        fig_ev.add_trace(go.Scatter(
            x=evolucao["Período"], y=evolucao["Meta"],
            name="Meta", line=dict(color="#f472b6", width=2, dash="dot"),
            mode="lines+markers", marker=dict(color="#f472b6", size=6)))
        fig_ev = plot_cfg(fig_ev, h=280)
        st.plotly_chart(fig_ev, use_container_width=True)

    with col_donut:
        st.markdown("#### Qtd por Linha")
        por_linha = df_f.groupby("Linha").size().reset_index(name="Qtd")
        fig_donut = px.pie(por_linha, names="Linha", values="Qtd",
                           hole=0.55, color_discrete_sequence=["#7c3aed","#06b6d4"])
        fig_donut.update_layout(
            plot_bgcolor=ROXO_CARD, paper_bgcolor=ROXO_CARD,
            font_color=ROXO_TEXTO, height=280,
            margin=dict(l=10,r=10,t=30,b=10),
            legend=dict(font=dict(color=ROXO_TEXTO), orientation="h", y=-0.15)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_grp:
        st.markdown("#### Qtd por Plano")
        por_plano = df_f.groupby("Plano").size().reset_index(name="Qtd").sort_values("Qtd", ascending=True)
        fig_grp = px.bar(por_plano, x="Qtd", y="Plano", orientation="h",
                         color="Qtd", color_continuous_scale="Purples")
        fig_grp.update_layout(
            plot_bgcolor=ROXO_CARD, paper_bgcolor=ROXO_CARD,
            font_color=ROXO_TEXTO, height=280,
            margin=dict(l=10,r=10,t=30,b=10),
            yaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO)),
            xaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO)),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_grp, use_container_width=True)

    st.divider()

    # ── RANKING + TICKET POR CANAL ─────────────────────────
    col_rank, col_canal = st.columns([1.4, 1])

    with col_rank:
        st.markdown("#### 🏆 Ranking de Vendedores")
        ranking = df_f.groupby("Vendedor").agg(
            Faturamento=("Valor (R$)", "sum"),
            Qtd=("Valor (R$)", "count"),
            Ticket=("Valor (R$)", "mean"),
            MetaTotal=("Meta", "sum")
        ).reset_index().sort_values("Faturamento", ascending=False).reset_index(drop=True)
        ranking["% Meta"] = (ranking["Faturamento"] / ranking["MetaTotal"] * 100).round(1)
        medalhas = ["🥇","🥈","🥉","4º","5º","6º","7º","8º"]

        for i, row in ranking.iterrows():
            av_url  = avatar_url(row["Vendedor"])
            atingiu = "✅" if row["% Meta"] >= 100 else "❌"
            st.markdown(f"""
            <div class="vendor-row">
              <span class="vendor-rank">{medalhas[i] if i < len(medalhas) else str(i+1)}</span>
              <img src="{av_url}" width="36" height="36"
                   style="border-radius:50%; border:2px solid #7c3aed"/>
              <div style="flex:1">
                <div class="vendor-name">{row["Vendedor"]}</div>
                <div class="vendor-val">R$ {row["Faturamento"]:,.2f} &nbsp;·&nbsp; {int(row["Qtd"])} vendas</div>
              </div>
              <div style="text-align:right">
                <div style="color:#e8d5ff; font-weight:700">R$ {row["Ticket"]:,.2f}</div>
                <div style="font-size:0.8rem; color:#a78bd4">{row['% Meta']}% {atingiu}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_canal:
        st.markdown("#### 📡 Ticket Médio por Canal")
        por_canal = df_f.groupby("Canal")["Valor (R$)"].mean().reset_index()
        por_canal.columns = ["Canal","Ticket Médio"]
        por_canal = por_canal.sort_values("Ticket Médio", ascending=True)
        fig_canal = px.bar(
            por_canal, x="Ticket Médio", y="Canal", orientation="h",
            color="Ticket Médio",
            color_continuous_scale=[[0, "#3b0764"], [0.5, "#7c3aed"], [1, "#a855f7"]],
            text=por_canal["Ticket Médio"].apply(lambda x: f"R${x:,.0f}")
        )
        fig_canal.update_traces(textposition="inside", textfont_color="#ffffff")
        fig_canal.update_layout(
            plot_bgcolor=ROXO_CARD, paper_bgcolor=ROXO_CARD,
            font_color=ROXO_TEXTO, height=360,
            margin=dict(l=10, r=20, t=30, b=10),
            yaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO)),
            xaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO),
                       range=[0, por_canal["Ticket Médio"].max() * 1.15]),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_canal, use_container_width=True)

    st.divider()

    # ── TICKET POR ANO ─────────────────────────────────────
    st.markdown("#### 📅 Faturamento por Mês")
    ordem_meses = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    nomes_pt = {"January":"Jan","February":"Fev","March":"Mar","April":"Abr",
                "May":"Mai","June":"Jun","July":"Jul","August":"Ago",
                "September":"Set","October":"Out","November":"Nov","December":"Dez"}
    por_mes = df_f.groupby("MesNome").agg(
        Faturamento=("Valor (R$)", "sum"),
        MesNum=("MesNum", "first")
    ).reset_index().sort_values("MesNum")
    por_mes["Mês"] = por_mes["MesNome"].map(nomes_pt)
    fig_mes = px.bar(
        por_mes, x="Mês", y="Faturamento",
        color="Faturamento",
        color_continuous_scale=[[0,"#3b0764"],[0.5,"#7c3aed"],[1,"#a855f7"]],
        text=por_mes["Faturamento"].apply(lambda x: f"R${x:,.0f}")
    )
    fig_mes.update_traces(textposition="outside", textfont_color="#e8d5ff")
    fig_mes.update_layout(
        plot_bgcolor=ROXO_CARD, paper_bgcolor=ROXO_CARD,
        font_color=ROXO_TEXTO, height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO), type="category"),
        yaxis=dict(gridcolor="#2d1b5e", tickfont=dict(color=ROXO_TEXTO)),
        coloraxis_showscale=False,
        bargap=0.25
    )
    st.plotly_chart(fig_mes, use_container_width=True)

else:
    st.markdown("""
    <div style='text-align:center; padding:100px 0'>
      <div style='font-size:5rem'>📡</div>
      <h2 style='color:#5b2d9e'>Carregue sua planilha na barra lateral</h2>
      <p style='color:#3d2b6b'>Clique em <b>📂 Subir Arquivo</b> para começar</p>
    </div>
    """, unsafe_allow_html=True)