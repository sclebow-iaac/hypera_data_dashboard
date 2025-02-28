#IMPORT LIBRARIES
#import streamlit
import streamlit as st
#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import numpy as np
import time

# import dashboards from local files
import dashboards.residential_dashboard as residential_dashboard
import dashboards.service_dashboard as service_dashboard
import dashboards.structure_dashboard as structure_dashboard
import dashboards.industrial_dashboard as industrial_dashboard
import dashboards.facade_dashboard as facade_dashboard
import dashboards.data_dashboard as data_dashboard

# import statistics
import project_statistics as statistics

# import attribute extraction
import attribute_extraction

#PAGE CONFIG AND CUSTOM CSS
#--------------------------
st.set_page_config(
    page_title="Ensō Hyperbuilding | Hyper-A",
    page_icon="🔄",
    layout="wide",  # Makes the dashboard use full screen width
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed for better landing page experience
)

st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap');
    
    /* Main background */
    .stApp {
        font-family: 'Roboto Mono', sans-serif;  /* Apply font family to entire app */
        background-color: white;
    }
    
    /* Main container */
    .main {
        font-family: 'Roboto Mono', sans-serif;
    }
    
    /* Headers */
    .css-10trblm, .css-qrbaxs {
        font-weight: 600;
        font-family: 'Roboto Mono', sans-serif !important;  /* Added !important */
    }
    
    /* All text elements */
    .stMarkdown, .stText, div, span, p, h1, h2, h3 {
        font-family: 'Roboto Mono', sans-serif !important;
    }
    
    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cards and containers */
    div.css-12w0qpk.e1tzin5v2 {
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Buttons and selectbox */
    .stButton>button, .stSelectbox {
        border-radius: 0.3rem;
    }
    
    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F5F5DC;  /* Beige color */
        padding: 1rem;
        border-right: 1px solid #E8E8D0;
    }

    /* Sidebar radio buttons */
    .st-cc, .st-dk, .st-dl, .st-dm {
        font-family: 'Roboto Mono', sans-serif !important;
    }

    /* Sidebar title */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        font-family: 'Roboto Mono', sans-serif !important;
        padding: 0.5rem 0;
    }

    /* Radio button text */
    .st-bq {
        font-family: 'Roboto Mono', sans-serif !important;
    }

    /* Radio button container */
    [data-testid="stSidebar"] .st-bw {
        padding: 0.5rem 0;
    }

    /* Selected radio button */
    [data-testid="stSidebar"] .st-cl {
        background-color: #E8E8D0;  /* Slightly darker beige for selected item */
        border-radius: 0.3rem;
    }

    /* Hover effect on radio buttons */
    [data-testid="stSidebar"] .st-cl:hover {
        background-color: #DFDFC5;
    }
    
    /* Modern navigation menu */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: white;
        border-bottom: 1px solid #f1f1f1;
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
    }
    
    .nav-link {
        text-decoration: none;
        color: #333;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    .nav-link:hover {
        color: #000;
    }
    
    .nav-link.active {
        font-weight: bold;
        border-bottom: 2px solid #333;
    }
    
    /* Hero section */
    .hero-container {
        position: relative;
        height: 80vh;
        overflow: hidden;
    }
    
    .hero-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 2rem;
        color: white;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        max-width: 800px;
        margin-bottom: 2rem;
    }
    
    /* Content sections */
    .section {
        padding: 4rem 2rem;
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .circle-icon {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        background-color: #f1f1f1;
        margin-right: 1rem;
    }
    
    /* Team cards */
    .team-card {
        background-color: white;
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    
    .team-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .team-icon {
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-right: 1rem;
        color: white;
    }
    
    /* Slideshow indicators */
    .slide-indicators {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .indicator {
        width: 0.75rem;
        height: 0.75rem;
        border-radius: 50%;
        background-color: #ddd;
        cursor: pointer;
    }
    
    .indicator.active {
        background-color: #333;
    }
    
    /* Metrics section */
    .metric-card {
        background-color: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Custom progress bar */
    .progress-container {
        width: 100%;
        height: 0.5rem;
        background-color: #f1f1f1;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 1rem;
    }
    
    /* Enso circle */
    .enso-circle {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 300px;
        height: 300px;
        margin: 0 auto;
    }
    
    /* Create smooth overlay for text on images */
    .image-overlay {
        position: relative;
        display: inline-block;
    }
    
    .image-overlay::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7) 100%);
    }
    
    .image-overlay-text {
        position: absolute;
        bottom: 2rem;
        left: 2rem;
        color: white;
        z-index: 1;
    }
    
    /* Custom container with border */
    .bordered-container {
        border: 1px solid #e5e5e5;
        border-radius: 1rem;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Fix for Streamlit components */
    div.element-container {width: 100%;}
    
    /* Full bleed section */
    .full-bleed {
        width: 100vw;
        margin-left: calc(50% - 50vw);
    }
    
    /* For the circular team visualization */
    .circle-container {
        position: relative;
        width: 600px;
        height: 600px;
        margin: 0 auto;
    }
    
    .center-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background-color: #f5f5f5;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 2px solid #333;
        z-index: 10;
    }
    
    .team-circle {
        position: absolute;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        cursor: pointer;
        transition: transform 0.3s ease;
        z-index: 5;
    }
    
    .team-circle:hover {
        transform: scale(1.1);
    }
    
    /* Make 3D model viewer responsive */
    iframe {
        width: 100%;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for selecting dashboards
dashboard_options = ["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data"]
selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)

# Create a placeholder for the dashboard content
dashboard_placeholder = st.empty()

# Function to display the residential dashboard
def display_residential_dashboard():
    with dashboard_placeholder.container():
        selected_team = "Residential Team"  # Set the selected team or get it from user input
        residential_dashboard.run(selected_team)  # Call the function from the residential dashboard

# Function to display the service dashboard
def display_service_dashboard():
    with dashboard_placeholder.container():
        selected_team = "Service Team"  # Set the selected team
        service_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the structure dashboard
def display_structure_dashboard():
    with dashboard_placeholder.container():
        selected_team = "Structure Team"  # Set the selected team
        structure_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the industrial dashboard
def display_industrial_dashboard():
    with dashboard_placeholder.container():
        selected_team = "Industrial Team"  # Set the selected team
        industrial_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the facade dashboard
def display_facade_dashboard():
    with dashboard_placeholder.container():
        selected_team = "Facade Team"  # Set the selected team
        facade_dashboard.run(selected_team)  # Only pass selected_team

# Hero section gallery slides
hero_slides = [
    {
        "title": "Ensō Hyperbuilding",
        "subtitle": "The Complete Circle of Life - A building that embodies completeness through continuous cycles and perfect imperfection",
        "image": "assets/enso_main.jpg"
    },
    {
        "title": "Absolute Enlightenment",
        "subtitle": "The Ensō Hyperbuilding embodies the Zen concept of complete awareness, creating spaces that inspire clarity and purpose.",
        "image": "assets/enso_concept1.jpg"
    },
    {
        "title": "Strength in Imperfection",
        "subtitle": "By embracing the beauty of imperfection, our design celebrates the natural variations that make spaces authentically human",
        "image": "assets/enso_concept2.jpg"
    },
    {
        "title": "Cyclical Nature of Existence",
        "subtitle": "Our building systems operate in sustainable cycles, mirroring the continuous renewal found in natural ecosystems",
        "image": "assets/enso_concept3.jpg"
    },
    {
        "title": "Unity of Opposites",
        "subtitle": "The Hyperbuilding balances contrasting elements—technology and nature, community and privacy, structure and flexibility—creating harmony through complementary forces",
        "image": "assets/enso_concept4.jpg"
    }
]

# Team vision slides
team_slides = [
    {
        "team": "Service",
        "description": "Distinct intertwined neighborhoods create a dynamic social network fostering connections and interactions. The principle of space exchange enables spaces to transform seamlessly unlocking layers of openness within the building.",
        "color": "#3B82F6",
        "image": "assets/service.png"
    },
    {
        "team": "Structural",
        "description": "Forces flow from the top to the floor through dynamic and variated elements, determined by the flow of circulation between functions of the building creating open and flexible spaces, with ever-different spatial qualities",
        "color": "#F43F5E",
        "image": "assets/structure.png"
    },
    {
        "team": "Residential",
        "description": "Creating a vibrant and integrated vertical living experience that fosters community connection, sustainability, and accessibility by designing mixed-use spaces, balancing XL and XS residential offerings, providing diverse and adaptable living options",
        "color": "#10B981",
        "image": "assets/residential.png"
    },
    {
        "team": "Industrial",
        "description": "A building that breathes life into the city, a vibrant ecosystem that produces its own clean energy, transforms waste into resources, and nurtures fresh food right where you live.",
        "color": "#F97316",
        "image": "assets/industrial.png"
    },
    {
        "team": "Facade",
        "description": "Modular and data-driven, it adjusts in real-time for optimal light, thermal performance, and occupant comfort, creating a sustainable, intelligent architectural systems.",
        "color": "#8B5CF6",
        "image": "assets/facade.png"
    }
]

# Team details for the implementation section
team_details = {
    "Service": {
        "color": "#3B82F6",
        "aspects": [
            "Human-scale design approach in expansive spaces",
            "Dynamic social network creation between neighborhoods",
            "Flexible space exchange systems",
            "Fluid and engaging circulation experiences",
            "Proximity-based function organization",
            "Balance between energy-demanding and energy-producing systems"
        ],
        "image": "assets/service_detail.png"
    },
    "Structure": {
        "color": "#F43F5E",
        "aspects": [
            "Integration of three primary flows (forces, people, water)",
            "Dynamic and varied structural elements",
            "Flexible space creation",
            "Water management through mass damping",
            "Flow-based spatial organization",
            "Adaptive spatial qualities"
        ],
        "image": "assets/structure_detail.png"
    },
    "Residential": {
        "color": "#10B981",
        "aspects": [
            "Connection to public spaces",
            "Efficiency in Unit Clustering",
            "Efficiency in Unit Layout",
            "5-minute commuting distance",
            "Multi-generational living considerations"
        ],
        "image": "assets/residential_detail.png"
    },
    "Industrial": {
        "color": "#F97316",
        "aspects": [
            "Clean energy production and management",
            "Waste-to-resource transformation systems",
            "On-site food production integration",
            "Prosumer energy sharing framework",
            "Zero-waste implementation strategies",
            "Nature-based solutions (NBS) integration",
            "Regenerative system development"
        ],
        "image": "assets/industrial_detail.png"
    },
    "Facade": {
        "color": "#8B5CF6",
        "aspects": [
            "Adaptive origami-inspired design systems",
            "Integration of wood and glass materials",
            "Real-time environmental response capabilities",
            "Smart shading and view optimization",
            "Data-driven comfort management",
            "Modular design approach"
        ],
        "image": "assets/facade_detail.png"
    }
}

# Team metrics for KPI section
team_metrics = {
    "Service": {
        "primary": {"name": "Connectivity Metric", "value": 0.72},
        "secondary": []
    },
    "Structure": {
        "primary": {"name": "Column-Free Floor Area Ratio", "value": 0.98},
        "secondary": []
    },
    "Residential": {
        "primary": {"name": "Maximum Travel Time", "value": 0.85},
        "secondary": []
    },
    "Industrial": {
        "primary": {"name": "Energy Self-Sufficiency Ratio", "value": 0.75},
        "secondary": [
            {"name": "Food Self-Sufficiency Ratio", "value": 0.60},
            {"name": "Water Recycling Ratio", "value": 0.80},
            {"name": "Waste Utilization Ratio", "value": 0.40}
        ]
    },
    "Facade": {
        "primary": {"name": "Primary Daylight Factor", "value": 0.85},
        "secondary": [
            {"name": "Panel Optimization", "value": 0.50},
            {"name": "Energy Generation Ratio", "value": 1.25}
        ]
    }
}

# Overall performance metrics
overall_metrics = {
    "Service": 76,
    "Structure": 89,
    "Residential": 95,
    "Industrial": 100,
    "Facade": 83
}

# Define a function to create the hero slideshow
def hero_slideshow():
    # Initialize slide index in session state if not exists
    if 'hero_slide_idx' not in st.session_state:
        st.session_state.hero_slide_idx = 0
    
    # Create container for the slideshow
    hero_container = st.container()
    
    with hero_container:
        # Try to display image, fall back to placeholder if not found
        try:
            # Create columns for navigation
            prev_col, img_col, next_col = st.columns([1, 10, 1])
            
            # Navigation buttons
            with prev_col:
                if st.button("←", key="prev_hero"):
                    st.session_state.hero_slide_idx = (st.session_state.hero_slide_idx - 1) % len(hero_slides)
                    st.experimental_rerun()
            
            with next_col:
                if st.button("→", key="next_hero"):
                    st.session_state.hero_slide_idx = (st.session_state.hero_slide_idx + 1) % len(hero_slides)
                    st.experimental_rerun()
            
            # Current slide
            with img_col:
                current_slide = hero_slides[st.session_state.hero_slide_idx]
                try:
                    st.image(current_slide["image"], use_column_width=True)
                except FileNotFoundError:
                    st.warning(f"Please add the image {current_slide['image']} to your assets folder")
                    # Display a placeholder instead
                    st.markdown(f"""
                    <div style="background-color: #f5f5f5; height: 400px; display: flex; justify-content: center; align-items: center; border-radius: 10px;">
                        <div style="text-align: center;">
                            <h2>{current_slide["title"]}</h2>
                            <p>{current_slide["subtitle"]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add caption
                st.markdown(f"""
                <div style="text-align: center; margin-top: -100px; position: relative; z-index: 10;">
                    <h1 style="color: white; text-shadow: 2px 2px 4px #000000;">{current_slide["title"]}</h1>
                    <p style="color: white; text-shadow: 1px 1px 2px #000000; max-width: 800px; margin: 0 auto;">
                        {current_slide["subtitle"]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error displaying slideshow: {e}")
            # Fallback content
            st.markdown("""
            <div style="background-color: #f5f5f5; height: 400px; display: flex; justify-content: center; align-items: center; border-radius: 10px;">
                <div style="text-align: center;">
                    <h2>Ensō Hyperbuilding</h2>
                    <p>The Complete Circle of Life - A building that embodies completeness through continuous cycles and perfect imperfection</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Slide indicators
    st.markdown("""
    <div class="slide-indicators">
    """ + "".join([f"""
        <div class="indicator{'active' if i == st.session_state.hero_slide_idx else ''}" 
             onclick="document.querySelector('[data-testid=\\"stExpander\\"]').click()"
             style="cursor: pointer;">
        </div>
    """ for i in range(len(hero_slides))]) + """
    </div>
    """, unsafe_allow_html=True)

# Define a function to create team vision slideshow
def team_vision_slideshow():
    # Initialize slide index in session state if not exists
    if 'team_slide_idx' not in st.session_state:
        st.session_state.team_slide_idx = 0
    
    # Create container for the slideshow
    team_container = st.container()
    
    with team_container:
        st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Our Unified Vision</h2>", unsafe_allow_html=True)
        
        # Create columns for navigation
        prev_col, img_col, next_col = st.columns([1, 10, 1])
        
        # Navigation buttons
        with prev_col:
            if st.button("←", key="prev_team"):
                st.session_state.team_slide_idx = (st.session_state.team_slide_idx - 1) % len(team_slides)
                st.experimental_rerun()
        
        with next_col:
            if st.button("→", key="next_team"):
                st.session_state.team_slide_idx = (st.session_state.team_slide_idx + 1) % len(team_slides)
                st.experimental_rerun()
        
        # Current slide
        with img_col:
            current_slide = team_slides[st.session_state.team_slide_idx]
            
            # Try to display image
            try:
                st.image(current_slide["image"], use_column_width=True)
            except FileNotFoundError:
                st.warning(f"Please add the image {current_slide['image']} to your assets folder")
                # Display a placeholder instead
                st.markdown(f"""
                <div style="background-color: #f5f5f5; height: 300px; display: flex; justify-content: center; align-items: center; border-radius: 10px;">
                    <div style="text-align: center;">
                        <h3 style="color: {current_slide["color"]};">{current_slide["team"]} Team</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add caption
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <h3 style="color: {current_slide["color"]};">{current_slide["team"]} Team</h3>
                <p>{current_slide["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Slide indicators
    st.markdown("""
    <div class="slide-indicators">
    """ + "".join([f"""
        <div class="indicator{'active' if i == st.session_state.team_slide_idx else ''}" 
             onclick="document.querySelector('[data-testid=\\"stExpander\\"]').click()"
             style="background-color: {team_slides[i]['color'] if i == st.session_state.team_slide_idx else '#ddd'}; cursor: pointer;">
        </div>
    """ for i in range(len(team_slides))]) + """
    </div>
    """, unsafe_allow_html=True)

# Define a function to create the essence of Enso section
def essence_of_enso():
    st.markdown("<h2 style='text-align: center; margin-top: 3rem; margin-bottom: 2rem;'>The Essence of Ensō</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <p>
        Ensō, the Zen circle, represents one of the most fundamental principles in Japanese aesthetics and philosophy. 
        Traditionally drawn in a single, fluid brush stroke, it symbolizes absolute enlightenment, strength in imperfection, 
        and the cyclical nature of existence.
        </p>
        <p style="margin-top: 1rem; margin-bottom: 2rem;">
        In our Hyperbuilding design, we've embraced these principles through:
        </p>
        """, unsafe_allow_html=True)
        
        # Principles with circle icons
        principles = [
            {
                "number": "1",
                "title": "Completion Through Incompletion",
                "description": "Design that allows for growth and adaptation, with spaces that evolve with user needs and systems that improve through iteration."
            },
            {
                "number": "2",
                "title": "Moment of Creation",
                "description": "Integration of spontaneous and planned elements, balancing control and natural development, and creating harmony between designed and emergent patterns."
            },
            {
                "number": "3",
                "title": "Unity of Opposites",
                "description": "Integration of traditional and modern elements, balance between public and private spaces, and harmony between technology and nature."
            }
        ]
        
        for principle in principles:
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 1.5rem;">
                <div style="width: 3rem; height: 3rem; border-radius: 50%; background-color: #f5f5f5; display: flex; justify-content: center; align-items: center; margin-right: 1rem; flex-shrink: 0; border: 1px solid #ddd;">
                    <span style="font-weight: bold;">{principle["number"]}</span>
                </div>
                <div>
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem;">{principle["title"]}</h3>
                    <p style="margin: 0;">{principle["description"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        try:
            st.image("assets/enso_circle.jpg", width=350)
        except FileNotFoundError:
            # Display SVG circle as fallback
            st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; height: 350px;">
                <svg width="300" height="300" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="none" />
                    <path d="M 50,10 A 40,40 0 1 1 10,50 A 40,40 0 0 1 90,50" fill="none" stroke="black" stroke-width="4" />
                </svg>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <p style="font-style: italic;">"When the mind is free to let the body create."</p>
            <p style="font-size: 0.9rem; color: #666;">— Zen philosophy on the creation of Ensō</p>
        </div>
        """, unsafe_allow_html=True)

# Function to create team implementation section
def team_implementation():
    st.markdown("<h2 style='text-align: center; margin-top: 4rem; margin-bottom: 2rem;'>Implementation Strategies</h2>", unsafe_allow_html=True)
    
    # Create tabs for teams (excluding Data team)
    teams = ["Service", "Structure", "Residential", "Industrial", "Facade"]
    cols = st.columns(len(teams))
    
    # Display each team in columns
    for i, team in enumerate(teams):
        with cols[i]:
            details = team_details[team]
            
            st.markdown(f"""
            <div style="text-align: center;">
                <h3 style="color: {details['color']};">{team}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Try to display team image
            try:
                st.image(details["image"], use_column_width=True)
            except FileNotFoundError:
                # Fallback placeholder with team color
                st.markdown(f"""
                <div style="background-color: {details['color']}20; height: 200px; display: flex; justify-content: center; align-items: center; border-radius: 10px; margin-bottom: 1rem;">
                    <h4 style="color: {details['color']};">{team} Team</h4>
                </div>
                """, unsafe_allow_html=True)
            
            # Display key aspects
            for aspect in details["aspects"][:3]:  # Show only first 3 aspects
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="width: 0.5rem; height: 0.5rem; border-radius: 50%; background-color: {details['color']}; margin-top: 0.5rem; margin-right: 0.5rem;"></div>
                    <div>{aspect}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add link to team dashboard
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child({dashboard_options.index(team)+1})').click(); return false;" 
                   style="color: {details['color']}; text-decoration: none; font-weight: 500;">
                    View Team Dashboard
                </a>
            </div>
            """, unsafe_allow_html=True)

# Function to create KPI section
def kpi_section():
    st.markdown("<h2 style='text-align: center; margin-top: 4rem; margin-bottom: 2rem;'>KPI's Definitions & Performance</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>A brief definition of what each team's KPI's definitions entails and where they stand currently</p>", unsafe_allow_html=True)
    
    # Create columns for metrics
    teams = ["Service", "Structure", "Residential", "Industrial", "Facade"]
    cols = st.columns(len(teams))
    
    # Display metrics for each team
    for i, team in enumerate(teams):
        with cols[i]:
            metrics = team_metrics[team]
            color = team_details[team]["color"]
            
            # Primary metric
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <h4>{team} KPI</h4>
                <p style="font-size: 0.9rem;">{metrics['primary']['name']}</p>
                <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0; color: {color};">
                    {metrics['primary']['value']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Secondary metrics if any
            for secondary in metrics.get('secondary', []):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.9rem;">{secondary['name']}</span>
                    <span style="font-weight: bold;">{secondary['value']}</span>
                </div>
                """, unsafe_allow_html=True)

# Function to display the Speckle 3D model
def display_speckle_model(client, project, selected_model, selected_version):
    st.markdown("<h2 style='text-align: center; margin-top: 4rem; margin-bottom: 2rem;'>Unified Speckle Model</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>Here we can place an Interactive UI of the model, loading with all disciplines activated at once and then make it more interactive through a navigation menu below</p>", unsafe_allow_html=True)
    
    # Create the iframe to display the model
    embed_src = f"https://macad.speckle.xyz/projects/{project.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    components = st.components.v1.iframe(src=embed_src, height=600)

# Function to display performance metrics
def performance_metrics():
    st.markdown("<h2 style='text-align: center; margin-top: 4rem; margin-bottom: 2rem;'>Overall Performance</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>Here we place the graphs describing how each team is performing individually</p>", unsafe_allow_html=True)
    
    # Create columns for the circular progress bars
    teams = ["Service", "Structure", "Residential", "Industrial", "Facade"]
    cols = st.columns(len(teams))
    
    # Display circular progress for each team
    for i, team in enumerate(teams):
        with cols[i]:
            value = overall_metrics[team]
            color = team_details[team]["color"]
            
            # Create circular progress bar with HTML/CSS
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="position: relative; width: 120px; height: 120px; margin: 0 auto;">
                    <svg width="120" height="120" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="54" fill="none" stroke="#e6e6e6" stroke-width="12" />
                        <circle cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="12" 
                                stroke-dasharray="339.292" stroke-dashoffset="{339.292 * (1 - value/100)}" 
                                transform="rotate(-90 60 60)" />
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.5rem; font-weight: bold;">
                        {value}%
                    </div>
                </div>
                <h4 style="margin-top: 1rem;">{team}</h4>
                <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child({dashboard_options.index(team)+1})').click(); return false;" 
                   style="color: {color}; text-decoration: none; font-size: 0.9rem;">
                    Detailed View
                </a>
            </div>
            """, unsafe_allow_html=True)

# Function to display the main navigation menu
def display_main_nav():
    st.markdown("""
    <div style="display: flex; justify-content: space-between; padding: 1rem 2rem; border-bottom: 1px solid #eee; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center;">
            <div style="width: 2.5rem; height: 2.5rem; border-radius: 50%; background-color: #000; color: white; display: flex; justify-content: center; align-items: center; margin-right: 1rem;">
                <span style="font-weight: bold;">円</span>
            </div>
            <h2 style="margin: 0;">Ensō Hyperbuilding (円相)</h2>
        </div>
        <div style="display: flex; gap: 2rem;">
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(1)').click(); return false;" style="text-decoration: none; color: #333; font-weight: bold;">Vision</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(7)').click(); return false;" style="text-decoration: none; color: #333;">Metrics</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(2)').click(); return false;" style="text-decoration: none; color: #333;">Service</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(3)').click(); return false;" style="text-decoration: none; color: #333;">Structure</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(4)').click(); return false;" style="text-decoration: none; color: #333;">Residential</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(5)').click(); return false;" style="text-decoration: none; color: #333;">Industrial</a>
            <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child(6)').click(); return false;" style="text-decoration: none; color: #333;">Facade</a>
            <a href="#" style="text-decoration: none; color: #333;">Gallery</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Function to create the circular team diagram
def circular_team_diagram():
    st.markdown("<h2 style='text-align: center; margin-top: 4rem; margin-bottom: 2rem;'>Our Unified Vision</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>The Ensō Hyperbuilding is brought to life through six specialized teams, each contributing to our circular philosophy of completeness through continuous cycles.</p>", unsafe_allow_html=True)
    
    # Initialize active team in session state if not exists
    if 'active_team' not in st.session_state:
        st.session_state.active_team = None
    
    # Create columns for diagram and details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create the circular diagram with HTML/CSS and JavaScript
        st.markdown("""
        <div class="circle-container">
            <div class="center-circle">
                <div style="text-align: center;">
                    <h3>Ensō</h3>
                    <p style="font-size: 0.9rem;">Complete Circle of Life</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Position teams in a circle around the center
        teams_with_positions = [
            {"team": "Service", "color": "#3B82F6", "icon": "👥", "x": 30, "y": 20},
            {"team": "Structure", "color": "#F43F5E", "icon": "🏗️", "x": 70, "y": 30},
            {"team": "Residential", "color": "#10B981", "icon": "🏠", "x": 80, "y": 70},
            {"team": "Industrial", "color": "#F97316", "icon": "⚙️", "x": 55, "y": 85},
            {"team": "Facade", "color": "#8B5CF6", "icon": "🪟", "x": 20, "y": 75},
            {"team": "Data", "color": "#6366F1", "icon": "📊", "x": 15, "y": 45}
        ]
        
        for t in teams_with_positions:
            st.markdown(f"""
            <div class="team-circle" style="top: {t['y']}%; left: {t['x']}%; background-color: {t['color']};"
                 onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child({dashboard_options.index(t['team'])+1 if t['team'] in dashboard_options else 1})').click();">
                {t['icon']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # If a team is active, show details
        if st.session_state.active_team:
            team = st.session_state.active_team
            details = team_details.get(team, {})
            st.markdown(f"""
            <div>
                <h3 style="color: {details.get('color', '#333')};">{team} Team</h3>
                <p>Description will go here...</p>
                <a href="#" onclick="document.querySelector('div[data-baseweb=\\"radio\\"] label:nth-child({dashboard_options.index(team)+1 if team in dashboard_options else 1})').click(); return false;"
                   style="color: {details.get('color', '#333')}; text-decoration: none;">
                    View Team Dashboard
                </a>
            </div>
            """, unsafe_allow_html=True)

# Only show main interface if "Main" is selected
if selected_dashboard == "Main":
    # Display main navigation menu
    display_main_nav()
    
    # Create main container for full-width content
    main_container = st.container()
    
    with main_container:
        # Hero slideshow
        hero_slideshow()
        
        # Essence of Enso section
        essence_of_enso()
        
        # Circular team diagram
        circular_team_diagram()
        
        # Team vision slideshow
        team_vision_slideshow()
        
        # Team implementation section
        team_implementation()
        
        # KPI section
        kpi_section()
        
        # Speckle integration
        speckleServer = "macad.speckle.xyz"
        speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
        
        # CLIENT
        client = SpeckleClient(host=speckleServer)
        # Get account from Token
        account = get_account_from_token(speckleToken, speckleServer)
        # Authenticate
        client.authenticate_with_account(account)
        
        # Get the team project
        project_id = '31f8cca4e0'
        selected_project = client.project.get(project_id=project_id)
        
        # Get the project with models
        project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
        
        # Get the models
        models = project.models.items
        
        # Use the first model by default or let user select
        with st.expander("Select Speckle Model (Click to expand)", expanded=False):
            # Add model selection
            selected_model_name = st.selectbox(
                label="Select model to analyze",
                options=[m.name for m in models],
                help="Select a specific model to analyze its data"
            )
            
            # Get the selected model object
            selected_model = [m for m in models if m.name == selected_model_name][0]
            
            # Get the versions for the selected model
            versions = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=100).items
            
            def versionName(version):
                timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
                return ' - '.join([version.authorUser.name, timestamp, version.message])
            
            keys = [versionName(version) for version in versions]
            
            # Add version selection
            selected_version_key = st.selectbox(
                label="Select version to analyze",
                options=keys,
                help="Select a specific version to analyze"
            )
            
            selected_version = versions[keys.index(selected_version_key)]
        
        # Display 3D model
        display_speckle_model(client, project, selected_model, selected_version)
        
        # Performance metrics
        performance_metrics()
        
        # Add attribute extraction for debugging (kept from original code)
        with st.expander("Advanced: Attribute Extraction", expanded=False):
            attribute_extraction.run(selected_version, client, project)

else:
    # Display only the selected dashboard
    if selected_dashboard == "Residential":
        display_residential_dashboard()
    elif selected_dashboard == "Service":
        display_service_dashboard()
    elif selected_dashboard == "Structure":
        display_structure_dashboard()
    elif selected_dashboard == "Industrial":
        display_industrial_dashboard()
    elif selected_dashboard == "Facade":
        display_facade_dashboard()
    elif selected_dashboard == "Data":
        data_dashboard.run()