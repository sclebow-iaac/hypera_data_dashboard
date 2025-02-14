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
import front_end.dashboards.residential_dashboard as residential_dashboard
import front_end.dashboards.service_dashboard as service_dashboard
import front_end.dashboards.structure_dashboard as structure_dashboard
import front_end.dashboards.industrial_dashboard as industrial_dashboard
import front_end.dashboards.facade_dashboard as facade_dashboard

#--------------------------
#PAGE CONFIG
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
    #Columns for inputs
    serverCol, tokenCol = st.columns([1,3])
    
    # Toggle buttons for showing/hiding viewer, statistics, and team-specific metrics
    # Columns for toggle buttons
    viewer_toggle, statistics_toggle, team_metrics_toggle, attribute_selection_toggle = st.columns(4)
#-------


#-------
#User Input boxes
speckleServer = serverCol.text_input("Server URL", "macad.speckle.xyz", help="Speckle server to connect.")
speckleToken = tokenCol.text_input("Speckle token", "", help="If you don't know how to get your token, take a look at this [link](<https://speckle.guide/dev/tokens.html>)👈")

# #-------
# #Toggle buttons
show_viewer = viewer_toggle.checkbox("Show Viewer", value=True, help="Toggle to show/hide the viewer")
show_statistics = statistics_toggle.checkbox("Show Statistics", value=True, help="Toggle to show/hide the statistics")
show_team_specific_metrics = team_metrics_toggle.checkbox("Show Team Metrics", value=True, help="Toggle to show/hide the team-specific metrics")
show_attribute_extraction = attribute_selection_toggle.checkbox("Show Attribute Extraction", value=True, help="Toggle to show/hide the attribute extraction")

#-------
#CLIENT
client = SpeckleClient(host=speckleServer)
#Get account from Token
account = get_account_from_token(speckleToken, speckleServer)
#Authenticate
client.authenticate_with_account(account)
#-------

# Get projects
projects = client.stream.list()

# Get the selected project object
selected_project_name = "Hyperbuilding_Team_A"
selected_project = [p for p in projects if p.name == selected_project_name][0]

# Get the project with models
project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
print(f'Project: {project.name}')

# Get the models
models = project.models.items

for model in models:
    print()
    print(f'Model: {model}')

# Add model selection
selected_model_name = st.selectbox(
    label="Select model to analyze",
    options=[m.name for m in models],
    help="Select a specific model to analyze its data"
)

print()
print(f'Selected model name: {selected_model_name}')

# Get the selected model object
selected_model = [m for m in models if m.name == selected_model_name][0]

print()
print(f'Selected model: {selected_model}')
print()

# Get the versions for the selected model
versions = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=100).items

for version in versions:
    print(f'Version: {version}')
    print()

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
    print(f'embed_src {embed_src}')  # Print the URL to verify correctness
    print()
    return st.components.v1.iframe(src=embed_src, height=height)

if show_viewer:
    #--------------------------
    #create a definition that generates an iframe from commit id
    def commit2viewer(stream, commit, height=400) -> str:
        embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
        print(embed_src)  # Print the URL to verify correctness
        return st.components.v1.iframe(src=embed_src, height=height)

    #VIEWER👁‍🗨
    with viewer:
        st.subheader("Selected Version👇")
        version2viewer(project, selected_model, selected_version)

