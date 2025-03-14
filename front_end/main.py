#IMPORT LIBRARIES
#import streamlit
import streamlit as st
#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import numpy as np
from dashboards.dashboard import *

# import dashboards from local files
import dashboards.residential_dashboard as residential_dashboard
import dashboards.service_dashboard as service_dashboard
import dashboards.structure_dashboard as structure_dashboard
import dashboards.industrial_dashboard as industrial_dashboard
import dashboards.facade_dashboard as facade_dashboard
import dashboards.data_dashboard as data_dashboard
import dashboards.slack_config as slack_config

# import statistics
import project_statistics as statistics

# import attribute extraction
import attribute_extraction

def display_federated_speckle_viewer(container, project_id, height):
    # Function to create a federated Speckle viewer
    # with multiple models
    
    model_ids = [] # List to store model IDs
    
    # Get the team dashboards
    team_dashboards = [
        residential_dashboard,
        service_dashboard,
        structure_dashboard,
        industrial_dashboard,
        facade_dashboard,
    ]
    
    # Loop through each dashboard and get the model IDs
    for dashboard in team_dashboards:
        # Get the model IDs from the dashboard
        model_id = dashboard.presentation_model_id
        # Check if the model ID is not None
        if model_id is not None:
            model_ids.append(model_id)
    
    # Join the model IDs into a single string
    federated_model_id = ','.join(model_ids)
    
    container.write(
        f'<iframe src="https://speckle.xyz/embed?stream={project_id}&commit={federated_model_id}" width="100%" height="{height}" frameborder="0"></iframe>',
        unsafe_allow_html=True
    )

