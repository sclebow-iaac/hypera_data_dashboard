#IMPORT LIBRARIES
#import streamlit
import streamlit as st
#specklepy libraries
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.transports.server import ServerTransport
from specklepy.api.wrapper import StreamWrapper
from specklepy.objects.base import Base
import numpy as np

#import pandas
import pandas as pd
#import plotly express
import plotly.express as px

# import os
import os

# import sys
import sys

# import dashboards from local files
import dashboards.residential_dashboard as residential_dashboard
import dashboards.service_dashboard as service_dashboard
import dashboards.structure_dashboard as structure_dashboard
import dashboards.industrial_dashboard as industrial_dashboard
import dashboards.facade_dashboard as facade_dashboard

# import data extractors
import data_extraction.data_extractor as data_extractor
import data_extraction.residential_extractor as residential_extractor
import data_extraction.service_extractor as service_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor
import data_extraction.facade_extractor as facade_extractor

# import statistics
import statistics

# import attribute extraction
import attribute_extraction

#--------------------------
#PAGE CONFIG AND CUSTOM CSS
st.set_page_config(
    page_title="Hyperbuilding_A Dashboard",
    page_icon="📊",
    layout="wide"  # Makes the dashboard use full screen width
)

# Add custom CSS
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap');
    
    /* Main background */
    .stApp {
        background-color: #ffffff;
        font-family: 'Roboto Mono', sans-serif;  /* Apply font family to entire app */
    }
    
    /* Main container */
    .main {
        background-color: #ffffff;
        color: white;
        font-family: 'Roboto Mono', sans-serif;
    }
    
    /* Headers */
    .css-10trblm, .css-qrbaxs {
        color: #000000;
        font-weight: 600;
        font-family: 'Roboto Mono', sans-serif !important;  /* Added !important */
    }
    
    /* All text elements */
    .stMarkdown, .stText, div, span, p, h1, h2, h3 {
        font-family: 'Roboto Mono', sans-serif !important;
    }
    
    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        background-color: #ffffff;
        color: black;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cards and containers */
    div.css-12w0qpk.e1tzin5v2 {
        background-color: #ffffff;
        color: black;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Text color */
    .css-1dp5vir {
        color: black;
    }
    
    /* Buttons and selectbox */
    .stButton>button, .stSelectbox {
        background-color: #ffffff;
        color: black;
        border-radius: 0.3rem;
    }
    
    /* Markdown text */
    .css-183lzff {
        color: black;
    }
    
    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        background-color: #2d2d2d;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

#--------------------------

#--------------------------
#CONTAINERS
header = st.container()
input = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()
#--------------------------

#--------------------------
#HEADER
#Page Header
with header:
    # Center title and image using HTML/CSS
    st.markdown("""
        <div style="text-align: center;">
            <h1>Speckle Stream Activity App📈</h1>
        </div>
    """, unsafe_allow_html=True)
    
 
#About info
    with header.expander("Hyper Building A🔽", expanded=True):
        st.markdown(
        """We use this space to record collaborators, commits, and timelines, to collect project data in a cohesive, accessible format.
"""
)
#--------------------------

with input:
    st.subheader("Inputs") # Add a subheader

#-------
    # Toggle buttons for showing/hiding viewer, statistics, and team-specific metrics
    # Columns for toggle buttons
    viewer_toggle, statistics_toggle, team_metrics_toggle, attribute_selection_toggle = st.columns(4)
#-------


#-------

# #-------
# #Toggle buttons
show_viewer = viewer_toggle.checkbox("Show Viewer", value=True, help="Toggle to show/hide the viewer")
show_statistics = statistics_toggle.checkbox("Show Statistics", value=True, help="Toggle to show/hide the statistics")
show_team_specific_metrics = team_metrics_toggle.checkbox("Show Team Metrics", value=True, help="Toggle to show/hide the team-specific metrics")
show_attribute_extraction = attribute_selection_toggle.checkbox("Show Attribute Extraction", value=True, help="Toggle to show/hide the attribute extraction")

#-------
# #Speckle Server and Token
speckleServer = "macad.speckle.xyz"
speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
#CLIENT
client = SpeckleClient(host=speckleServer)
#Get account from Token
account = get_account_from_token(speckleToken, speckleServer)
#Authenticate
client.authenticate_with_account(account)
#-------

# Get the team project
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
    #--------------------------
    #create a definition that generates an iframe from commit id
    def commit2viewer(stream, commit, height=400) -> str:
        embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
        # print(embed_src)  # Print the URL to verify correctness
        return st.components.v1.iframe(src=embed_src, height=height)

    #VIEWER👁‍🗨
    with viewer:
        st.subheader("Selected Version👇")
        version2viewer(project, selected_model, selected_version)

if show_statistics:
    statistics.show(report, client, project, models, versions)
# print(f'selected_model: {selected_model}\n')
# print(f'selected_version: {selected_version}\n')

if show_team_specific_metrics:
    # TEAM SPECIFIC METRICS
    st.subheader("Team Specific Metrics 👥 [TOTALLY FAKE DATA RIGHT NOW]")

    # Team selection dropdown
    selected_team = st.selectbox(
        "Select Team",
        ["Residential", "Service", "Structure", "Industrial", "Facade"],
        key="team_selector"
    )

    # Create columns for team metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    # Display team-specific metrics based on selection
    if selected_team == "Residential":
        residential_data = residential_extractor.extract(models, client, project_id)
        # print(f'Residential data: {residential_data}\n')

        # residential_dashboard.run(metric_col1, metric_col2, selected_team)

    elif selected_team == "Service":
        service_data = service_extractor.extract(models, client, project_id)
        # print(f'Service data: {service_data}\n')

        # service_dashboard.run(metric_col1, metric_col2, selected_team)
        
    elif selected_team == "Structure":
        structure_data = structure_extractor.extract(models, client, project_id)
        # print(f'Structure data: {structure_data}\n')

        # structure_dashboard.run(metric_col1, metric_col2, selected_team)

    elif selected_team == "Industrial":
        industrial_data = industrial_extractor.extract(models, client, project_id)
        # print(f'Industrial data: {industrial_data}\n')

        # industrial_dashboard.run(metric_col1, metric_col2, selected_team)

    elif selected_team == "Facade":
        facade_data = facade_extractor.extract(models, client, project_id)
        # print(f'Facade data: {facade_data}\n')

        # facade_dashboard.run(metric_col1, metric_col2, selected_team)

# Get geometry data from the selected version

if show_attribute_extraction:
    attribute_extraction.run(selected_version, client, project)