import streamlit as st
import sys, os

# Ensure project root is on path (fixes Pylance + Streamlit runtime)
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import backend as rag
import ui_components as ui

# Page config 
st.set_page_config(
    page_title="Neural Mind · RAG Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global UI (CSS + canvas + JS) 
ui.inject_ui()
ui.render_navbar(active_page="chat")

# Hero 
ui.render_hero()

# Layout: sidebar left | chat right 
st.markdown('<div class="nm-chat-layout">', unsafe_allow_html=True)

# LEFT COLUMN: knowledge upload 
col_side, col_chat = st.columns([1, 3], gap="large")

with col_side:
    st.markdown("""
    <div class="nm-card reveal">
      <div class="nm-card-title">Upload Context</div>
      <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px;font-family:var(--font-mono);">
        Paste any text to add to your MongoDB knowledge base.
      </p>
    </div>
    """, unsafe_allow_html=True)

    user_text = st.text_area(
        label="Knowledge input",
        label_visibility="collapsed",
        placeholder="Paste articles, docs, notes, anything…",
        height=160,
        key="knowledge_input",
    )

    if st.button("⬆ Upload to Knowledge Base", use_container_width=True):
        if user_text.strip():
            with st.spinner("Embedding & storing…"):
                rag.ingest_text(user_text)
            st.markdown("""
            <script>window.NM && window.NM.soundSuccess && window.NM.soundSuccess();</script>
            """, unsafe_allow_html=True)
            ui.toast_success("Uploaded and embedded successfully!")
        else:
            st.warning("Please enter some text first.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Info card
    st.markdown("""
    <div class="nm-card reveal" style="padding:18px;">
      <div style="font-size:11px;font-family:var(--font-mono);color:var(--text-muted);line-height:1.8;">
        <div style="color:var(--accent-cyan);margin-bottom:8px;font-weight:600;">HOW IT WORKS</div>
        <div>① Paste text → MongoDB Atlas</div>
        <div>② Query → mpnet-768 embeds it</div>
        <div>③ Vector search → top-3 docs</div>
        <div>④ Gemini 2.5 Flash answers</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# RIGHT COLUMN: chat window 
with col_chat:
    st.markdown("""
    <div class="nm-chat-window reveal">
      <div class="nm-chat-header">
        <div class="nm-chat-header-info">
          <div class="nm-chat-avatar">🧠</div>
          <div>
            <div class="nm-chat-header-name">Neural Mind</div>
            <div class="nm-chat-header-sub">● Active · Gemini 2.5 Flash + RAG</div>
          </div>
        </div>
        <div style="font-size:11px;font-family:var(--font-mono);color:var(--text-muted);">
          MongoDB Atlas · all-mpnet-base-v2
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Message history 
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render intro message if no history
    if not st.session_state.messages:
        st.markdown("""
        <div class="nm-message" style="padding:28px 28px 0;">
          <div class="nm-msg-avatar ai">🧠</div>
          <div class="nm-msg-bubble">
            Hey! I'm Neural Mind. Upload some text to my knowledge base
            using the panel on the left, then ask me anything about it.
            I'll retrieve the most relevant context and answer precisely. ✦
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Existing messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            ui.render_message("user", message["content"])
        else:
            ui.render_message(
                "assistant",
                message["content"],
                sources=message.get("sources")
            )

    # Chat input 
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    prompt = st.chat_input("Ask anything about your knowledge base…")

    if prompt:
        # Play send sound
        st.markdown("""
        <script>
          if(window.NM) {
            window.NM.soundSend();
            window.NM.soundThink();
          }
        </script>
        """, unsafe_allow_html=True)

        # Show user message immediately
        ui.render_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Thinking indicator
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("""
        <div class="nm-message">
          <div class="nm-msg-avatar ai">🧠</div>
          <div class="nm-msg-bubble">
            <div class="nm-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(""):
            response_data = rag.get_rag_response(prompt)
            answer  = response_data["answer"]
            sources = response_data["sources"]

        # Clear thinking dot, render answer
        thinking_placeholder.empty()
        ui.render_message("assistant", answer, sources=sources)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })

        # Success sound
        st.markdown("""
        <script>window.NM && window.NM.soundSuccess && window.NM.soundSuccess();</script>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close nm-chat-layout

# Footer 
st.markdown("""
<div style="text-align:center;padding:40px;font-size:11px;
  font-family:var(--font-mono);color:var(--text-muted);border-top:1px solid var(--border-dim);
  margin-top:40px;">
  Neural Mind · RAG Pipeline ·
  <span style="color:var(--accent-violet)">MongoDB</span> +
  <span style="color:var(--accent-cyan)">HuggingFace</span> +
  <span style="color:var(--accent-pink)">Gemini</span>
</div>
""", unsafe_allow_html=True)