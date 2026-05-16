import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_javascript import st_javascript
from dotenv import load_dotenv

load_dotenv()

from agent.graph import run_agent
from agent.memory import format_chat_history
from data.geo import get_nearby_areas

st.set_page_config(
    page_title="Dine AI — Smart Restaurant Discovery",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for sleek design ---
st.markdown("""
<style>
    /* Global */
    [data-testid="stAppViewContainer"] {
        background: #fafbff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #001E47 0%, #002D6B 100%);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #94B8E0 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Dropdown inputs - make selected value visible */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
    }
    /* Multiselect tags */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #006FCF !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] * {
        color: #ffffff !important;
    }
    /* Date/time inputs */
    [data-testid="stSidebar"] [data-baseweb="input"] {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"] input {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stDateInput > div > div,
    [data-testid="stSidebar"] .stTimeInput > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 8px;
        padding-top: 4px;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 12px 0 !important;
    }
    [data-testid="stSidebar"] .stCaption p {
        color: #6B9FD4 !important;
    }
    [data-testid="stSidebar"] small {
        color: #6B9FD4 !important;
    }

    /* Genre/Card buttons in sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        padding: 6px 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.15) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #006FCF !important;
        border: 2px solid #4DA3FF !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 0 8px rgba(0, 111, 207, 0.5) !important;
    }

    /* Active selections display */
    .active-tags {
        background: rgba(0, 111, 207, 0.2);
        border: 1px solid rgba(77, 163, 255, 0.4);
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.8rem;
        color: #A8D4FF;
    }

    /* Main header area */
    .header-container {
        background: linear-gradient(135deg, #006FCF 0%, #0044A4 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: white;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.8);
        margin-top: 4px;
    }

    /* Chat styling */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
    }

    /* Toggle styling */
    [data-testid="stSidebar"] .stToggle label span {
        color: #ffffff !important;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

GENRE_OPTIONS = [
    {"icon": "☕", "label": "Cafe"},
    {"icon": "🍛", "label": "North Indian"},
    {"icon": "🥘", "label": "South Indian"},
    {"icon": "🍝", "label": "Italian"},
    {"icon": "🍣", "label": "Japanese"},
    {"icon": "🥡", "label": "Asian"},
    {"icon": "🍺", "label": "Brewery"},
    {"icon": "🥩", "label": "BBQ"},
    {"icon": "🦐", "label": "Seafood"},
    {"icon": "🌿", "label": "Vegetarian"},
    {"icon": "👔", "label": "Fine Dining"},
    {"icon": "🍹", "label": "Nightlife"},
]

CARD_OPTIONS = [
    {"icon": "💎", "label": "Amex Platinum", "key": "amex_platinum"},
    {"icon": "🥇", "label": "Amex Gold", "key": "amex_gold"},
    {"icon": "🍽️", "label": "HDFC Diners Club", "key": "hdfc_diners"},
    {"icon": "🏦", "label": "ICICI Sapphiro", "key": "icici_sapphiro"},
    {"icon": "✈️", "label": "Axis Atlas", "key": "axis_atlas"},
    {"icon": "🛍️", "label": "SBI Elite", "key": "sbi_elite"},
    {"icon": "🏧", "label": "SBI SimplyCLICK", "key": "sbi_simplyclick"},
]

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; padding: 8px 0 16px;'>"
        "<span style='font-size:1.4rem; font-weight:700; letter-spacing:1px;'>"
        "🍽️ DINE AI</span><br>"
        "<span style='font-size:0.7rem; color:#6B9FD4; letter-spacing:2px;'>"
        "SMART RESTAURANT DISCOVERY</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Genre filters
    st.markdown("### What are you craving?")
    if "selected_genres" not in st.session_state:
        st.session_state.selected_genres = []

    cols = st.columns(3)
    for i, genre in enumerate(GENRE_OPTIONS):
        col = cols[i % 3]
        with col:
            is_selected = genre["label"] in st.session_state.selected_genres
            label = f"{'✓ ' if is_selected else ''}{genre['icon']} {genre['label']}"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(label, key=f"g_{i}", use_container_width=True, type=btn_type):
                if is_selected:
                    st.session_state.selected_genres.remove(genre["label"])
                else:
                    st.session_state.selected_genres.append(genre["label"])
                st.rerun()

    if st.session_state.selected_genres:
        st.markdown(
            f'<div class="active-tags">✓ {" · ".join(st.session_state.selected_genres)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # My Cards — select cards to see benefits
    st.markdown("### 💳 My Cards")
    st.caption("Select your cards to see dining rewards")
    if "selected_cards" not in st.session_state:
        st.session_state.selected_cards = []

    cols = st.columns(2)
    for i, card in enumerate(CARD_OPTIONS):
        col = cols[i % 2]
        with col:
            is_selected = card["label"] in st.session_state.selected_cards
            label = f"{'✓ ' if is_selected else ''}{card['icon']} {card['label']}"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(label, key=f"card_{i}", use_container_width=True, type=btn_type):
                if is_selected:
                    st.session_state.selected_cards.remove(card["label"])
                else:
                    st.session_state.selected_cards.append(card["label"])
                st.rerun()

    if st.session_state.selected_cards:
        st.markdown(
            f'<div class="active-tags">💳 {" · ".join(st.session_state.selected_cards)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Preferences
    st.markdown("### Preferences")
    near_me_on = st.session_state.get("near_me_toggle", False)
    if near_me_on:
        location = "Bangalore"
        st.selectbox("City", ["Bangalore"], disabled=True, help="Location detected via Near Me")
    else:
        location = st.selectbox("City", ["Any", "Bangalore", "Mumbai", "Delhi"])
    budget = st.select_slider(
        "Budget (for two)",
        options=["Any", "₹500", "₹1500", "₹3000", "₹5000", "₹5000+"],
        value="Any",
    )
    dietary = st.multiselect(
        "Dietary",
        ["Vegetarian", "Vegan", "Gluten-free", "Jain", "Seafood"],
    )
    occasion = st.selectbox(
        "Occasion",
        ["Any", "Date night", "Business dinner", "Casual", "Family", "Celebration", "Brunch"],
    )

    st.markdown("---")

    # Availability
    st.markdown("### Availability")
    avail_date = st.date_input("Date", value=None)
    avail_time = st.time_input("Time", value=None)

    st.markdown("---")

    # Near Me (Bangalore geolocation)
    st.markdown("### 📍 Near Me")
    if "user_location" not in st.session_state:
        st.session_state.user_location = None
    if "nearby_areas" not in st.session_state:
        st.session_state.nearby_areas = []

    near_me_active = st.toggle("Enable location", value=False, key="near_me_toggle")
    if near_me_active:
        loc_js = st_javascript("""
        await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve({lat: pos.coords.latitude, lng: pos.coords.longitude}),
                (err) => resolve(null),
                {timeout: 10000}
            );
        });
        """)
        if loc_js and isinstance(loc_js, dict) and "lat" in loc_js:
            st.session_state.user_location = loc_js
            nearby = get_nearby_areas(loc_js["lat"], loc_js["lng"])
            st.session_state.nearby_areas = nearby
            if nearby:
                area_names = [f"{a['area']} ({a['distance_km']}km)" for a in nearby[:5]]
                st.markdown(
                    f'<div class="active-tags">📍 Nearby: {" · ".join(area_names)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No restaurants found within 7km")
        elif loc_js == 0:
            pass  # st_javascript returns 0 initially before resolving
        else:
            st.caption("Waiting for location access...")

    st.markdown("---")

    # Toggles
    st.markdown("### Enhance")
    top_rated_only = st.toggle("⭐ 4.5+ Rated Only", value=False)

    st.markdown("---")

    # Actions
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
    with c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.selected_genres = []
            st.session_state.selected_cards = []
            st.rerun()

    st.markdown(
        "<div style='text-align:center; padding-top:12px;'>"
        "<small>Built with LangGraph · RAG · GPT-4</small></div>",
        unsafe_allow_html=True,
    )

# --- Main Content ---
st.markdown(
    '<div class="header-container">'
    '<p class="header-title">🍽️ Dine AI</p>'
    '<p class="header-subtitle">'
    'Your AI-powered restaurant discovery agent — find the perfect spot in seconds'
    '</p></div>',
    unsafe_allow_html=True,
)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Display Chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Welcome ---
WELCOME_MSG = (
    "Hi! I'm **Dine AI** — your personal restaurant discovery agent.\n\n"
    "**How to use:**\n"
    "1. Pick cuisines & set preferences in the sidebar\n"
    "2. Ask me anything below\n\n"
    "**Try:**\n"
    "- *\"Romantic Italian spot in Bangalore, under 3k\"*\n"
    "- *\"Best restaurants with card rewards in Mumbai\"*\n"
    "- *\"Table for 2 at Indian Accent, 8pm?\"*"
)

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(WELCOME_MSG)
    st.session_state.messages.append({"role": "assistant", "content": WELCOME_MSG})

# --- Chat Input ---
user_input = st.chat_input("What are you in the mood for?")

if user_input:
    context_parts = []

    if st.session_state.selected_genres:
        context_parts.append(
            f"Cuisine/category: {', '.join(st.session_state.selected_genres)}"
        )
    if location != "Any":
        context_parts.append(f"City: {location}")
    if budget != "Any":
        budget_map = {"₹500": 500, "₹1500": 1500, "₹3000": 3000, "₹5000": 5000, "₹5000+": 99999}
        context_parts.append(f"Budget: under {budget} for two")
    if dietary:
        context_parts.append(f"Dietary: {', '.join(dietary)}")
    if occasion != "Any":
        context_parts.append(f"Occasion: {occasion}")
    if avail_date:
        context_parts.append(f"Date: {avail_date.strftime('%A, %B %d')}")
    if avail_time:
        context_parts.append(f"Time: {avail_time.strftime('%I:%M %p')}")
    if st.session_state.get("selected_cards"):
        context_parts.append(
            f"IMPORTANT: User has these cards: {', '.join(st.session_state.selected_cards)}. "
            "Show dining rewards, discounts, bonus points, and complimentary perks available "
            "at each restaurant for these cards."
        )
    if top_rated_only:
        context_parts.append("Only show restaurants rated 4.5+")
    if st.session_state.get("nearby_areas"):
        area_list = [a["area"] for a in st.session_state.nearby_areas[:5]]
        context_parts.append(
            f"User is near these Bangalore areas (sorted by proximity): {', '.join(area_list)}. "
            "Prioritize restaurants in these areas."
        )

    enhanced_prompt = user_input
    if context_parts:
        enhanced_prompt = f"{user_input}\n\n[Filters: {'; '.join(context_parts)}]"

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Searching restaurants..."):
            try:
                chat_history = format_chat_history(st.session_state.chat_history)
                response, updated_history = run_agent(
                    enhanced_prompt, chat_history=chat_history
                )
                st.session_state.chat_history = updated_history
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                error_str = str(e)
                if "api_key" in error_str.lower() or "auth" in error_str.lower():
                    error_msg = "⚠️ API key missing or invalid. Set OPENAI_API_KEY in .env"
                elif "rate" in error_str.lower():
                    error_msg = "⚠️ Rate limited. Wait a moment and try again."
                else:
                    error_msg = f"⚠️ Error: {error_str}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
