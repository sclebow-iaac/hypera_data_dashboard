#IMPORT LIBRARIES
#import streamlit
import json
import streamlit as st
#specklepy libraries
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.transports.server import ServerTransport

#import pandas
import pandas as pd
#import plotly express
import plotly.express as px

# import os
import os

from typing import Dict, Any
from specklepy.objects.base import Base

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

PROJECTS_FILE = "projects.json"

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
    
    # # Center the image
    # col1, col2, col3 = st.columns([1,2,1])
    # with col2:
    #     st.image(
    #         r"E:\IAAC term 2\Layer 3.png",
    #         caption="building visualization",
    #         width=400
    #     )
#About info
    with header.expander("Hyper Building A🔽", expanded=True):
        st.markdown(
        """We use this space to record collaborators, commits, and timelines, to collect project data in a cohesive, accessible format.
"""
)
#--------------------------

with input:
    st.subheader("Inputs")

#-------
    #Columns for inputs
    serverCol, tokenCol = st.columns([1,3])
#-------


#-------
#User Input boxes
speckleServer = serverCol.text_input("Server URL", "macad.speckle.xyz", help="Speckle server to connect.")
speckleToken = tokenCol.text_input("Speckle token", "", help="If you don't know how to get your token, take a look at this [link](<https://speckle.guide/dev/tokens.html>)👈")

#-------
#CLIENT
client = SpeckleClient(host=speckleServer)
#Get account from Token
account = get_account_from_token(speckleToken, speckleServer)
#Authenticate
client.authenticate_with_account(account)
#-------

# Get projects
project = client.project.get(project_id="31f8cca4e0")
print(f'Project: {project.name}')

# Get models
project = client.project.get_with_models(project_id="31f8cca4e0", models_limit=100)

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

# #Stream Branches 🌴
# branches = client.branch.list(stream.id)
# #Stream Commits 🏹
# commits = client.commit.list(stream.id, limit=100)        
        
# # Add branch selection
# selected_branch = st.selectbox(
#     label="Select branch to analyze",
#     options=[b.name for b in branches],
#     help="Select a specific branch to analyze its data"
# )

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

def extract_data_dynamically(data):
    # adapt to different data structures
    extracted_info = {}

    try:
    # Get all base properties
        if hasattr(data, 'data'):
            base_props = data.data
            for prop_name, prop_value in base_props.items():
                extracted_info[prop_name] = prop_value
                print(f"Property: {prop_name} = {prop_value}")
        
        # Get displayValue if it exists (contains geometry info)
        if hasattr(data, 'displayValue'):
            display_props = data.displayValue
            extracted_info['displayValue'] = display_props
            print("Display properties:", display_props)
            
    # Get units if present
        if hasattr(data, 'units'):
            extracted_info['units'] = data.units
            
    # Get totalChildrenCount if present
        if hasattr(data, 'totalChildrenCount'):
            extracted_info['totalChildrenCount'] = data.totalChildrenCount
            
    except Exception as e:
        print(f"Error extracting properties: {e}")
        print("Data structure:", dir(data))
    
    return extracted_info

def get_object_parameters(obj: Base) -> Dict[str, Any]:
    try:
        parameters_data = obj["parameters"]
        parameters = parameters_data.get_dynamic_member_names()

        result_dict: Dict[str, Any] = {
            parameters_data[parameter]["name"]: parameters_data[parameter]["value"]
            for parameter in parameters
        }
        return result_dict
    except Exception as e:
        print(f"Error getting parameters: {e}")
        return {}

def get_object_data(stream_id: str, object_id: str) -> Dict[str, Any]:
    try:
        transport = ServerTransport(client=client, stream_id=stream_id)
        original_object: Any = operations.receive(
            obj_id=object_id, remote_transport=transport
        )
        result_dict: Dict[str, Any] = {}

        if hasattr(original_object, 'speckle_type') and (
            original_object.speckle_type
            == "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
        ):
            definition_object: Any = original_object["definition"]
        else:
            definition_object: Any = original_object

        if hasattr(definition_object, 'type'):
            result_dict["type"] = definition_object.type
        if hasattr(definition_object, 'family'):
            result_dict["family"] = definition_object.family
            
        result_dict.update(get_object_parameters(definition_object))
        return result_dict
    except Exception as e:
        print(f"Error getting object data: {e}")
        return {}

