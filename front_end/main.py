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

# import data extraction
import data_extraction.residential_extractor as residential_extractor
import data_extraction.service_extractor as service_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor
import data_extraction.facade_extractor as facade_extractor
import data_extraction.data_extractor as data_extractor

# import statistics
import project_statistics as statistics

# import attribute extraction
import attribute_extraction

import subprocess
import datetime

import sys
import os
import signal

#PAGE CONFIG AND CUSTOM CSS
#--------------------------
st.set_page_config(
    page_title="Hyperbuilding_A Dashboard",
    page_icon="front_end/assets/logo.jpg",
    layout="wide"  # Makes the dashboard use full screen width
)

@st.cache_resource
def run_slack_process():
    print("Starting Slack message task...")

    # Run the Slack message task in a subprocess
    process = subprocess.Popen([sys.executable, 'front_end/dashboards/slack_message_task.py']) 

    return process

# run_slack_process() # Commented out to avoid running the process at startup

def display_federated_speckle_viewer(container, project_id, height):
    # Function to create a federated Speckle viewer
    # With multiple models

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

    display_speckle_viewer(
        container=container, 
        project_id=project_id, 
        model_id=federated_model_id,
        is_transparent=True,
        hide_controls=False,
        hide_selection_info=False,
        no_scroll=False,
        height=height,
    )

