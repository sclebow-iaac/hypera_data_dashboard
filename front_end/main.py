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

#PAGE CONFIG AND CUSTOM CSS
#--------------------------
st.set_page_config(
    page_title="Hyperbuilding_A Dashboard",
    page_icon="📊",
    layout="wide"  # Makes the dashboard use full screen width
)

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
    </style>
""", unsafe_allow_html=True)

# Sidebar for selecting dashboards
# dashboard_options = ["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data", "Slack Configuration"]
# selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)


selected_dashboard = create_top_menu(["Main", "Residential", "Service", "Structure", "Industrial", "Facade", "Data", "Slack Configuration"])

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
        # Center title and image using HTML/CSS
        st.markdown("""
            <div style="text-align: center;">
                <h1>Welcome to Hyper Building A!</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Add slideshow
        st.markdown("### Project Gallery")
        
        # List of images for slideshow
        images = [
            {"path": "assets/facade.png", "caption": "Facade"},
            {"path": "assets/residential.png", "caption": "Residential"},
            {"path": "assets/service.png", "caption": "Service"},
            {"path": "assets/structure.png", "caption": "Structure"},
            {"path": "assets/industrial.png", "caption": "Industrial"}
        ]
        
        # Create columns for slideshow navigation
        prev_col, img_col, next_col = st.columns([1, 10, 1])
        
        # Initialize slideshow index in session state if not exists
        if 'slideshow_idx' not in st.session_state:
            st.session_state.slideshow_idx = 0
        
        # Navigation buttons
        with prev_col:
            if st.button("←", key="prev_main"):
                st.session_state.slideshow_idx = (st.session_state.slideshow_idx - 1) % len(images)
        with next_col:
            if st.button("→", key="next_main"):
                st.session_state.slideshow_idx = (st.session_state.slideshow_idx + 1) % len(images)
        
        # Display current image
        with img_col:
            current_image = images[st.session_state.slideshow_idx]
            try:
                st.image(current_image["path"], 
                        caption=current_image["caption"], 
                        use_container_width=True)
            except FileNotFoundError:
                st.warning(f"Please add the image {current_image['path']} to your assets folder")
        
        st.markdown("---")  # Add a separator

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
    elif selected_dashboard == "Slack Configuration":
        slack_config.run()

#--------------------------