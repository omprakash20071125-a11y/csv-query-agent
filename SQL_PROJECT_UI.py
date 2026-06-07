import uuid
import hashlib
import streamlit as st
import pandas as pd
from langgraph.types import Command
from SQL_project import sql_chatbot, load_csv, fetch_schema, conn

st.set_page_config(page_title="SQL Chatbot", page_icon="🧠", layout="centered")

# ── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #080b10;
    --surface:   #0e1219;
    --surface2:  #141922;
    --border:    #1e2535;
    --border2:   #2a3447;
    --accent:    #00d4ff;
    --accent2:   #7b61ff;
    --green:     #00e5a0;
    --red:       #ff4d6d;
    --amber:     #ffb830;
    --text:      #e8edf5;
    --muted:     #5a6882;
    --card-glow: 0 0 0 0.5px #1e2535, 0 4px 24px rgba(0,212,255,0.04);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* ── HERO ── */
.hero {
    padding: 2.8rem 0 2rem;
    text-align: center;
    position: relative;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: .6rem;
    opacity: .8;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin: 0 0 .5rem;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent) 60%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    letter-spacing: .04em;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.6rem 0 .7rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 0.5px;
    background: var(--border);
}

/* ── STAT PILLS ── */
.stat-row { display: flex; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
.stat-pill {
    background: var(--surface);
    border: 0.5px solid var(--border);
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text);
    display: flex; align-items: center; gap: 6px;
}
.stat-pill b { color: var(--accent); font-weight: 500; }

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 12px !important;
    padding: .5rem !important;
    transition: border-color .2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploader"] label {
    color: var(--muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

/* ── SUCCESS / WARNING / ERROR ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-width: 0.5px !important;
    font-size: 13px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 0.5px solid var(--border) !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 0.5px solid var(--border) !important;
    border-radius: 12px !important;
    padding: .8rem 1rem !important;
    margin-bottom: .5rem !important;
    box-shadow: var(--card-glow) !important;
}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--surface2) !important;
    border-color: var(--border2) !important;
}
[data-testid="stChatMessage"] p {
    font-size: 14px !important;
    line-height: 1.65 !important;
    color: var(--text) !important;
}

/* ── CODE BLOCKS ── */
[data-testid="stCode"] {
    background: #060810 !important;
    border: 0.5px solid var(--border2) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stCode"] pre {
    color: var(--accent) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 0.5px solid var(--border2) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    color: var(--text) !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
}

/* ── BUTTONS ── */
[data-testid="stButton"] button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    letter-spacing: .04em !important;
    border-radius: 8px !important;
    border: 0.5px solid var(--border2) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    transition: all .15s !important;
    padding: .45rem 1rem !important;
}
[data-testid="stButton"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(0,212,255,.05) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 0.5px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--muted) !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--muted) !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* ── APPROVAL CARD ── */
.approval-card {
    background: rgba(255,184,48,.04);
    border: 0.5px solid rgba(255,184,48,.3);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.approval-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: .5rem;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 2;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] button {
    background: rgba(0,229,160,.08) !important;
    border-color: rgba(0,229,160,.3) !important;
    color: var(--green) !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(0,229,160,.15) !important;
    border-color: var(--green) !important;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
defaults = {
    "file_hash":         None,
    "current_file_name": None,
    "messages":          [],
    "awaiting_approval": False,
    "interrupt_sql":     "",
    "csv_loaded":        False,
    "schema":            "",
    "df":                None,
    "chat_ended":        False,
    "thread_id":         str(uuid.uuid4()),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">natural language · sql · langgraph</div>
    <h1>SQL Chatbot</h1>
    <div class="hero-sub">upload csv → ask anything → get instant answers</div>
</div>
""", unsafe_allow_html=True)

# ── STEP 1 — UPLOAD ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 / upload data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop your CSV here or click to browse",
    type=["csv"],
    label_visibility="collapsed"
)

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_hash  = hashlib.md5(file_bytes).hexdigest()
    uploaded_file.seek(0)

    if file_hash != st.session_state.file_hash:
        df     = load_csv(uploaded_file)
        schema = fetch_schema(df)

        st.session_state.file_hash          = file_hash
        st.session_state.current_file_name  = uploaded_file.name
        st.session_state.schema             = schema
        st.session_state.df                 = df
        st.session_state.csv_loaded         = True
        st.session_state.chat_ended         = False
        st.session_state.messages           = []
        st.session_state.thread_id          = str(uuid.uuid4())

    # stat pills
    df = st.session_state.df
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">📄 <b>{st.session_state.current_file_name}</b></div>
        <div class="stat-pill">rows <b>{len(df):,}</b></div>
        <div class="stat-pill">cols <b>{len(df.columns)}</b></div>
        <div class="stat-pill">size <b>{df.memory_usage(deep=True).sum() // 1024} KB</b></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.session_state.df = None

if st.session_state.df is not None:
    with st.expander("preview data", expanded=False):
        st.dataframe(st.session_state.df, use_container_width=True, height=260)

# ── STEP 2 — CHAT ─────────────────────────────────────────────────────────────

# ── NO CSV GUARD ────────────────────────────────────────────────────────────
if not st.session_state.csv_loaded:
    st.markdown('<div class="section-label">02 / chat</div>', unsafe_allow_html=True)
    st.chat_input('upload a csv file first to start chatting...', disabled=True)
    st.error('⚠️ No data loaded — please upload a CSV file above to start chatting.')

if st.session_state.csv_loaded:
    st.markdown('<div class="section-label">02 / chat</div>', unsafe_allow_html=True)

    # ── END CHAT ─────────────────────────────────────────────────────────────
    if st.session_state.chat_ended:
        st.success("Session complete — your updated data is ready.")
        final_df  = pd.read_sql("SELECT * FROM data", conn)
        csv_bytes = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ download updated csv",
            data=csv_bytes,
            file_name="updated_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("↺  start new session", use_container_width=True):
            for key in list(defaults.keys()):
                st.session_state.pop(key, None)
            st.rerun()

    else:
        # ── CHAT HISTORY ─────────────────────────────────────────────────────
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                ◈<br>
                no messages yet<br>
                ask anything about your data below
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                role   = msg["role"]
                avatar = "👤" if role == "user" else "🤖"
                with st.chat_message(role, avatar=avatar):
                    if msg.get("sql"):
                        st.code(msg["sql"], language="sql")
                    if msg.get("feedback"):
                        st.caption(f"→ {msg['feedback']}")
                    st.write(msg["content"])

        # ── APPROVAL CARD ─────────────────────────────────────────────────────
        if st.session_state.awaiting_approval:
            st.markdown("""
            <div class="approval-card">
                <div class="approval-title">⚠ human approval required</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(st.session_state.interrupt_sql, language="sql")
            col1, col2 = st.columns(2)
            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            with col1:
                if st.button("✓  approve & execute", use_container_width=True):
                    with st.spinner("executing..."):
                        res = sql_chatbot.invoke(Command(resume="yes"), config=config)
                    answer = res.get("result_llm") or res.get("result") or "Done."
                    st.session_state.messages.append({
                        "role": "assistant", "content": f"✓ {answer}",
                        "sql": None, "feedback": None,
                    })
                    st.session_state.awaiting_approval = False
                    st.session_state.df = pd.read_sql("SELECT * FROM data", conn)
                    st.rerun()

            with col2:
                if st.button("✕  cancel", use_container_width=True):
                    with st.spinner("cancelling..."):
                        sql_chatbot.invoke(Command(resume="no"), config=config)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "cancelled — no changes made.",
                        "sql": None, "feedback": None,
                    })
                    st.session_state.awaiting_approval = False
                    st.rerun()

        # ── CHAT INPUT ────────────────────────────────────────────────────────
        user_input = st.chat_input(
            "ask anything — e.g. who has the highest salary?",
            disabled=st.session_state.awaiting_approval,
        )

        if user_input:
            st.session_state.messages.append({
                "role": "user", "content": user_input,
                "sql": None, "feedback": None,
            })
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)

            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            with st.spinner("generating sql..."):
                final_state = sql_chatbot.invoke(
                    {
                        "query":      user_input,
                        "schema":     st.session_state.schema,
                        "feedback":   "",
                        "sql_query":  "",
                        "result":     "",
                        "result_llm": "",
                    },
                    config=config,
                )

            graph_state    = sql_chatbot.get_state(config)
            is_interrupted = bool(graph_state.tasks and any(
                hasattr(t, "interrupts") and t.interrupts
                for t in graph_state.tasks
            ))

            if is_interrupted:
                st.session_state.awaiting_approval = True
                st.session_state.interrupt_sql     = final_state.get("sql_query", "")
                st.session_state.messages.append({
                    "role":     "assistant",
                    "content":  "this query modifies data — review and approve above.",
                    "sql":      final_state.get("sql_query", ""),
                    "feedback": final_state.get("feedback", ""),
                })
            else:
                answer = final_state.get("result_llm") or final_state.get("result") or "no result."
                st.session_state.messages.append({
                    "role":     "assistant",
                    "content":  answer,
                    "sql":      final_state.get("sql_query", ""),
                    "feedback": final_state.get("feedback", ""),
                })
            st.rerun()

        # ── BOTTOM BUTTONS ────────────────────────────────────────────────────
        if st.session_state.messages:
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⌫  clear chat", use_container_width=True):
                    st.session_state.messages          = []
                    st.session_state.awaiting_approval = False
                    st.session_state.thread_id         = str(uuid.uuid4())
                    st.rerun()
            with col2:
                if st.button("◼  end session", use_container_width=True):
                    st.session_state.chat_ended = True
                    st.rerun()