# if commits:
#     latest_commit = commits[-1]
#     print("SOURCEAPPLICATION", commits[0].sourceApplication)
    
#     object_data = get_object_data(stream.id, latest_commit.referencedObject)
#     if object_data:
#         print("Object Data received:", object_data)
        
#         object_df = pd.DataFrame([object_data])
#         print("DataFrame created:", object_df)
        
#         st.subheader("Object Data")
#         st.dataframe(object_df)
        
#         parameters_df = pd.DataFrame([{
#             'Parameter': key,
#             'Value': value
#         } for key, value in object_data.items() 
#         if key not in ['type', 'family']])
        
#         st.subheader("Parameters")
#         st.dataframe(parameters_df)
# else:
#     st.warning("No commits found for this stream.")

# Get commits for selected branch
# branch_commits = [
#     commit for commit in client.commit.list(stream.id, limit=100)
#     if commit.branchName == selected_branch
# ]

if st.button("Fetch Data"):
    specific_object_id = "22cf45139a693bae7cb1a71d54b80c98"
    
    transport = ServerTransport(client=client, stream_id=selected_model.id)
    try:
        specific_obj = operations.receive(specific_object_id, transport)
        
        def collect_object_data(obj, prefix=""):
            data = []
            
            # Get all attributes
            for attr in dir(obj):
                if not attr.startswith('_'):  # Skip private attributes
                    try:
                        value = getattr(obj, attr)
                        # Skip methods, only include data
                        if not callable(value):
                            data.append({
                                'Object': prefix,
                                'Property': attr,
                                'Value': str(value),
                                'Type': type(value).__name__
                            })
                            
                            # Recursively process nested objects
                            if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
                                nested_data = collect_object_data(value, f"{prefix}.{attr}")
                                data.extend(nested_data)
                    except:
                        continue
            
            return data

        # Collect all data
        all_data = collect_object_data(specific_obj, "root")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Display as table
        st.write("All Object Properties:")
        st.dataframe(df)
        
        # Optional: Save to CSV
        df.to_csv("speckle_object_data.csv", index=False)
        
    except Exception as e:
        st.error(f"Error processing object: {e}")

def process_all_projects():
    try:
        projects = load_project_urls()
        all_project_data = []

        for project in projects:
            try:
                print(f"Processing project: {project['name']} ({project['url']})")
                extracted_info = get_speckle_data(project['url'])
                # extracted_info = extract_data_dynamically(data)
                all_project_data.append({"name": project['name'], "data": [extracted_info]})
            except Exception as e:
                st.warning(f"Error processing project {project['name']}: {str(e)}")
            continue 

        return all_project_data
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        return []

def get_speckle_data(url):
    parts = url.split("/")
    stream_id = parts[-3]
    commit_id = parts[-1]
    return dict({"stream_id": stream_id, "commit_id": commit_id})

#--------------------------
#create a definition that generates an iframe from commit id
def commit2viewer(stream, commit, height=400) -> str:
    embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
    print(embed_src)  # Print the URL to verify correctness
    return st.components.v1.iframe(src=embed_src, height=height)

# <iframe title="Speckle" src="https://macad.speckle.xyz/projects/31f8cca4e0/models/e2578d4a64@671a67a8c1#embed=%7B%22isEnabled%22%3Atrue%2C%22hideControls%22%3Atrue%7D" width="600" height="400" frameborder="0"></iframe>
# #--------------------------
# #create a definition that generates an iframe from commit id
# def commit2viewer(stream, commit, height=400) -> str:
#     embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
#     # print(embed_src)  # Print the URL to verify correctness
#     return st.components.v1.iframe(src=embed_src, height=height)

# #--------------------------

