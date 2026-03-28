# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:58:24 2026

@author: Shobhit Sharma
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="ChatGPT Prompt Analysis Dashboard",
    layout="wide"
)

st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
}

/* KPI Cards */
.metric-card {
    background: #020617;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #1e293b;
    text-align: center;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
}

/* Section headers */
h1, h2, h3 {
    color: #e2e8f0;
}

/* Improve spacing */
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# TITLE
# -------------------------
st.markdown("---")
st.markdown("""
<h1 style='text-align: center; color: #38bdf8;'>
📊 ChatGPT Prompt Analysis Dashboard
</h1>
<p style='text-align: center; color: #94a3b8;'>
Analyze how prompt types, length, and context affect ChatGPT outputs
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data.csv.gz")

df = load_data()

df["verbosity"] = pd.cut(
    df["output_word_count"],
    bins=[0, 50, 150, 300, 1000],
    labels=["Concise", "Moderate", "Verbose", "Very Verbose"]
)

verbosity_filter = st.sidebar.multiselect(
    "Select Verbosity Level",
    df["verbosity"].unique()
)

if verbosity_filter:
    df = df[df["verbosity"].isin(verbosity_filter)]

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    ["Overview", "Prompt Types", "Readability", "Context Impact", "Length vs Complexity", "WordCloud Analysis", "Verbosity"]
)


# -------------------------
# OVERVIEW
# -------------------------
if section == "Overview":
    st.header("📌 Project Overview")

    # -------------------------
    # KPI METRICS
    # -------------------------
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📌 Total Prompts</h4>
            <h2>{len(df)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📖 Avg Readability</h4>
            <h2>{round(df["Readability_Score"].mean(), 2)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📏 Avg Output Length</h4>
            <h2>{int(df["output_word_count"].mean())}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🧩 Prompt Types</h4>
            <h2>{df["prompt_type"].nunique()}</h2>
        </div>
        """, unsafe_allow_html=True)
    # -------------------------
    # MINI VISUAL (NON-DUPLICATE)
    # -------------------------
    st.markdown("---")
    st.subheader("📊 Prompt Length Distribution")

    fig = px.histogram(
        df,
        x="instruction_word_count",
        nbins=30,
        title="Distribution of Prompt Length"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # KEY INSIGHTS (IMPROVED)
    # -------------------------
    st.markdown("---")
    st.subheader("🔍 Key Insights")

    st.markdown("""
    - **Creative tasks dominate** ChatGPT usage patterns  
    - Majority of responses fall under **medium readability**  
    - Adding extra context:
        - 🔽 reduces response length  
        - 🔼 improves readability  
    - Prompt length has a **very weak correlation** with output complexity  
    - Response quality depends more on **clarity of instruction than length**
    """)

    # -------------------------
    # DATA PREVIEW
    # -------------------------
    st.markdown("---")
    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(10))


# -------------------------
# PROMPT TYPES
# -------------------------
elif section == "Prompt Types":
    st.header("🧩 Distribution of Prompt Types")

    fig = px.histogram(df, x="prompt_type", color="prompt_type")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Creative tasks are the most frequent
    - Listing and explanation tasks are also common
    - Questions and problem-solving are less frequent
    """)


# -------------------------
# READABILITY
# -------------------------
elif section == "Readability":
    st.header("📖 Readability Distribution")

    fig = px.histogram(df, x="Prompt_readability_level", color="Prompt_readability_level")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Most responses are **medium readable**
    - Easy readability is also significant
    - Very difficult responses are rare
    """)


# -------------------------
# CONTEXT IMPACT
# -------------------------
elif section == "Context Impact":
    st.header("📈 Effect of Extra Context")

    grouped = df.groupby("has_extra_context").agg({
        "output_word_count": "mean",
        "Readability_Score": "mean"
    }).reset_index()

    fig = px.bar(
        grouped,
        x="has_extra_context",
        y=["output_word_count", "Readability_Score"],
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Adding context:
        - Reduces output length
        - Improves readability score
    - More context → more precise answers
    """)


# WORDCLOUD


elif section == "WordCloud Analysis":
    st.header("☁️ WordCloud Analysis")

    text_type = st.selectbox(
        "Select Text Source",
        ["Instruction (Prompts)", "Output (Responses)"]
    )

    if text_type == "Instruction (Prompts)":
        text_data = " ".join(df["instruction"].dropna().astype(str))
    else:
        text_data = " ".join(df["output"].dropna().astype(str))

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='black',
        colormap='viridis'
    ).generate(text_data)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")

    st.pyplot(fig)
    
    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Frequent words reveal common task patterns
    - Prompts heavily include action words like *write, create, explain*
    - Outputs reflect structured and descriptive language
    """)
    
# VERBOSITY




elif section == "Verbosity":
    st.header("📏 Response Verbosity Analysis")

    import plotly.express as px

    fig = px.histogram(
        df,
        x="verbosity",
        color="verbosity",
        title="Distribution of Response Verbosity"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Avg verbosity stats
    col1, col2 = st.columns(2)

    col1.metric(
        "Average Output Length",
        int(df["output_word_count"].mean())
    )

    col2.metric(
        "Max Output Length",
        int(df["output_word_count"].max())
    )

    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Most responses fall under **Moderate verbosity**
    - Very verbose outputs are less frequent
    - Short prompts can still generate long responses
    - Verbosity depends more on task type than prompt length
    """)
    


# -------------------------
# LENGTH VS COMPLEXITY
# -------------------------
elif section == "Length vs Complexity":
    st.header("📊 Prompt Length vs Output Complexity")

    fig = px.scatter(
        df,
        x="instruction_word_count",
        y="Readability_Score",
        trendline="ols",
        opacity=0.5
    )

    fig.update_layout(
    yaxis=dict(range=[-200, 150]))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown("""
    ### 📌 Insights
    - Slight positive correlation between length and complexity
    - Very short prompts → unpredictable readability
    - Longer prompts → more structured responses
    """)
    
st.markdown("---")

st.markdown("""
<p style='text-align: center; color: grey;'>
Built by Shobhit Sharma • ChatGPT Prompt Analysis • Hugging Face Dataset
</p>
""", unsafe_allow_html=True)