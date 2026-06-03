import streamlit as st
from config.settings import SUPPORTED_CURRENCIES, SUPPORTED_LANGUAGES, APP_NAME
from utils.translations import _
from data.fetcher import StockDataFetcher

def setup_page(page_title: str, page_icon: str, layout: str = "wide"):
    """
    Initializes the page config, injects global CSS (including dynamic theme),
    hides the native Streamlit sidebar nav, and renders the custom unified sidebar.
    """
    st.set_page_config(page_title=f"{page_title} - {APP_NAME}", page_icon=page_icon, layout=layout, initial_sidebar_state="expanded")
    
    theme = st.session_state.get("theme", "dark")
    t_bg = "#0E1117" if theme == "dark" else "#F8FAFC"
    t_fg = "#f1f5f9" if theme == "dark" else "#0f172a"
    t_card = "#1A1F2E" if theme == "dark" else "#FFFFFF"
    t_sidebar = "linear-gradient(180deg, #111928, #0e1117, #111928)" if theme == "dark" else "linear-gradient(180deg, #F8FAFC, #FFFFFF, #F8FAFC)"
    t_border = "rgba(255,255,255,0.06)" if theme == "dark" else "rgba(0,0,0,0.08)"
    t_muted = "#94a3b8" if theme == "dark" else "#64748b"
    t_input = "#1a1f2e" if theme == "dark" else "#FFFFFF"

    # Inject global CSS
    st.markdown(f"""
    <style>
    :root {{
        --theme-bg: {t_bg};
        --theme-fg: {t_fg};
        --theme-card: {t_card};
        --theme-border: {t_border};
        --theme-muted: {t_muted};
        --theme-input: {t_input};
    }}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif !important;
        background-color: {t_bg} !important;
        color: {t_fg} !important;
    }}

    .main .block-container {{ padding: 2rem 1.5rem 2rem; max-width: 1200px; }}

    [data-testid="stSidebar"] {{
        background: {t_sidebar} !important;
        border-right: 1px solid {t_border} !important;
    }}
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] p {{
        color: {t_fg} !important; font-family: 'Inter', sans-serif !important;
    }}
    hr {{ border-color: {t_border} !important; }}

    /* Hide native Streamlit navigation */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Global UI Elements */
    [data-testid="stMetric"] {{
        background: {t_card} !important;
        border: 1px solid {t_border} !important;
        border-radius: 12px !important; padding: 1rem !important;
        border-left: 3px solid #667eea !important;
        transition: all 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{
        border-left-color: #a78bfa !important;
        box-shadow: 0 0 15px rgba(102,126,234,0.12);
        transform: translateY(-2px);
    }}
    [data-testid="stMetric"] label {{ color: {t_muted} !important; font-weight: 500 !important; font-size: 0.8rem !important; text-transform: uppercase; }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; font-weight: 700 !important; color: {t_fg} !important; }}

    .stButton > button {{
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important; transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.25);
    }}
    .stButton > button:hover {{ box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important; transform: translateY(-2px) !important; }}

    .stTabs [data-baseweb="tab-list"] {{ background: {t_card} !important; border: 1px solid {t_border} !important; border-radius: 10px !important; padding: 3px !important; }}
    .stTabs [data-baseweb="tab"] {{ color: {t_muted} !important; font-weight: 500 !important; border-radius: 8px !important; }}
    .stTabs [aria-selected="true"] {{ background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; }}

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {{
        background-color: {t_input} !important; border-color: {t_border} !important;
        color: {t_fg} !important; border-radius: 8px !important;
    }}

    [data-testid="stExpander"] {{ background: {t_card} !important; border: 1px solid {t_border} !important; border-radius: 12px !important; }}
    [data-testid="stExpander"] summary {{ font-weight: 600 !important; color: {t_fg} !important; }}

    [data-testid="stPlotlyChart"] {{ border-radius: 12px; overflow: hidden; border: 1px solid {t_border}; background: {t_card} !important; }}
    
    .brand {{ text-align: center; padding: 0.8rem 0; margin-bottom: 0.5rem; border-bottom: 1px solid {t_border}; }}
    .brand .b-icon {{ display: flex; justify-content: center; margin-bottom: 0.4rem; }}
    .brand .b-name {{
        font-size: 1.15rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }}
    .brand .b-ver {{ font-size: 0.68rem; color: {t_muted}; letter-spacing: 1px; margin-top: 0.1rem; }}
    </style>
    """, unsafe_allow_html=True)

    # Render unified custom sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="brand">
            <div class="b-icon">
                <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="url(#logo-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <defs>
                    <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#667eea" />
                      <stop offset="100%" stop-color="#f093fb" />
                    </linearGradient>
                  </defs>
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
            </div>
            <div class="b-name">{APP_NAME}</div>
            <div class="b-ver">v2.0 — PRO</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### Main Menu")

        # Native Streamlit Navigation (Prevents page reload and state loss)
        st.page_link("app.py", label=_("home"), icon=":material/home:")
        st.page_link("pages/1_Stock_Analysis.py", label=_("stock_analysis"), icon=":material/monitoring:")
        st.page_link("pages/2_Portfolio_Builder.py", label=_("portfolio_builder"), icon=":material/pie_chart:")
        st.page_link("pages/3_Efficient_Frontier.py", label=_("efficient_frontier"), icon=":material/scatter_plot:")
        st.page_link("pages/4_Monte_Carlo.py", label=_("monte_carlo"), icon=":material/casino:")
        st.page_link("pages/5_Risk_Analysis.py", label=_("risk_analysis"), icon=":material/security:")

        st.markdown("---")
        st.markdown(f"### {_('settings')}")
        
        # Theme (Using radio/pills instead of selectbox for better UX)
        theme_options = ["dark", "light"]
        current_theme = st.session_state.get("theme", "dark")
        # Ensure index doesn't crash if current_theme is invalid
        theme_idx = theme_options.index(current_theme) if current_theme in theme_options else 0
        new_theme = st.radio(_("theme"), theme_options, index=theme_idx, format_func=lambda x: _(f"{x}_mode"), horizontal=True)
        if new_theme != current_theme:
            st.session_state["theme"] = new_theme
            st.rerun()

        # Language
        lang_names = list(SUPPORTED_LANGUAGES.keys())
        current_lang_code = st.session_state.get("language", "en")
        current_lang = [k for k, v in SUPPORTED_LANGUAGES.items() if v == current_lang_code]
        current_lang = current_lang[0] if current_lang else "English"
        new_lang = st.selectbox(_("language"), lang_names, index=lang_names.index(current_lang))
        if SUPPORTED_LANGUAGES[new_lang] != current_lang_code:
            st.session_state["language"] = SUPPORTED_LANGUAGES[new_lang]
            st.rerun()

        # Currency
        curr_names = list(SUPPORTED_CURRENCIES.keys())
        current_curr_code = st.session_state.get("currency", "USD")
        current_curr = [k for k, v in SUPPORTED_CURRENCIES.items() if v == current_curr_code]
        current_curr = current_curr[0] if current_curr else "USD ($)"
        new_curr = st.selectbox(_("currency"), curr_names, index=curr_names.index(current_curr))
        if SUPPORTED_CURRENCIES[new_curr] != current_curr_code:
            st.session_state["currency"] = SUPPORTED_CURRENCIES[new_curr]
            # Fetch new FX rate
            fx = StockDataFetcher().get_exchange_rate("USD", SUPPORTED_CURRENCIES[new_curr])
            st.session_state["fx_rate"] = fx
            st.rerun()

        st.markdown("---")
        from datetime import datetime
        now = datetime.now()
        is_open = (now.weekday() < 5) and (9 <= now.hour < 16)
        dot, label = ("Open", "Market is Open") if is_open else ("Closed", "Market is Closed")
        st.caption(f"Status: {label}")