def load_project_urls():
    with open(PROJECTS_FILE, 'r') as file:
        return json.load(file)

#VIEWER👁‍🗨
with viewer:
    st.subheader("Selected Commit👇")
    version2viewer(project, selected_model, selected_version)

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
# cdate = pd.to_datetime(timestamps).dt.date.value_counts().reset_index().sort_values("createdAt")
# #date range to fill null dates.
# null_days = pd.date_range(start=cdate["createdAt"].min(), end=cdate["createdAt"].max())
# #add null days to table
# cdate = cdate.set_index("createdAt").reindex(null_days, fill_value=0)
# #reset index
# cdate = cdate.reset_index()
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
#create a definition that generates an iframe from commit id
def commit2viewer(stream, commit, height=400) -> str:
    embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
    print(embed_src)  # Print the URL to verify correctness
    return st.components.v1.iframe(src=embed_src, height=height)

#--------------------------

#data from speckle model

try:
    projects_data = process_all_projects()

    if projects_data:
        df = pd.json_normalize(projects_data, "data", ["name"])
        st.write("Project Data:")
        st.dataframe(df)
except Exception as e:
    st.error(f"Error processing projects: {str(e)}")


df.to_csv("extracted_data.csv", index=False)

st.dataframe(df)

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
    metric_col1.metric("Floor Count", "25")
    metric_col2.metric("Unit Types", "4")
    metric_col3.metric("Normalized Travel Time", "from formula")
    
    # Residential-specific chart
    residential_data = pd.DataFrame({
        'Unit Type': ['housing', 'social', 'retail', 'open space'],
        'Travel Time (min)': [40, 60, 30, 20]
    })
    res_chart = px.bar(residential_data, x='Unit Type', y='Travel Time (min)')
    res_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(res_chart, use_container_width=True)

elif selected_team == "Service":
    metric_col1.metric("Circulation Areas", "8")
    metric_col2.metric("Service Cores", "3")
    metric_col3.metric("Normalized Value", "from formula")
    
    # Service-specific chart
    service_data = pd.DataFrame({
        'System': ['Distance Efficiency', 'Vertical Circulation'],
        'Percentage (%)': [95, 90]
    })
    service_chart = px.bar(service_data, x='System', y='Percentage (%)')
    service_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(service_chart, use_container_width=True)

elif selected_team == "Structure":
    metric_col1.metric("Column Grid", "8m x 8m")
    metric_col2.metric("Core Walls", "6")
    metric_col3.metric("Noarmalized Floor Usage", "from formula")
    
    # Structure-specific chart
    structure_data = pd.DataFrame({
        'Element': ['Self-Energy Generation', 'Existing Energy Consumption'],
        'Percentage Efficiency (%)': [25, 90]
    })
    structure_chart = px.bar(structure_data, x='Element', y='Percentage Efficiency (%)')
    structure_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(structure_chart, use_container_width=True)

elif selected_team == "Industrial":
    metric_col1.metric("Production Areas", "4")
    metric_col2.metric("Storage Capacity", "2000m³")
    metric_col3.metric("Normalized Recycling Efficiency", "from formula")
    
    # Industrial-specific chart
    industrial_data = pd.DataFrame({
        'Values': ['Energy Production', 'Energy Storage'],
        'Efficiency (%)': [50, 50]
    })
    industrial_chart = px.bar(industrial_data, x='Values', y='Efficiency (%)')
    industrial_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(industrial_chart, use_container_width=True)


else: # Facade
    metric_col1.metric("Facade Area", "1000m²")
    metric_col2.metric("Facade Type", "Curtain Wall")
    metric_col3.metric("Normalized Value", "from formula")

    # Facade-specific chart
    facade_data = pd.DataFrame({
        'Values': ['Daylight Used', 'Incoming Daylight'],
        'Efficiency (%)': [50, 50]
    })
    facade_chart = px.pie(facade_data, names=facade_data["Values"], values=facade_data["Efficiency (%)"], hole=0.5)
    facade_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(facade_chart, use_container_width=True)
