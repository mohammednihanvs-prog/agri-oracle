import streamlit as st
import google.genai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Agri-Oracle: Smart Agriculture Advisor",
    page_icon="🌾",
    layout="centered"
)

# --- SECURE API CLIENT SETUP ---
try:
    # Look for the secret in st.secrets
    API_KEY = st.secrets["GENAI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"⚠️ API Key Initialization Error: {e}")
    st.info("Make sure your secrets.toml has: GENAI_API_KEY = 'your_actual_key'")
    st.stop()

# Using standard model string identifier
MODEL_NAME = "gemini-1.5-flash"

# --- SIDEBAR: USER DATA ---
st.sidebar.header("📍 User Parameters")
location = st.sidebar.selectbox("Location", ["Kerala (Kuttanad)", "Kerala (Other)"])
soil = st.sidebar.selectbox("Soil Type", ["Sandy Loam", "Clay", "Laterite"])
capital = st.sidebar.number_input("Available Capital (₹)", value=50000, step=1000)

# --- DATA CONSTANTS ---
weather_forecast = "90-day forecast: 15% increase in monsoon rain."
prices = {"Ginger": 180, "Turmeric": 90}

# --- UI: DASHBOARD HEADER ---
st.title("🌾 Agri-Oracle: Smart Agriculture Advisor")
st.markdown("---")

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Weather Outlook", "Monsoon +15%", delta="High Risk", delta_color="inverse")
col2.metric("Ginger Price", f"₹{prices['Ginger']}/kg")
col3.metric("Turmeric Price", f"₹{prices['Turmeric']}/kg")

# --- AI LOGIC (CACHED) ---
@st.cache_data(show_spinner=False)
def get_recommendation(loc, sl, cap, lang):
    prompt = f"""
    Act as a Senior Agricultural Consultant. 
    User Data: Location {loc}, Soil {sl}, Capital ₹{cap}.
    Weather: {weather_forecast}.
    Market: Ginger ₹180, Turmeric ₹90.
    Policy: Kuttanad Package offers 40% subsidy for Tubers/Intercropping.
    
    Task: Recommend the best crop between Ginger and Turmeric. 
    Explain 'Why' based on Risk vs Reward.
    Language: Please provide the response in {lang}.
    """
    try:
        # Correct google-genai structural call syntax
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt
        )
        # Verify text payload exists
        if response.text:
            return response.text
        else:
            return "Error: Received an empty response from the AI model."
    except Exception as api_error:
        # Return the exact error string so we can read it on-screen
        return f"SDK/API Call Failed: {str(api_error)}"

# --- DISPLAY ADVISORY ---
st.subheader("📋 Professional Advisory")

# Language Toggle State Logic
if 'language' not in st.session_state:
    st.session_state.language = "English"

# Advisory Box with a loading spinner
with st.spinner("Analyzing real-time market and climate data..."):
    report = get_recommendation(location, soil, capital, st.session_state.language)

# Render the AI report inside a styled card
st.markdown(f"""
<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #2e7d32; color: #1e1e1e;">
    {report}
</div>
""", unsafe_allow_html=True)

# Translation Button Logic
def toggle_language():
    if st.session_state.language == "English":
        st.session_state.language = "Malayalam"
    else:
        st.session_state.language = "English"

st.markdown("---")
btn_label = "Translate to Malayalam" if st.session_state.language == "English" else "English-ലേക്ക് മാറ്റുക"
st.button(btn_label, on_click=toggle_language)

# --- FOOTER ---
st.caption("Agri-Oracle Optimizer v1.0 | Data-driven insights for sustainable farming.")