if show_statistics:
    with report:
        st.subheader("Statistics")

    # Columns for Cards
    modelCol, versionCol, connectorCol, contributorCol = st.columns(4)

    #DEFINITIONS
    #create a definition to convert your list to markdown
    def listToMarkdown(list, column):
        list = ["- " + i +  "\n" for i in list]
        list = "".join(list)
        return column.markdown(list)

    #Model Card 💳
    modelCol.metric(label = "Number of Models in Project", value= len(models))
    #branch names as markdown list
    modelNames = [m.name for m in models]
    listToMarkdown(modelNames, modelCol)

    #Version Card 💳
    versionCol.metric(label = "Number of Versions in Selected Model", value= len(versions))

    def get_all_versions_in_project(project):
        all_versions = []
        for model in project.models.items:
            versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
            all_versions.extend(versions)
        return all_versions

    #Connector Card 💳
    #connector list
    all_versions_in_project = get_all_versions_in_project(project)
    connectorList = [v.sourceApplication for v in all_versions_in_project]
    #number of connectors
    connectorCol.metric(label="Number of Connectors in Project", value= len(dict.fromkeys(connectorList)))
    #get connector names
    connectorNames = list(dict.fromkeys(connectorList))
    #convert it to markdown list
    listToMarkdown(connectorNames, connectorCol)

    def get_all_coillaborators_in_project(project):
        all_collaborators = []
        for model in project.models.items:
            versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
            for version in versions:
                all_collaborators.append(version.authorUser)
        return all_collaborators

    #Contributor Card 💳
    all_collaborators = get_all_coillaborators_in_project(project)
    contributorCol.metric(label = "Number of Contributors to Project", value= len(all_collaborators))
    #unique contributor names
    contributorNames = list(dict.fromkeys([col.name for col in all_collaborators]))
    #convert it to markdown list
    listToMarkdown(contributorNames,contributorCol)

    st.subheader("Graphs for Entire Project 📊")
    #COLUMNS FOR CHARTS
    model_graph_col, connector_graph_col, collaborator_graph_col = st.columns([2,1,1])

    #model GRAPH 📊
    #model count dataframe
    model_names = []
    version_counts = []
    for model in models:
        model_names.append(model.name)
        version_count = len(client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items)
        print(f'Model: {model.name} - Version count: {version_count}\n')
        version_counts.append(version_count)

    model_counts = pd.DataFrame([[model_name, version_count] for model_name, version_count in zip(model_names, version_counts)])

    #rename dataframe columns
    model_counts.columns = ["modelName", "totalCommits"]
    #create graph
    model_count_graph = px.bar(model_counts, x=model_counts.modelName, y=model_counts.totalCommits, color=model_counts.modelName, labels={"modelName":"","totalCommits":""})
    #update layout
    model_count_graph.update_layout(
        showlegend = False,
        margin = dict(l=1,r=1,t=1,b=1),
        height=220,
        paper_bgcolor='rgb(255, 255, 255)',  # Transparent background
        plot_bgcolor='rgb(255, 255, 255)',   # Transparent plot area
        font_family="Arial",
        font_color="black"
    )
    #show graph
    model_graph_col.plotly_chart(model_count_graph, use_container_width=True)

    #CONNECTOR CHART 🍩
    version_frame = pd.DataFrame.from_dict([c.dict() for c in all_versions_in_project])
    #get apps from commits
    apps = version_frame["sourceApplication"]
    #reset index
    apps = apps.value_counts().reset_index()
    #rename columns
    apps.columns=["app","count"]
    #donut chart
    fig = px.pie(apps, names=apps["app"],values=apps["count"], hole=0.5)
    #set dimensions of the chart
    fig.update_layout(
        showlegend=False,
        margin=dict(l=1, r=1, t=1, b=1),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    #set width of the chart so it uses column width
    connector_graph_col.plotly_chart(fig, use_container_width=True)

    #COLLABORATOR CHART 🍩
    #get authors from commits

    version_user_names = []
    for user in version_frame["authorUser"]:
        print(f'type: {type(user)}')
        print(f'user: {user.get('name')}\n')
        version_user_names.append(user.get('name'))

    authors = pd.DataFrame(version_user_names).value_counts().reset_index()
    #rename columns
    authors.columns=["author","count"]
    #create our chart
    authorFig = px.pie(authors, names=authors["author"], values=authors["count"],hole=0.5)
    authorFig.update_layout(
        showlegend=False,
        margin=dict(l=1,r=1,t=1,b=1),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',  # Add transparent background
        plot_bgcolor='rgba(0,0,0,0)',   # Add transparent plot background
        font_family="Roboto Mono",
        font_color="#2c3e50",
        yaxis_scaleanchor="x",
    )
    collaborator_graph_col.plotly_chart(authorFig, use_container_width=True)

    #COMMIT PANDAS TABLE 🔲
    st.subheader("Commit Activity Timeline 🕒")
    #created at parameter to dataframe with counts
    # print("VALUE")
    # print(pd.to_datetime(commits["createdAt"]).dt.date.value_counts().reset_index())

    timestamps = [version.createdAt.date() for version in all_versions_in_project]
    print(f'timestamps: {timestamps}\n')

    #convert to pandas dataframe and
    # rename the column of the timestamps frame to createdAt
    timestamps_frame = pd.DataFrame(timestamps, columns=["createdAt"]).value_counts().reset_index().sort_values("createdAt")

    print(f'timestamps_frame: {timestamps_frame}\n')

    cdate = timestamps_frame
    #rename columns
    cdate.columns = ["date", "count"]
    #redate indexed dates
    cdate["date"] = pd.to_datetime(cdate["date"]).dt.date

    print(f'cdate: {cdate}\n')

    #COMMIT ACTIVITY LINE CHART📈
    #line chart
    fig = px.line(cdate, x=cdate["date"], y=cdate["count"], markers =True)
    #recolor line
    fig.update_layout(
        showlegend=False,
        margin=dict(l=1,r=1,t=1,b=1),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',  # Add transparent background
        plot_bgcolor='rgba(0,0,0,0)',   # Add transparent plot background
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    fig.update_traces(line_color="red")

    #Show Chart
    st.plotly_chart(fig, use_container_width=True)

    #--------------------------

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
        residential_dashboard.run(metric_col1, metric_col2, selected_team)

    elif selected_team == "Service":
        service_dashboard.run(metric_col1, metric_col2, selected_team)
        
    elif selected_team == "Structure":
        structure_dashboard.run(metric_col1, metric_col2, selected_team)
    elif selected_team == "Industrial":
        industrial_dashboard.run(metric_col1, metric_col2, selected_team)

    elif selected_team == "Facade":
        facade_dashboard.run(metric_col1, metric_col2, selected_team)
print(f'selected_model: {selected_model}\n')
print(f'selected_version: {selected_version}\n')

# Get geometry data from the selected version

if show_attribute_extraction:
    with st.spinner("Getting geometry data..."):

        def get_geometry_data(selected_version, verbose=True):
            objHash = selected_version.referencedObject
            if verbose:
                print(f'objHash: {objHash}')
                print(f'Starting to receive data...\n')
            transport = ServerTransport(client=client, stream_id=project.id)
            base = operations.receive(objHash, transport)
            return base

        base = get_geometry_data(selected_version, verbose=True)
        print(f'base: {base}\n')

        def get_all_attributes(base_data: Base, flattened=False, depth=0, all_attributes=set()) -> set:
            # print(f'{"-" * depth}Getting attributes of {base}...')
            
            for key in base_data.__dict__:
                if depth < 2:
                    try:
                        print(f'depth: {depth} - Key: {key} - Type: {type(base.__dict__[key])}')
                    except Exception as e:
                        # print(f'Error: {e}')
                        pass
                # print(f'{"  " * depth}Key: {key} - Value: {base.__dict__[key]} - Type: {type(base.__dict__[key])}')
                all_attributes.add(key)

                if flattened: # If flattened is True, we need to recursively get all attributes of nested objects
                    if base_data.__getitem__(key) is not None:
                        try:
                            all_attributes = get_all_attributes(base_data.__getitem__(key)[0], flattened=True, depth=depth+1, all_attributes=all_attributes)
                        except Exception as e:
                            # print(f'Error: {e}')
                            pass
                            

            return all_attributes

        def search_for_attribute(base_data: Base, attribute: str, depth=0, single=True, found=False, output=[]): # single=True means we only want to find the first occurrence of the attribute, return all values of the attribute
            # print(f'{"  " * depth}Searching for attribute {attribute} in {base_data}...')

            for key in base_data.__dict__:
                # print(f'{"  " * depth}Key: {key} - Value: {base_data.__dict__[key]} - Type: {type(base_data.__dict__[key])}')
                if key == attribute:
                    found = True
                    output.append(base_data.__dict__[key])
                    if single:
                        break

                if base_data.__getitem__(key) is not None:
                    try:
                        found, output = search_for_attribute(base_data.__getitem__(key)[0], attribute, depth=depth+1, single=single, found=found, output=output)
                    except Exception as e:
                        # print(f'Error: {e}')
                        pass

            return found, output

        # all_attributes_unflattened = get_all_attributes(base)
        # print(f'all_attributes_unflattened: {all_attributes_unflattened}\n')

        base_data = base.__getitem__('@Data')
        print(f'base_data: {base_data}\n')

        keys = [key for key in dir(base_data) if not key.startswith('__')]
        print(f'keys: {keys}\n')


        # while '@Data' in dir(base_data):
        #     print(f'base_data: {base_data}')
        #     base_data = base_data.__getitem__('@Data')

        all_attributes_flattened = get_all_attributes(base_data, flattened=True)
        print(f'all_attributes_flattened: {all_attributes_flattened}\n')

        # Add a dropdown to select the attribute to search for
        selected_attribute = st.selectbox(
            label="Select attribute to search for",
            options=list(all_attributes_flattened),
            help="Select a specific attribute to search for in the base data"
        )

        # Add a toggle to search for a single or all occurrences of the attribute
        search_single = st.checkbox(
            label="Search for a single occurrence",
            value=True,
            help="Toggle to search for a single or all occurrences of the selected attribute"
        )

        # Check if a specific attribute exists in the base data
        attribute_to_search = selected_attribute
        attribute_found = search_for_attribute(base_data, attribute_to_search, single=search_single)
        print(f'Attribute {attribute_to_search} found: {attribute_found}\n')

        # Display the found attribute as a markdown table
        if attribute_found[0]:
            table_header = "| Attribute | Value |\n| --- | --- |\n"
            table_data = ""
            for i, value in enumerate(attribute_found[1]):
                table_data += f"| {attribute_to_search} | {value} |\n"
            st.markdown(table_header + table_data)
        else:
            st.error(f"Attribute {attribute_to_search} not found in the base data")