st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap');
    
    /* Main background */
    .stApp {
        font-family: 'Roboto Mono', sans-serif;  /* Apply font family to entire app */
        font-size: 14px !important;  /* Base font size for the entire app */
    }
    
    /* Main container */
    .main {
        font-family: 'Roboto Mono', sans-serif;
        font-size: 14px !important;
    }
    
    /* Headers */
    .css-10trblm, .css-qrbaxs {
        font-weight: 600;
        font-family: 'Roboto Mono', sans-serif !important;
    }
    
    /* All text elements */
    .stMarkdown, .stText, div, span, p {
        font-family: 'Roboto Mono', sans-serif !important;
        font-size: 13px !important;
    }

    /* Header sizes */
    h1 {
        font-size: 28px !important;
    }
    
    h2 {
        font-size: 24px !important;
    }
    
    h3 {
        font-size: 20px !important;
    }

    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        font-size: 16px !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }
    
    /* Cards and containers */
    div.css-12w0qpk.e1tzin5v2 {
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Buttons and selectbox */
    div.stButton > button {
        background-color: transparent;
        border: 0px solid #000000;
        padding: 0;
        font-size: 14px !important;  /* Changed from 8px to match overall theme */
    }
    div.stButton > button:hover {
        background-color: #ffffff;
        border-radius: 5px;
    }
    /* Style for selected button */
    div.stButton > button[data-selected="true"] {
        border-bottom: 2px solid #000000;
        border-radius: 0;
    }
    div.stButton > button[data-selected="true"]:hover {
        background-color: transparent;
    }
    
    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    </style>
    
""", unsafe_allow_html=True)

# Sidebar for selecting dashboards
# dashboard_options = ["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data", "Slack Configuration"]
# selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)


selected_dashboard = create_top_menu(["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data", "SlackBot", 'ProjectStats'])

# Create a placeholder for the dashboard content
dashboard_placeholder = st.empty()

left_margin, content_container, right_margin = get_content_container_columns()

with content_container:
    #--------------------------
    #CONTAINERS
    header = st.container()
    input_container = st.container()  # Renamed from 'input' to 'input_container'
    viewer = st.container()
    report = st.container()
    graphs = st.container()
    #--------------------------


    # # Only show main interface if "Main" is selected
    if selected_dashboard == "Main":
        #HEADER
        #Page Header
        with header:
            # First, get all images for the slideshow
            images = [
                {"path": "front_end/assets/Enso/02/ensolr.gif", "caption": "The Essence of Ensō", 
                "description": "Ensō, the Zen circle, represents one of the most fundamental principles in Japanese aesthetics and philosophy. Traditionally drawn in a single, fluid brush stroke, it symbolizes absolute enlightenment, strength in imperfection, and the cyclical nature of existence"},
                # Add other images as needed
            ]
            
            # Initialize slideshow index in session state if not exists
            if 'slideshow_idx' not in st.session_state:
                st.session_state.slideshow_idx = 0
            
            # Get current image
            current_image = images[st.session_state.slideshow_idx]
            
            # Use the same container structure as the top menu bar
            # Reference from dashboard.py: image_container, header_container, button_container = st.columns([1, 5, 7], gap="small")
            
            # Create an empty container to maintain consistent spacing
            empty = st.container()
            
            # Create a full-width container for the image 
            st.markdown("""
                <style>
                /* Eliminate space between menu and image */
                section.main > div.block-container {
                    padding-top: 0;
                }
                
                /* Make the image container match the top menu width */
                div.element-container:has(img) {
                    max-width: 100%;
                    width: 100%;
                    padding: 0;
                    margin-top: 0px;
                }
                
                /* Display navigation buttons as an overlay */
                .nav-buttons {
                    position: absolute;
                    top: 50%;
                    width: 100%;
                    z-index: 100;
                    display: flex;
                    justify-content: space-between;
                    padding: 0 200px;
                }
                
                /* Style caption and description */
                .image-caption {
                    text-align: center;
                    padding: 0 90px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Display the image with use_container_width=True to fill the space
            st.image(current_image["path"], use_container_width=True)
            
            # Add navigation buttons as a row below the image
            nav_left, nav_center, nav_right = st.columns([1, 10, 1])
            
            with nav_left:
                if st.button("←", key="prev_main"):
                    st.session_state.slideshow_idx = (st.session_state.slideshow_idx - 1) % len(images)
                    st.experimental_rerun()
                    
            with nav_center:
                st.markdown(f"""
                <div class="image-caption">
                    <h2>{current_image.get('caption', '')}</h2>
                    <p>{current_image.get('description', '')}</p>
                    <p class="caption-small">Core Principles of Ensō Hyperbuilding</p>
                </div>
                """, unsafe_allow_html=True)
                    
            with nav_right:
                if st.button("→", key="next_main"):
                    st.session_state.slideshow_idx = (st.session_state.slideshow_idx + 1) % len(images)
                    st.experimental_rerun()
            


            # PRINCIPLES SECTION
            principles_container = st.container()
            with principles_container:
                # Add more padding before the principles section
                st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
                
                # Left-aligned title with more padding below
                st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>Ensō Hyperbuilding embraces these principles through:</h3>", unsafe_allow_html=True)
                
                # Create three principle containers
                for i, (title, description) in enumerate([
                    ("Completion Through Incompletion", 
                    "A design that allows for growth and adaptation, with spaces that evolve with user needs and systems that improve through iteration."),
                    ("Moment of Creation", 
                    "Integration of spontaneous and planned elements, balancing control and natural development, and creating harmony between designed and emergent patterns."),
                    ("Unity of Opposites", 
                    "Juxtaposition of traditional and modern elements, balance between public and private spaces, and harmony between technology and nature.")
                ]):
                    # Create a container for each principle
                    principle = st.container()
                    with principle:
                        # Create two columns - one narrow for the logo, one wide for the text
                        logo_col, text_col = st.columns([1, 10])
                        
                        # Add logo with number in the left column
                        with logo_col:
                            # Use Streamlit's native image display with number overlay
                            # First create a container for positioning
                            img_container = st.container()
                            
                            # Display the image
                            img_container.image("front_end/assets/logo.jpg", width=80)
                        
                            # Add the number overlay using CSS positioning
                            img_container.markdown(f"""
                            <div style="
                                position: relative;
                                top: -75px;
                                left: 30px;
                                font-size: 20px;
                                font-weight: bold;
                                width: 20px;
                                text-align: center;
                                color: black;
                            ">
                                {i+1}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        # Add text in the right column
                        with text_col:
                            st.markdown(f"""
                            <div style="margin-left: 30px;">
                                <h4 style="margin-bottom: 10px; margin-top: 15px;">{title}</h4>
                                <p>{description}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add some space between principles
                        if i < 2:  # Don't add after the last one
                            st.markdown("<hr style='margin: 20px 0; opacity: 0.3;'>", unsafe_allow_html=True)



            # VISON SECTION
            vision_container = st.container()
            with vision_container:
                # Add spacing before the vision section
                st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
                
                # Display the full-width image
                st.image("front_end/assets/vision.png", use_container_width=True)
                
                # Add centered title and text
                st.markdown("""
                <div style="text-align: center; margin-top: 0px; margin-bottom: 0px;">
                    <h2>Our Unified Vision</h2>
                    <p>The Ensō Hyperbuilding is brought to life through six specialized teams, each contributing to our circular philosophy of completeness through continuous cycles.</p>
                </div>
                """, unsafe_allow_html=True)

            # DISCIPLINES SECTION
            disciplines_container = st.container()
            with disciplines_container:
                # Add spacing before the disciplines section
                st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
                
                # Define discipline data with properly formatted markdown
                disciplines = [
                    {
                        "name": "Service",
                        "gif_path": "front_end/assets/Service/01/serviceLR.gif",
                        "description": """
            At the heart of the concept lies a human-scale approach, where even expansive spaces become a canvas for community life. By interweaving distinct neighborhoods into a dynamic social network, the design fosters connection and interaction. The principle of space exchange enables spaces to transform seamlessly unlocking layers of openness within the building.

            Circulation is envisioned as an experience — fluid, engaging, and deeply attuned to the proximities that link people and functions. This vision is supported by innovative movement systems, spatial proximity tailored to community needs, and a sustainable balance between energy-demanding, energy-neutral, and energy-producing systems.
                        """,
                        "markdown_content": """
            # Service

            * Human-scale design approach in expansive spaces
            * Dynamic social network creation between neighborhoods
            * Flexible space exchange systems
            * Fluid and engaging circulation experiences
            * Proximity-based function organization
            * Balance between energy-demanding and energy-producing systems
                        """,
                        "image_on_left": True
                    },
                    {
                        "name": "Structure",
                        "gif_path": "front_end/assets/Structure/01/structureLR.gif",
                        "description": """
            Service﻿ Team Vision
            At the heart of the concept lies a human-scale approach, where even expansive spaces become a canvas for community life. By interweaving distinct neighborhoods into a dynamic social network, the design fosters connection and interaction. The principle of space exchange enables spaces to transform seamlessly unlocking layers of openness within the building.

            Circulation is envisioned as an experience — fluid, engaging, and deeply attuned to the proximities that link people and functions. This vision is supported by innovative movement systems, spatial proximity tailored to community needs, and a sustainable balance between energy-demanding, energy-neutral, and energy-producing systems.
                        """,
                        "markdown_content": """
            # Structure

            * Integration of three primary flows (forces, people, water)
            * Dynamic and varied structural elements
            * Flexible space creation
            * Water management through mass damping
            * Flow-based spatial organization
            * Adaptive spatial qualities
                        """,
                        "image_on_left": False
                    },
                    {
                        "name": "Residential",
                        "gif_path": "front_end/assets/Residential/01/residentialLR.gif",
                        "description": """
            Our vision is to create a vibrant and integrated vertical living experience that fosters community connection, sustainability, and accessibility. By designing mixed-use spaces within a hyperbuilding, we aim to balance XL and XS residential offerings, providing diverse and adaptable living options.

            Our focus is on enhancing environmental impact, user experience, and fast circulation within and between neighborhoods, all while creating a machine-like city concept inside a hyperbuilding.
                        """,
                        "markdown_content": """
            # Residential

            * Connection to public spaces
            * Efficiency in Unit Clustering
            * Efficiency in Unit Layout
                        """,
                        "image_on_left": True
                    },
                    {
                        "name": "Industrial",
                        "gif_path": "front_end/assets/Industrial/01/industrialLR.gif",
                        "description": """
            A building that breathes life into the city —a vibrant ecosystem that produces its own clean energy, transforms waste into resources, and nurtures fresh food right where you live. It's a prosumer powerhouse, generating and sharing renewable energy while creating harmony between humans and the environment.

            Here, every design choice embodies zero-waste principles, turning challenges into opportunities, and every space is alive with nature-based solutions that blur the line between the built and natural worlds. This is more than a building; it's a bold step toward a regenerative future where sustainability is not just a goal but a way of life.
                        """,
                        "markdown_content": """
            # Industrial

            * Clean energy production and management
            * Waste-to-resource transformation systems
            * On-site food production integration
            * Prosumer energy sharing framework
            * Zero-waste implementation strategies
            * Nature-based solutions (NBS) integration
            * Regenerative system development
                        """,
                        "image_on_left": False
                    },
                    {
                        "name": "Facade",
                        "gif_path": "front_end/assets/Facade/01/facadeLR.gif",
                        "description": """
            A hyperbuilding with an adaptive origami-inspired wood and glass facade balances shading, views, and energy efficiency.

            Modular and data-driven, it adjusts in real-time for optimal light, thermal performance, and occupant comfort, creating a sustainable, intelligent architectural system.
                        """,
                        "markdown_content": """
            # Facade

            * Adaptive origami-inspired design systems
            * Integration of wood and glass materials
            * Real-time environmental response capabilities
            * Smart shading and view optimization
            * Data-driven comfort management
            * Modular design approach
                        """,
                        "image_on_left": True
                    }
                ]
                
                # Create container for each discipline
                for discipline in disciplines:
                    # Create a container with padding
                    discipline_container = st.container()
                    
                    # Add styling for the container
                    st.markdown("""
                    <style>
                    .discipline-container {
                        border: 10px solid #ffffff;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 10px 10px 10px 10px;
                        background-color: #ffffff;
                        width: 100%;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Start the styled container
                    st.markdown('<div class="discipline-container">', unsafe_allow_html=True)
                    
                    # Create three columns - image, spacing, and text
                    if discipline["image_on_left"]:
                        img_col, spacing_col, text_col = st.columns([10, 1, 10])
                    else:
                        text_col, spacing_col, img_col = st.columns([10, 1, 10])
                    
                    # Add image to image column
                    with img_col:
                        st.image(discipline["gif_path"], use_container_width=True)
                        
                    # Empty middle column serves as spacing
                    with spacing_col:
                        st.write("")
                    
                    # Add text to text column with simple formatting
                    with text_col:
                        # Add some vertical margin at the top for vertical centering
                        st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
                        
                        # Make the title larger
                        st.markdown(f"<h1 style='font-size: 2.5rem; margin-bottom: 30px;'>{discipline['name']}</h1>", unsafe_allow_html=True)
                        
                        # Add description paragraph if available
                        if "description" in discipline and discipline["description"]:
                            # Split paragraphs and format each
                            paragraphs = discipline["description"].strip().split("\n\n")
                            for paragraph in paragraphs:
                                if paragraph.strip():  # Only process non-empty paragraphs
                                    st.markdown(f"<p style='font-size: 1.1rem; line-height: 1.6; margin-bottom: 20px;'>{paragraph.strip()}</p>", unsafe_allow_html=True)
                            
                            # Add spacing between description and bullet points
                            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                        
                        # Extract bullet points from markdown content
                        bullet_points = []
                        for line in discipline["markdown_content"].split('\n'):
                            if line.strip().startswith('*'):
                                # Remove the '*' and any leading/trailing whitespace
                                point = line.strip()[1:].strip()
                                if point:  # Ensure the point is not empty
                                    bullet_points.append(point)
                        
                        # Add each bullet point with custom styling
                        for point in bullet_points:
                            st.markdown(f"<div style='font-size: 1.2rem; margin-bottom: 15px; line-height: 1.8;'>• {point}</div>", unsafe_allow_html=True)
                        
                        # Add some vertical margin at the bottom for vertical centering
                        st.markdown("<div style='margin-bottom: 0px;'></div>", unsafe_allow_html=True)
                    
                    # End the styled container
                    st.markdown('</div>', unsafe_allow_html=True)






            # KPI's SLIDESHOW SECTION
            vision_container = st.container()
            with vision_container:
                # Add spacing before the vision section
                st.markdown("<div style='margin-top: 200px;'></div>", unsafe_allow_html=True)
                
                # Add centered title and text
                st.markdown("""
                <div style="text-align: center; margin-top: 50px; margin-bottom: 50px;">
                    <h1>KPI's Definitions & Performance</h1>
                """, unsafe_allow_html=True)

                # Display the full-width image
                st.image("front_end/assets/Service/02/servicelr.gif", use_container_width=True)

                # Add centered caption text
                st.markdown("""
                <div style="text-align: center; margin-top: 5px; margin-bottom: 100px;">
                    <h1>Service Design Strategy Integration</h1>
                    <p>Distinct Intertwined neighborhoods create a dynamic social network fostering connections and interactions. The principle of space exchange enables spaces to transform seamlessly unlocking layers of openness within the building.</p>
                </div>
                """, unsafe_allow_html=True)

            
            # VERTICAL COLUMNS FOR KPI'S
            kpi_metrics_container = st.container()
            with kpi_metrics_container:
            # Add spacing before KPI metrics
                st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
            
            # Create 9 columns: 5 for content and 4 for padding
            cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])
            
            models, client, project_id = setup_speckle_connection()

            # Service column (index 0)
            with cols[0]:
                # Discipline name
                st.markdown("<h3 style='text-align: center;'>Service</h3>", unsafe_allow_html=True)

                # Discipline image
                st.image("front_end/assets/Service/03/service01.png")

                # Caption
                st.markdown("<p style='text-align: center;'><strong>Service KPIs</strong></p>", unsafe_allow_html=True)
                
                # Call the service dashboard to get the metrics
                verified, team_data, model_data = service_extractor.extract(attribute_display=False)
                service_metrics = service_dashboard.generate_metrics(verified, team_data)
                display_st_metric_values(container=cols[0], metrics=service_metrics, use_columns=False, include_header=False)
                
            # Structure column (index 2)
            with cols[2]:
                # Discipline name
                st.markdown("<h3 style='text-align: center;'>Structure</h3>", unsafe_allow_html=True)
                
                # Discipline image
                st.image("front_end/assets/Structure/03/structure01.png")
                
                # Caption
                st.markdown("<p style='text-align: center;'><strong>Structure KPIs</strong></p>", unsafe_allow_html=True)
                
                verified, team_data, model_data = structure_extractor.extract(attribute_display=False)
                structure_metrics = structure_dashboard.generate_metrics(verified, team_data)
                display_st_metric_values(container=cols[2], metrics=structure_metrics, use_columns=False, include_header=False)
            
            # Residential column (index 4)
            with cols[4]:
                # Discipline name
                st.markdown("<h3 style='text-align: center;'>Residential</h3>", unsafe_allow_html=True)
                
                # Discipline image
                st.image("front_end/assets/Residential/03/residential01.png")
                
                # Caption
                st.markdown("<p style='text-align: center;'><strong>Residential KPIs</strong></p>", unsafe_allow_html=True)
                
                verified, team_data, model_data = residential_extractor.extract(attribute_display=False)
                residential_metrics = residential_dashboard.generate_metrics(verified, team_data)
                display_st_metric_values(container=cols[4], metrics=residential_metrics, use_columns=False, include_header=False)
            
            # Industrial column (index 6)
            with cols[6]:
                # Discipline name
                st.markdown("<h3 style='text-align: center;'>Industrial</h3>", unsafe_allow_html=True)
                
                # Discipline image
                st.image("front_end/assets/Industrial/03/industrial01.png")
                
                # Caption
                st.markdown("<p style='text-align: center;'><strong>Industrial KPIs</strong></p>", unsafe_allow_html=True)
                
                verified, team_data, model_data = industrial_extractor.extract(attribute_display=False)
                industrial_metrics = industrial_dashboard.generate_metrics(verified, team_data)
                display_st_metric_values(container=cols[6], metrics=industrial_metrics, use_columns=False, include_header=False)

            # Facade column (index 8)
            with cols[8]:
                # Discipline name
                st.markdown("<h3 style='text-align: center;'>Facade</h3>", unsafe_allow_html=True)
                
                # Discipline image
                st.image("front_end/assets/Facade/03/facade01.png")
                
                # Caption
                st.markdown("<p style='text-align: center;'><strong>Facade KPIs</strong></p>", unsafe_allow_html=True)
                
                verified, team_data, model_data = facade_extractor.extract(attribute_display=False)
                facade_metrics = facade_dashboard.generate_metrics(verified, team_data)
                display_st_metric_values(container=cols[8], metrics=facade_metrics, use_columns=False, include_header=False)

            # # Add speckle inputs selection menu
            # with input_container:  # Use the new name here
            #     st.subheader("Inputs")
            #     viewer_toggle, statistics_toggle = st.columns(2)
                
            #     show_viewer = viewer_toggle.checkbox("Show Speckle Viewer", value=True)
            #     show_statistics = statistics_toggle.checkbox("Show Project Statistics", value=True)

            #     # #-------
            #     # #Speckle Server and Token
            #     speckleServer = "macad.speckle.xyz"
            #     speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
            #     #CLIENT
            #     client = SpeckleClient(host=speckleServer)
            #     #Get account from Token
            #     account = get_account_from_token(speckleToken, speckleServer)
            #     #Authenticate
            #     client.authenticate_with_account(account)
            #     # #-------

            #     # # Get the team project
            #     project_id = '31f8cca4e0'
            #     selected_project = client.project.get(project_id=project_id)

            #     # Get the project with models
            #     project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
            #     # print(f'Project: {project.name}')

            #     # Get the models
            #     models = project.models.items

            #     # Add model selection
            #     selected_model_name = st.selectbox(
            #         label="Select model to analyze",
            #         options=[m.name for m in models],
            #         help="Select a specific model to analyze its data"
            #     )

            #     # Get the selected model object
            #     selected_model = [m for m in models if m.name == selected_model_name][0]

            #     # Get the versions for the selected model
            #     versions = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=100).items

            #     def versionName(version):
            #         timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
            #         return ' - '.join([version.authorUser.name, timestamp, version.message])

            #     keys = [versionName(version) for version in versions]

            #     # Add version selection
            #     selected_version_key = st.selectbox(
            #         label="Select version to analyze",
            #         options=keys,
            #         help="Select a specific version to analyze"
            #     )
            #     try:
            #         selected_version = versions[keys.index(selected_version_key)]

            #         # Create a iframe to display the selected version
            #         def version2viewer(project, model, version, height=400) -> str:
            #             embed_src = f"https://macad.speckle.xyz/projects/{project.id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"            
            #             # print(f'embed_src {embed_src}')  # Print the URL to verify correctness
            #             # print()
            #             return st.components.v1.iframe(src=embed_src, height=height)

            #         if show_viewer:
            #             with viewer:
            #                 st.subheader("Selected Version👇")
            #                 version2viewer(project, selected_model, selected_version)

            #         if show_statistics:
            #             statistics.show(report, client, project, models, versions)

            #         # Add a separator
            #         st.markdown("---")
            #         # Add attribute extraction for debugging
            #         attribute_extraction.run(selected_version, client, project)
            #     except:
            #         st.error("No version selected/found. Please select a version to analyze.")

    else:
        with dashboard_placeholder.container():
            # Display only the selected dashboard
            if selected_dashboard == "Residential":
                residential_dashboard.run('residential')
            elif selected_dashboard == "Service":
                service_dashboard.run('service')
            elif selected_dashboard == "Structure":
                structure_dashboard.run('structure')
            elif selected_dashboard == "Industrial":
                industrial_dashboard.run('industrial')
            elif selected_dashboard == "Facade":
                facade_dashboard.run('facade')
            elif selected_dashboard == "Data":
                data_dashboard.run()
            elif selected_dashboard == "SlackBot":
                slack_config.run()
            elif selected_dashboard == 'ProjectStats':
                statistics.run()

            #--------------------------