# Set page configuration
st.set_page_config(
    page_title="Ensō Hyperbuilding (円相)",
    page_icon="front_end/assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #ffffff;
    }
    
    /* Navigation styling */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    .nav-logo {
        display: flex;
        align-items: center;
    }
    
    .nav-logo img {
        height: 40px;
        margin-right: 10px;
    }
    
    .nav-links {
        display: flex;
    }
    
    .nav-link {
        margin: 0 15px;
        color: #333;
        text-decoration: none;
        font-weight: 500;
    }
    
    .nav-link:hover {
        color: #000;
        border-bottom: 2px solid #000;
    }
    
    /* Slideshow styling */
    .slideshow-container {
        position: relative;
        margin-bottom: 2rem;
    }
    
    .slide-dots {
        text-align: center;
        margin-top: 10px;
    }
    
    .slide-dot {
        display: inline-block;
        height: 10px;
        width: 10px;
        margin: 0 5px;
        background-color: #bbb;
        border-radius: 50%;
        cursor: pointer;
    }
    
    .slide-dot.active {
        background-color: #333;
    }
    
    /* Section styling */
    .section-container {
        margin: 3rem 0;
        padding: 1rem;
    }
    
    .section-title {
        text-align: center;
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .enso-bullet {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1.5rem;
    }
    
    .enso-bullet img {
        width: 50px;
        margin-right: 15px;
    }
    
    /* Discipline sections */
    .discipline-section {
        display: flex;
        align-items: center;
        margin: 3rem 0;
        gap: 2rem;
    }
    
    /* KPI section */
    .kpi-nav {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .kpi-link {
        margin: 0 15px;
        padding: 5px 10px;
        cursor: pointer;
        color: #999;
    }
    
    .kpi-link.active {
        color: #000;
        font-weight: bold;
    }
    
    .kpi-metrics {
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
    }
    
    .kpi-metric {
        text-align: center;
        width: 18%;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    
    /* Performance section */
    .performance-container {
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
    }
    
    .performance-item {
        text-align: center;
        width: 18%;
    }
    
    .performance-circle {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }
    
    .performance-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Create a simpler navigation styling with more compact buttons
st.markdown("""
<style>
    .stButton button {
        padding: 2px 5px;
        font-size: 0.8rem;
        font-weight: normal;
        height: auto;
        min-width: 0;
        width: auto;
        margin: 0 2px;
    }
    .compact-header h3 {
        margin: 0;
        padding: 0;
        white-space: nowrap;
        font-size: 1.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Create a 2-column layout for the navigation bar with more space for the title
logo_col, menu_col = st.columns([1, 2])

# Logo and title in the left column
with logo_col:
    cols = st.columns([1, 3])
    with cols[0]:
        try:
            st.image("front_end/assets/logo.jpg", width=50)
        except Exception as e:
            st.markdown("🔄") # Fallback to an emoji if image fails
    with cols[1]:
        st.markdown("<div class='compact-header'><h3>Ensō Hyperbuilding (円相)</h3></div>", unsafe_allow_html=True)

# Navigation buttons in the right column using a container for better alignment
with menu_col:
    # Use a single row with HTML for more compact buttons
    menu_items = ["Vision", "Metrics", "Service", "Structure", "Residential", "Industrial", "Facade", "Slack"]
    page_routes = {
        "Vision": "main",
        "Metrics": "data_dashboard", 
        "Service": "service_dashboard",
        "Structure": "structure_dashboard",
        "Residential": "residential_dashboard",
        "Industrial": "industrial_dashboard",
        "Facade": "facade_dashboard",
        "Slack": "slack_config"
    }
    
    # Create a container with flex display for the buttons
    container = st.container()
    
    # Create a more compact horizontal layout for buttons
    num_cols = 8  # Fixed number of columns, more compact
    button_cols = container.columns(num_cols)
    
    # Add buttons with minimal spacing
    for i, menu_item in enumerate(menu_items):
        with button_cols[i]:
            current_page = page_routes[menu_item] == (st.query_params.get("page", ["main"])[0] if isinstance(st.query_params.get("page", ["main"]), list) else st.query_params.get("page", "main"))
            button_style = "primary" if current_page else "secondary"
            
            if st.button(menu_item, key=f"nav_{menu_item}", type=button_style, use_container_width=False):
                st.query_params["page"] = page_routes[menu_item]
                
                # Use JavaScript for navigation
                st.markdown(f"""
                <script>
                    window.location.href = "/?page={page_routes[menu_item]}";
                </script>
                """, unsafe_allow_html=True)

# Get query parameters
query_params = st.query_params  # Fix: Removed parentheses
page = query_params["page"] if "page" in query_params else "main"

# Display the selected page
if page == "main":
    # First Slideshow section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    
    # Content for each slide
    slide_content = [
        {
            "image": "front_end/assets/Enso/enso01.png",
            "title": "Ensō Hyperbuilding",
            "text": "The Complete Circle of Life - A building that embodies completeness through continuous cycles and perfect imperfection"
        },
        {
            "image": "front_end/assets/Enso/enso02.png",
            "title": "Absolute Enlightenment",
            "text": "The Ensō Hyperbuilding embodies the Zen concept of complete awareness, creating spaces that inspire clarity and purpose"
        },
        {
            "image": "front_end/assets/Enso/enso03.png",
            "title": "Strength in Imperfection",
            "text": "By embracing the beauty of imperfection, our design celebrates the natural variations that make spaces authentically human"
        },
        {
            "image": "front_end/assets/Enso/enso04.png",
            "title": "Cyclical Nature of Existence",
            "text": "Our building systems operate in sustainable cycles, mirroring the continuous renewal found in natural ecosystems"
        },
        {
            "image": "front_end/assets/Enso/enso05.png",
            "title": "Unity of Opposites",
            "text": "The Hyperbuilding balances contrasting elements—technology and nature, community and privacy, structure and flexibility—creating harmony through complementary forces"
        }
    ]
    
    # Initialize session state for the slideshow
    if 'slide_index' not in st.session_state:
        st.session_state.slide_index = 0
    
    # Create a container for the slideshow
    slide_container = st.container()
    
    # Display the current slide
    with slide_container:
        current_slide = slide_content[st.session_state.slide_index]
        st.image(current_slide["image"], use_container_width=True)
        st.markdown(f"<h2 style='text-align: center;'>{current_slide['title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{current_slide['text']}</p>", unsafe_allow_html=True)
    
    # Create navigation buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("←", key="prev_slide"):
            st.session_state.slide_index = (st.session_state.slide_index - 1) % len(slide_content)
            st.experimental_rerun()
    
    with col3:
        if st.button("→", key="next_slide"):
            st.session_state.slide_index = (st.session_state.slide_index + 1) % len(slide_content)
            st.experimental_rerun()
    
    # Display slide indicators
    slide_indicators = "".join([
        f"<span style='display: inline-block; height: 10px; width: 10px; margin: 0 5px; border-radius: 50%; background-color: {'#333' if i == st.session_state.slide_index else '#bbb'};'></span>"
        for i in range(len(slide_content))
    ])
    
    with col2:
        st.markdown(f"<div style='text-align: center;'>{slide_indicators}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # The Essence of Ensō section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'>The Essence of Ensō</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <p>Ensō, the Zen circle, represents one of the most fundamental principles in Japanese aesthetics and philosophy. 
    Traditionally drawn in a single, fluid brush stroke, it symbolizes absolute enlightenment, strength in imperfection, 
    and the cyclical nature of existence.</p>
    
    <p>Ensō Hyperbuilding embraces these principles through:</p>
    """, unsafe_allow_html=True)
    
    # Create columns for the bullet points with Enso images
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="enso-bullet">
            <img src="front_end/assets/logo.jpg" alt="Enso 1">
            <div>
                <h3>Completion Through Incompletion</h3>
                <p>A design that allows for growth and adaptation, with spaces that evolve with user needs and systems that improve through iteration.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="enso-bullet">
            <img src="front_end/assets/logo.jpg" alt="Enso 2">
            <div>
                <h3>Moment of Creation</h3>
                <p>Integration of spontaneous and planned elements, balancing control and natural development, and creating harmony between designed and emergent patterns.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="enso-bullet">
            <img src="front_end/assets/logo.jpg" alt="Enso 3">
            <div>
                <h3>Unity of Opposites</h3>
                <p>Juxtaposition of traditional and modern elements, balance between public and private spaces, and harmony between technology and nature.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Our Unified Vision section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    try:
        st.image("front_end/assets/vision.png", use_container_width=True)
    except Exception as e:
        st.error(f"Unable to load vision image: {e}")
        
    st.markdown("""
    <h2 class="section-title">Our Unified Vision</h2>
    <p style="text-align: center; margin-bottom: 3rem;">
        The Ensō Hyperbuilding is brought to life through six specialized teams, each contributing to our circular philosophy of completeness through continuous cycles.
    </p>
    """, unsafe_allow_html=True)
    
    # Service section - left image, right text
    st.markdown("""
    <div class="discipline-section" style="display: flex; align-items: center; margin: 3rem 0; gap: 2rem;">
        <div style="flex: 1; text-align: center;">
            <img src="front_end/assets/Service/01/serviceLR.gif" style="width: 100%; max-width: 400px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Service+Image'; this.style.opacity=0.7;">
        </div>
        <div style="flex: 1;">
            <h2 style="margin-bottom: 1rem;">Service</h2>
            <ul style="padding-left: 1.5rem;">
                <li>Human-scale design approach in expansive spaces</li>
                <li>Dynamic social network creation between neighborhoods</li>
                <li>Flexible space exchange systems</li>
                <li>Fluid and engaging circulation experiences</li>
                <li>Proximity-based function organization</li>
                <li>Balance between energy-demanding and energy-producing systems</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Structure section - right image, left text
    st.markdown("""
    <div class="discipline-section" style="display: flex; align-items: center; margin: 3rem 0; gap: 2rem;">
        <div style="flex: 1;">
            <h2 style="margin-bottom: 1rem;">Structure</h2>
            <ul style="padding-left: 1.5rem;">
                <li>Integration of three primary flows (forces, people, water)</li>
                <li>Dynamic and varied structural elements</li>
                <li>Flexible space creation</li>
                <li>Water management through mass damping</li>
                <li>Flow-based spatial organization</li>
                <li>Adaptive spatial qualities</li>
            </ul>
        </div>
        <div style="flex: 1; text-align: center;">
            <img src="front_end/assets/Structure/01/structureLR.gif" style="width: 100%; max-width: 400px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Structure+Image'; this.style.opacity=0.7;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Residential section - left image, right text
    st.markdown("""
    <div class="discipline-section" style="display: flex; align-items: center; margin: 3rem 0; gap: 2rem;">
        <div style="flex: 1; text-align: center;">
            <img src="front_end/assets/Residential/01/residentialLR.gif" style="width: 100%; max-width: 400px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Residential+Image'; this.style.opacity=0.7;">
        </div>
        <div style="flex: 1;">
            <h2 style="margin-bottom: 1rem;">Residential</h2>
            <ul style="padding-left: 1.5rem;">
                <li>Connection to public spaces</li>
                <li>Efficiency in Unit Clustering</li>
                <li>Efficiency in Unit Layout</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Industrial section - right image, left text
    st.markdown("""
    <div class="discipline-section" style="display: flex; align-items: center; margin: 3rem 0; gap: 2rem;">
        <div style="flex: 1;">
            <h2 style="margin-bottom: 1rem;">Industrial</h2>
            <ul style="padding-left: 1.5rem;">
                <li>Clean energy production and management</li>
                <li>Waste-to-resource transformation systems</li>
                <li>On-site food production integration</li>
                <li>Prosumer energy sharing framework</li>
                <li>Zero-waste implementation strategies</li>
                <li>Nature-based solutions (NBS) integration</li>
                <li>Regenerative system development</li>
            </ul>
        </div>
        <div style="flex: 1; text-align: center;">
            <img src="front_end/assets/Industrial/01/industrialLR.gif" style="width: 100%; max-width: 400px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Industrial+Image'; this.style.opacity=0.7;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Facade section - left image, right text
    st.markdown("""
    <div class="discipline-section" style="display: flex; align-items: center; margin: 3rem 0; gap: 2rem;">
        <div style="flex: 1; text-align: center;">
            <img src="front_end/assets/Facade/01/facadeLR.gif" style="width: 100%; max-width: 400px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Facade+Image'; this.style.opacity=0.7;">
        </div>
        <div style="flex: 1;">
            <h2 style="margin-bottom: 1rem;">Facade</h2>
            <ul style="padding-left: 1.5rem;">
                <li>Adaptive origami-inspired design systems</li>
                <li>Integration of wood and glass materials</li>
                <li>Real-time environmental response capabilities</li>
                <li>Smart shading and view optimization</li>
                <li>Data-driven comfort management</li>
                <li>Modular design approach</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # KPI's Definitions & Performance section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'>KPI's Definitions & Performance</h2>", unsafe_allow_html=True)
    
    # Tabs for different disciplines
    kpi_tabs = st.tabs(["Service", "Structure", "Residential", "Industrial", "Facade"])
    
    # Service KPI tab
    with kpi_tabs[0]:
        # Gallery for Service
        try:
            st.image("front_end/assets/Service/02", use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load Service gallery image: {e}")
            
        st.markdown("""
        <p>Distinct Intertwined neighborhoods create a dynamic social network fostering connections and interactions. 
        The principle of space exchange enables spaces to transform seamlessly unlocking layers of openness within the building.</p>
        """, unsafe_allow_html=True)
        
        # Service KPI metrics
        st.subheader("KPI Metrics")
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <img src="front_end/assets/Service/03/service01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Service+KPI'; this.style.opacity=0.7;">
            <h3>Occupancy Efficiency</h3>
            <div class="kpi-value">{:.2f}</div>
        </div>
        """.format(service_dashboard.occupancy_efficiency if hasattr(service_dashboard, 'occupancy_efficiency') else 0.0), 
        unsafe_allow_html=True)
    
    # Structure KPI tab
    with kpi_tabs[1]:
        # Gallery for Structure
        try:
            st.image("front_end/assets/Structure/02", use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load Structure gallery image: {e}")
            
        st.markdown("""
        <p>Forces flow from the top to the floor through dynamic and variated elements, determined by the flow of 
        circulation between functions of the building creating open and flexible spaces, with ever-different spatial qualities</p>
        """, unsafe_allow_html=True)
        
        # Structure KPI metrics
        st.subheader("KPI Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Structure/03/structure01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Structure+KPI'; this.style.opacity=0.7;">
                <h3>Column-Free Area Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(structure_dashboard.column_free_area_ratio if hasattr(structure_dashboard, 'column_free_area_ratio') else 0.0), 
            unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Structure/03/structure01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Structure+KPI'; this.style.opacity=0.7;">
                <h3>Load Capacity per Square Meter</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(structure_dashboard.load_capacity_per_sqm if hasattr(structure_dashboard, 'load_capacity_per_sqm') else 0.0), 
            unsafe_allow_html=True)
    
    # Residential KPI tab
    with kpi_tabs[2]:
        # Gallery for Residential
        try:
            st.image("front_end/assets/Residential/02", use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load Residential gallery image: {e}")
            
        st.markdown("""
        <p>Creating a vibrant and integrated vertical living experience that fosters community connection, 
        sustainability, and accessibility by designing mixed-use spaces, balancing XL and XS residential offerings, 
        providing diverse and adaptable living options</p>
        """, unsafe_allow_html=True)
        
        # Residential KPI metrics
        st.subheader("KPI Metrics")
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <img src="front_end/assets/Residential/03/residential01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Residential+KPI'; this.style.opacity=0.7;">
            <h3>Mixed Use Index</h3>
            <div class="kpi-value">{:.2f}</div>
        </div>
        """.format(residential_dashboard.mixed_use_index if hasattr(residential_dashboard, 'mixed_use_index') else 0.0), 
        unsafe_allow_html=True)
    
    # Industrial KPI tab
    with kpi_tabs[3]:
        # Gallery for Industrial
        try:
            st.image("front_end/assets/Industrial/02", use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load Industrial gallery image: {e}")
            
        st.markdown("""
        <p>A building that breathes life into the city, a vibrant ecosystem that produces its own clean energy, 
        transforms waste into resources, and nurtures fresh food right where you live.</p>
        """, unsafe_allow_html=True)
        
        # Industrial KPI metrics
        st.subheader("KPI Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Industrial/03/industrial01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Industrial+KPI'; this.style.opacity=0.7;">
                <h3>Energy Self-Sufficiency Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(industrial_dashboard.energy_self_sufficiency if hasattr(industrial_dashboard, 'energy_self_sufficiency') else 0.0), 
            unsafe_allow_html=True)
            
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Industrial/03/industrial01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Industrial+KPI'; this.style.opacity=0.7;">
                <h3>Water Recycling Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(industrial_dashboard.water_recycling_ratio if hasattr(industrial_dashboard, 'water_recycling_ratio') else 0.0), 
            unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Industrial/03/industrial01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Industrial+KPI'; this.style.opacity=0.7;">
                <h3>Food Self-sufficiency Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(industrial_dashboard.food_self_sufficiency if hasattr(industrial_dashboard, 'food_self_sufficiency') else 0.0), 
            unsafe_allow_html=True)
            
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Industrial/03/industrial01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Industrial+KPI'; this.style.opacity=0.7;">
                <h3>Waste Utilization Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(industrial_dashboard.waste_utilization_ratio if hasattr(industrial_dashboard, 'waste_utilization_ratio') else 0.0), 
            unsafe_allow_html=True)
    
    # Facade KPI tab
    with kpi_tabs[4]:
        # Gallery for Facade
        try:
            st.image("front_end/assets/Facade/02", use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load Facade gallery image: {e}")
            
        st.markdown("""
        <p>Modular and data-driven, it adjusts in real-time for optimal light, thermal performance, 
        and occupant comfort, creating sustainable, intelligent architectural systems.</p>
        """, unsafe_allow_html=True)
        
        # Facade KPI metrics
        st.subheader("KPI Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Facade/03/facade01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Facade+KPI'; this.style.opacity=0.7;">
                <h3>Daylight Factor & Solar Loads</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(facade_dashboard.daylight_factor if hasattr(facade_dashboard, 'daylight_factor') else 0.0), 
            unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Facade/03/facade01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Facade+KPI'; this.style.opacity=0.7;">
                <h3>Panel Optimization</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(facade_dashboard.panel_optimization if hasattr(facade_dashboard, 'panel_optimization') else 0.0), 
            unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <img src="front_end/assets/Facade/03/facade01.png" style="width: 200px; aspect-ratio: 3/4;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=Facade+KPI'; this.style.opacity=0.7;">
                <h3>Energy Generation Ratio</h3>
                <div class="kpi-value">{:.2f}</div>
            </div>
            """.format(facade_dashboard.energy_generation_ratio if hasattr(facade_dashboard, 'energy_generation_ratio') else 0.0), 
            unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Unified Speckle Model section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'>Unified Speckle Model</h2>", unsafe_allow_html=True)
    
    # Create container for Speckle viewer
    speckle_container = st.container()
    project_id = "9fb8e668b3" # Example project ID - replace with actual ID
    
    # Display federated Speckle viewer
    try:
        display_federated_speckle_viewer(speckle_container, project_id, 600)
    except Exception as e:
        st.error(f"Unable to load Speckle viewer: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Overall Performance section
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'>Overall Performance</h2>", unsafe_allow_html=True)
    
    # Get team performances from statistics
    team_performances = {
        "Service": statistics.get_service_performance() if hasattr(statistics, 'get_service_performance') else 0.75,
        "Structure": statistics.get_structure_performance() if hasattr(statistics, 'get_structure_performance') else 0.82,
        "Residential": statistics.get_residential_performance() if hasattr(statistics, 'get_residential_performance') else 0.68,
        "Industrial": statistics.get_industrial_performance() if hasattr(statistics, 'get_industrial_performance') else 0.92,
        "Facade": statistics.get_facade_performance() if hasattr(statistics, 'get_facade_performance') else 0.84
    }
    
    # Create performance displays
    st.markdown("<div class='performance-container'>", unsafe_allow_html=True)
    
    for team, performance in team_performances.items():
        percentage = int(performance * 100)
        st.markdown(f"""
        <div class="performance-item">
            <h3>{team}</h3>
            <div class="performance-circle">
                <img src="front_end/assets/logo.jpg" alt="Enso Logo" style="width: 100%;" onerror="this.onerror=null; this.src='https://via.placeholder.com/120?text=Enso'; this.style.opacity=0.7;">
                <div class="performance-value">{percentage}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Individual team metrics
    team_metrics_tabs = st.tabs(["Service", "Structure", "Residential", "Industrial", "Facade"])
    
    # Add snapshot of each team's dashboard performance
    with team_metrics_tabs[0]:
        try:
            service_dashboard.display_performance_summary() if hasattr(service_dashboard, 'display_performance_summary') else st.info("Service performance data not available")
        except Exception as e:
            st.error(f"Error displaying Service performance: {e}")
    
    with team_metrics_tabs[1]:
        try:
            structure_dashboard.display_performance_summary() if hasattr(structure_dashboard, 'display_performance_summary') else st.info("Structure performance data not available")
        except Exception as e:
            st.error(f"Error displaying Structure performance: {e}")
    
    with team_metrics_tabs[2]:
        try:
            residential_dashboard.display_performance_summary() if hasattr(residential_dashboard, 'display_performance_summary') else st.info("Residential performance data not available")
        except Exception as e:
            st.error(f"Error displaying Residential performance: {e}")
    
    with team_metrics_tabs[3]:
        try:
            industrial_dashboard.display_performance_summary() if hasattr(industrial_dashboard, 'display_performance_summary') else st.info("Industrial performance data not available")
        except Exception as e:
            st.error(f"Error displaying Industrial performance: {e}")
    
    with team_metrics_tabs[4]:
        try:
            facade_dashboard.display_performance_summary() if hasattr(facade_dashboard, 'display_performance_summary') else st.info("Facade performance data not available")
        except Exception as e:
            st.error(f"Error displaying Facade performance: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "residential_dashboard":
    residential_dashboard.display_residential_dashboard()
elif page == "service_dashboard":
    service_dashboard.display_service_dashboard()
elif page == "structure_dashboard":
    structure_dashboard.display_structure_dashboard()
elif page == "industrial_dashboard":
    industrial_dashboard.display_industrial_dashboard()
elif page == "facade_dashboard":
    facade_dashboard.display_facade_dashboard()
elif page == "data_dashboard":
    data_dashboard.display_data_dashboard()
elif page == "slack_config":
    slack_config.display_slack_config()