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

run_slack_process()

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

# Function to display the residential dashboard
def display_residential_dashboard():
    with dashboard_placeholder.container():
        selected_team = "residential"  # Set the selected team or get it from user input
        residential_dashboard.run(selected_team)  # Call the function from the residential dashboard

# Function to display the service dashboard
def display_service_dashboard():
    with dashboard_placeholder.container():
        selected_team = "service"  # Set the selected team
        service_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the structure dashboard
def display_structure_dashboard():
    with dashboard_placeholder.container():
        selected_team = "structure"  # Set the selected team
        structure_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the industrial dashboard
def display_industrial_dashboard():
    with dashboard_placeholder.container():
        selected_team = "industrial"  # Set the selected team
        industrial_dashboard.run(selected_team)  # Only pass selected_team

# Function to display the facade dashboard
def display_facade_dashboard():
    with dashboard_placeholder.container():
        selected_team = "facade"  # Set the selected team
        facade_dashboard.run(selected_team)  # Only pass selected_team


st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap');
    
    /* Main background */
    .stApp {
        font-family: 'Roboto Mono', sans-serif;  /* Apply font family to entire app */
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
    div.stButton > button {
        background-color: transparent;
        border: 0px solid #000000;
        padding: 0;
        font-size: 8px;  /* Change this value to adjust font size */
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


selected_dashboard = create_top_menu(["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data", "SlackBot"])

# Create a placeholder for the dashboard content
dashboard_placeholder = st.empty()


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
    
    # Create a full-width container for the image (with no padding)
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
            margin-top: -50px;
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
    
    # Add Principles section after the slideshow
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
    
    # Remove separator to reduce extra space

    with input_container:  # Use the new name here
        st.subheader("Inputs")
        viewer_toggle, statistics_toggle = st.columns(2)
        
        show_viewer = viewer_toggle.checkbox("Show Speckle Viewer", value=True)
        show_statistics = statistics_toggle.checkbox("Show Project Statistics", value=True)

        # #-------
        # #Speckle Server and Token
        speckleServer = "macad.speckle.xyz"
        speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
        #CLIENT
        client = SpeckleClient(host=speckleServer)
        #Get account from Token
        account = get_account_from_token(speckleToken, speckleServer)
        #Authenticate
        client.authenticate_with_account(account)
        # #-------

        # # Get the team project
        project_id = '31f8cca4e0'
        selected_project = client.project.get(project_id=project_id)

        # Get the project with models
        project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
        # print(f'Project: {project.name}')

        # Get the models
        models = project.models.items

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
        try:
            selected_version = versions[keys.index(selected_version_key)]

            # Create a iframe to display the selected version
            def version2viewer(project, model, version, height=400) -> str:
                embed_src = f"https://macad.speckle.xyz/projects/{project.id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"            
                # print(f'embed_src {embed_src}')  # Print the URL to verify correctness
                # print()
                return st.components.v1.iframe(src=embed_src, height=height)

            if show_viewer:
                with viewer:
                    st.subheader("Selected Version👇")
                    version2viewer(project, selected_model, selected_version)

            if show_statistics:
                statistics.show(report, client, project, models, versions)

            # Add a separator
            st.markdown("---")
            # Add attribute extraction for debugging
            attribute_extraction.run(selected_version, client, project)
        except:
            st.error("No version selected/found. Please select a version to analyze.")



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
    elif selected_dashboard == "SlackBot":
        slack_config.run()

#--------------------------