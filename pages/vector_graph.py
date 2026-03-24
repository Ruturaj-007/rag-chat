import streamlit as st
import sys, os

# Make root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend as rag
import ui_components as ui

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
import numpy as np

# Page config
st.set_page_config(
    page_title="Neural Mind · Vector Space",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.inject_ui()
ui.render_navbar(active_page="vectors")

# Hero
ui.render_vector_hero()

# Waveform banner 
st.markdown("""
<div style="padding:0 40px;max-width:800px;margin:0 auto 40px;">
  <div id="waveform-container"></div>
</div>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    if(window.NM && window.NM.createWaveform) {
      window.NM.createWaveform('waveform-container');
    }
  });
  // Fallback if DOM already loaded
  setTimeout(function() {
    if(window.NM && window.NM.createWaveform && !document.querySelector('#waveform-container canvas')) {
      window.NM.createWaveform('waveform-container');
    }
  }, 500);
</script>
""", unsafe_allow_html=True)

# Query input 
st.markdown("""
<div style="padding:0 40px;max-width:700px;margin:0 auto;">
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        label="Query",
        label_visibility="collapsed",
        placeholder="Enter a query to visualize it in semantic space…",
        key="vector_query"
    )
with col2:
    plot_btn = st.button("🔮 Plot", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Info pills 
st.markdown("""
<div style="display:flex;gap:10px;justify-content:center;padding:20px 0 32px;flex-wrap:wrap;">
  <span class="nm-pill nm-pill-violet">PCA dimensionality reduction</span>
  <span class="nm-pill nm-pill-cyan">768D → 2D projection</span>
  <span class="nm-pill nm-pill-pink">all-mpnet-base-v2 embeddings</span>
  <span class="nm-pill nm-pill-violet">Top-5 semantic neighbors</span>
</div>
""", unsafe_allow_html=True)

# Plot logic 
if plot_btn:
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        st.markdown("""
        <script>window.NM && window.NM.soundThink && window.NM.soundThink();</script>
        """, unsafe_allow_html=True)

        with st.spinner("Reducing 768 dimensions to 2…"):
            # 1. Backend data
            data = rag.get_vectors_for_visualization(query)

            # 2. Prepare
            all_vectors = [data["query_vector"]] + [d["vector"] for d in data["docs"]]
            all_labels  = ["● YOUR QUERY"] + [d["content"][:45] + "…" for d in data["docs"]]
            all_types   = ["Query"]        + ["Document" for _ in data["docs"]]
            all_texts   = ["User Query"]   + [d["content"] for d in data["docs"]]

            # 3. PCA
            n_comp = min(2, len(all_vectors))
            pca = PCA(n_components=n_comp)
            reduced = pca.fit_transform(np.array(all_vectors))

            df = pd.DataFrame(reduced, columns=["x", "y"] if n_comp == 2 else ["x"])
            if n_comp == 1:
                df["y"] = 0

            df["label"]     = all_labels
            df["type"]      = all_types
            df["full_text"] = all_texts

        # 4. Custom plotly dark theme matching our CSS
        color_map = {
            "Query":    "#ec4899",
            "Document": "#06b6d4",
        }
        size_map = {"Query": 22, "Document": 14}
        df["size"] = df["type"].map(size_map)

        fig = go.Figure()

        for t in ["Document", "Query"]:
            sub = df[df["type"] == t]
            fig.add_trace(go.Scatter(
                x=sub["x"],
                y=sub["y"],
                mode="markers+text",
                name=t,
                text=sub["label"],
                textposition="top center",
                hovertext=sub["full_text"],
                hovertemplate="<b>%{text}</b><br><br>%{hovertext}<extra></extra>",
                marker=dict(
                    size=sub["size"].tolist(),
                    color=color_map[t],
                    opacity=0.9,
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                    symbol="circle",
                ),
                textfont=dict(
                    family="JetBrains Mono, monospace",
                    size=10,
                    color="rgba(240,238,255,0.75)",
                ),
            ))

        # Draw connection lines from query to each doc
        qx, qy = df.iloc[0]["x"], df.iloc[0]["y"]
        for _, row in df[df["type"] == "Document"].iterrows():
            fig.add_trace(go.Scatter(
                x=[qx, row["x"]],
                y=[qy, row["y"]],
                mode="lines",
                showlegend=False,
                line=dict(color="rgba(124,58,237,0.25)", width=1, dash="dot"),
                hoverinfo="none",
            ))

        fig.update_layout(
            title=dict(
                text="Semantic Distance Map",
                font=dict(family="Syne, sans-serif", size=20, color="#f0eeff"),
                x=0.04,
            ),
            paper_bgcolor="rgba(8, 6, 21, 0.0)",
            plot_bgcolor ="rgba(13, 10, 30, 0.9)",
            height=560,
            font=dict(family="Space Grotesk, sans-serif", color="#a89ec9"),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(42, 36, 80, 0.6)",
                zeroline=False,
                showticklabels=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(42, 36, 80, 0.6)",
                zeroline=False,
                showticklabels=False,
            ),
            legend=dict(
                bgcolor="rgba(13,10,30,0.7)",
                bordercolor="rgba(42,36,80,0.5)",
                borderwidth=1,
                font=dict(size=12, color="#a89ec9"),
            ),
            margin=dict(l=20, r=20, t=60, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Stats cards
        variance = pca.explained_variance_ratio_ * 100
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:0 40px 40px;max-width:800px;margin:0 auto;">
          <div class="nm-card" style="text-align:center;">
            <div style="font-family:var(--font-display);font-size:28px;font-weight:800;color:var(--accent-violet)">
              {len(data['docs'])}
            </div>
            <div style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">
              Documents Retrieved
            </div>
          </div>
          <div class="nm-card" style="text-align:center;">
            <div style="font-family:var(--font-display);font-size:28px;font-weight:800;color:var(--accent-cyan)">
              {variance[0]:.1f}%
            </div>
            <div style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">
              PC1 Variance
            </div>
          </div>
          <div class="nm-card" style="text-align:center;">
            <div style="font-family:var(--font-display);font-size:28px;font-weight:800;color:var(--accent-pink)">
              768D
            </div>
            <div style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">
              Original Space
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <script>window.NM && window.NM.soundSuccess && window.NM.soundSuccess();</script>
        """, unsafe_allow_html=True)
        ui.toast_success(f"Plotted {len(data['docs'])} documents in semantic space.")

        # Raw doc preview
        with st.expander("▸ View raw retrieved documents"):
            for i, doc in enumerate(data["docs"]):
                st.markdown(f"""
                <div class="nm-card" style="margin-bottom:12px;">
                  <div style="font-size:11px;font-family:var(--font-mono);color:var(--accent-cyan);
                    margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">
                    Document {i+1}
                  </div>
                  <div style="font-size:13px;color:var(--text-secondary);line-height:1.6;">
                    {doc['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)