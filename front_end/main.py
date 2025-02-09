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
        metric_col1.metric("Index of Mixed Use", "0.6")
        metric_col2.metric("Unit Types", "4")
        metric_col3.metric("Normalized Travel Time", "0.8 (hours)")

        number_of_units = [40, 60, 30, 20]  
        unit_types = ['Housing', 'Social', 'Commercial', 'Open Space']
        total_number_of_units = sum(number_of_units)

        # Compute the formula
        numerator = sum(
            units * (units - 1) for units in number_of_units
        )
        denominator = total_number_of_units * (total_number_of_units - 1)

        if denominator != 0:  # Avoid division by zero
            calculated_value = 1 - (numerator / denominator)
        else:
            calculated_value = None  # Handle division by zero case

        # Residential-specific chart
        residential_data = pd.DataFrame({
            'Unit Type': unit_types,
            'Number of Units': number_of_units
        })
        res_chart = px.bar(residential_data, x='Unit Type', y='Number of Units')
        res_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        st.plotly_chart(res_chart, use_container_width=True)

        st.markdown("""
        <h2 style='text-align: center, font-size: 24px;'>Mixed Use Index</h2>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the metric can be expressed as:
            
            $$ 
            1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}
            $$
        """, unsafe_allow_html=True)

        st.markdown("")

        # Display the computed value
        if calculated_value is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {calculated_value:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    elif selected_team == "Service":
        occupancy_efficiency = 80
        utilization_rate = 34
        n = 5
        active_hours = 12
        function_exchange_factor = 4
        total_available_hours_per_day = 13
        total_spaces_available = 50

        metric_col1.metric("Number of Spaces", n)

        metrics_data = {
            "Occupancy Efficiency": occupancy_efficiency,  # No units here for calculations
            "Utilization Rate": utilization_rate,  # No units here for calculations
            "Active Hours": active_hours,  # No units here for calculations
            "Function Exchange Factor": function_exchange_factor,  # No units here for calculations
            "Total Available Hours per Day": total_available_hours_per_day,  # No units here for calculations
            "Total Spaces Available": total_spaces_available  # No units here for calculations
        }

        # Create columns for metrics based on the number of metrics to display
        metric_cols = st.columns(len(metrics_data))  # Create a column for each metric

        for i, (metric_name, value) in enumerate(metrics_data.items()):
            col = metric_cols[i]  # Access the corresponding column

            # Display the metric with units in the name
            if metric_name == "Occupancy Efficiency":
                col.metric(metric_name, f"{value}%", help="Percentage of occupancy efficiency")
            elif metric_name == "Utilization Rate":
                col.metric(metric_name, f"{value}%", help="Percentage of utilization rate")
            elif metric_name == "Active Hours":
                col.metric(metric_name, f"{value} hours", help="Total active hours")
            elif metric_name == "Function Exchange Factor":
                col.metric(metric_name, f"{value}", help="Unitless function exchange factor")
            elif metric_name == "Total Available Hours per Day":
                col.metric(metric_name, f"{value} hours", help="Total available hours per day")
            elif metric_name == "Total Spaces Available":
                col.metric(metric_name, f"{value}", help="Total number of spaces available")

            # Ensure value is a valid number before conversion
            try:
                # Use the raw value for calculations
                raw_value = float(value)  # Convert to float for calculations
                if metric_name in ["Occupancy Efficiency", "Utilization Rate"]:
                    max_value = 100
                elif metric_name == "Active Hours":
                    max_value = 24
                elif metric_name == "Function Exchange Factor":
                    max_value = 10
                elif metric_name == "Total Available Hours per Day":
                    max_value = 24
                elif metric_name == "Total Spaces Available":
                    max_value = 100
                
                progress_bar = col.progress(raw_value / max_value)  # Use raw_value for progress bar
            except (ValueError, TypeError) as e:
                print(f"Error converting value for {metric_name}: {value}. Error: {e}")
                progress_bar = col.progress(0)  # Default to 0 if conversion fails

            col.markdown(f"""
            <div style="text-align: center; font-size: 24px;">
            {value} / {max_value}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")


        # Compute the formula
        numerator = utilization_rate * active_hours * function_exchange_factor # what kind of summation we need to do here
        denominator = total_available_hours_per_day * total_spaces_available

        if denominator != 0:  # Avoid division by zero
            calculated_value = numerator / denominator
        else:
            calculated_value = None  # Handle division by zero case

        st.markdown("")
        st.markdown("")

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the metric can be expressed as:
            
            $$ 
            \frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor)}{TotalAvailableHoursPerDay \cdot TotalSpacesAvailable}
            $$
        """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")
        if calculated_value is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Occupancy Efficiency: {calculated_value:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)


    elif selected_team == "Structure":

        #floor flexibility:column-free FAR
        # Define the variables for the new formula
        total_column_free_floor_area = 800  # Example value for total column-free floor area
        total_floor_area = 1000  # Example value for total floor area

        # Compute the formula
        if total_floor_area != 0:  # Avoid division by zero
            column_free_floor_area_ratio = total_column_free_floor_area / total_floor_area
        else:
            column_free_floor_area_ratio = None  # Handle division by zero case

        # Structure-specific chart

        st.markdown("<h2 style='text-align: center;'>Floor Flexibility: Column-Free FAR</h2>", unsafe_allow_html=True)
        structure_data = pd.DataFrame({
            'Number of Columns': [10],
            'Total Floor Area': [1000]
        })
        structure_chart = px.bar(structure_data, x='Number of Columns', y='Total Floor Area')
        structure_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        st.plotly_chart(structure_chart, use_container_width=True)

        # Add major text underneath the metrics
        st.markdown("<h2 style='text-align: center; font-size: 24px;'>Floor Flexibility: Column-Free Floor Area Ratio</h2>", unsafe_allow_html=True)

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the Column-Free Floor Area Ratio can be expressed as:
            
            $$ 
            \text{Column-Free Floor Area Ratio} = \frac{\text{Total Column-Free Floor Area (m²)}}{\text{Total Floor Area (m²)}}
            $$
        """, unsafe_allow_html=True)

        # Display the computed value
        if column_free_floor_area_ratio is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {column_free_floor_area_ratio:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        #structural efficiency: embodied carbon emissions per square meter
        # Define the variables for the new formula
        total_embodied_carbon_emissions = 800  
        usable_floor_area = 1000  

        # Compute the formula
        if usable_floor_area != 0:  # Avoid division by zero
            embodied_carbon_emissions_per_square_meter = total_embodied_carbon_emissions / usable_floor_area
        else:
            embodied_carbon_emissions_per_square_meter = None  # Handle division by zero case

        # Structure-specific chart

        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)
        structure_data = pd.DataFrame({
            'Total Embodied Carbon Emmissions': [10],
            'Floor Area': [1000]
        })
        structure_chart = px.bar(structure_data, x='Total Embodied Carbon Emmissions', y='Floor Area')
        structure_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        st.plotly_chart(structure_chart, use_container_width=True)

        # Add major text underneath the metrics
        st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the Embodied Carbon Emissions per Square Meter can be expressed as:
            
            $$ 
            \text{Embodied Carbon Emissions per Square Meter (kg/m²)} = \frac{\text{Total Embodied Carbon Emissions (kg)}}{\text{Usable Floor Area (m²)}}
            $$
        """, unsafe_allow_html=True)

        # Display the computed value
        if embodied_carbon_emissions_per_square_meter is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {embodied_carbon_emissions_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        #structural efficiency: load capacity per square meter
        # Define the variables for the new formula
        load_capacity = 800  
        self_weight_of_structure = 500  

        # Compute the formula
        if self_weight_of_structure != 0:  # Avoid division by zero
            load_capacity_per_square_meter = load_capacity / self_weight_of_structure
        else:
            load_capacity_per_square_meter = None  # Handle division by zero case

        # Structure-specific chart

        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
        structure_data = pd.DataFrame({
            'Load Capacity': [10],
            'Self Weight of Structure': [1000]
        })
        structure_chart = px.bar(structure_data, x='Load Capacity', y='Self Weight of Structure')
        structure_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        st.plotly_chart(structure_chart, use_container_width=True)

        # Add major text underneath the metrics
        st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the Load Capacity per Square Meter can be expressed as:
            
            $$ 
            \text{Load Capacity per Square Meter (kg/m²)} = \frac{\text{Load Capacity (kg)}}{\text{Self Weight of Structure (kg)}}
            $$
        """, unsafe_allow_html=True)

        # Display the computed value
        if load_capacity_per_square_meter is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {load_capacity_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        #structural efficiency: material efficiency ratio
        # Define the variables for the new formula
        theoretical_minimum_material_usage = 800  
        actual_material_usage = 500  

        # Compute the formula
        if actual_material_usage != 0:  # Avoid division by zero
            material_efficiency_ratio = theoretical_minimum_material_usage / actual_material_usage
        else:
            material_efficiency_ratio = None  # Handle division by zero case

        # Structure-specific chart

        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
        structure_data = pd.DataFrame({
            'Theoretical Minimum Material Usage': [10],
            'Actual Material Usage': [1000]
        })
        structure_chart = px.bar(structure_data, x='Theoretical Minimum Material Usage', y='Actual Material Usage')
        structure_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        st.plotly_chart(structure_chart, use_container_width=True)

        # Add major text underneath the metrics
        st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Material Efficiency Ratio</h2>", unsafe_allow_html=True)

        # Add the math formula
        st.markdown(r"""
            The formula for calculating the Material Efficiency Ratio can be expressed as:
            
            $$ 
            \text{Material Efficiency Ratio} = \frac{\text{Theoretical Minimum Material Usage (kg)}}{\text{Actual Material Usage (kg)}}
            $$
        """, unsafe_allow_html=True)

        # Display the computed value
        if material_efficiency_ratio is not None:
            st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {material_efficiency_ratio:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    elif selected_team == "Industrial":
        # Define the variables for the new formula
        energy_generation = [800, 850, 900, 950]  # Example values over time
        energy_demand = [500, 600, 700, 800]  # Example values over time

        # Compute the energy self-sufficiency ratio for each time point
        energy_self_sufficiency_ratios = [
            gen / demand if demand != 0 else None
            for gen, demand in zip(energy_generation, energy_demand)
        ]

        # Create a DataFrame for the line chart
        time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
        line_data = pd.DataFrame({
            'Time': time_points,
            'Energy Generation': energy_generation,
            'Energy Demand': energy_demand,
            'Energy Self-Sufficiency Ratio': energy_self_sufficiency_ratios
        })

        # Create a line chart
        line_chart = px.line(line_data, x='Time', y=['Energy Generation', 'Energy Demand', 'Energy Self-Sufficiency Ratio'],
                              labels={'value': 'Energy (kWh)', 'variable': 'Metrics'},
                              title='Energy Metrics Over Time')
        line_chart.update_layout(
            title_x=0.5,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(line_chart, use_container_width=True)

        # Display the last calculated value for energy self-sufficiency ratio
        if energy_self_sufficiency_ratios[-1] is not None:
            st.markdown(f"<h3 style='text-align: center;'>Latest Energy Self-Sufficiency Ratio: {energy_self_sufficiency_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        # Define the variables for the new formula
        food_production = [800, 850, 900, 950]  # Example values over time
        food_demand = [500, 600, 700, 800]  # Example values over time

        # Compute the food self-sufficiency ratio for each time point
        food_self_sufficiency_ratios = [
            gen / demand if demand != 0 else None
            for gen, demand in zip(food_production, food_demand)
        ]

        # Create a DataFrame for the line chart
        time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
        line_data = pd.DataFrame({
            'Time': time_points,
            'Food Production': food_production,
            'Food Demand': food_demand,
            'Food Self-Sufficiency Ratio': food_self_sufficiency_ratios
        })

        # Create a line chart
        line_chart = px.line(line_data, x='Time', y=['Food Production', 'Food Demand', 'Food Self-Sufficiency Ratio'],
                              labels={'value': 'Food (kg)', 'variable': 'Metrics'},
                              title='Food Metrics Over Time')
        line_chart.update_layout(
            title_x=0.5,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(line_chart, use_container_width=True)

        # Display the last calculated value for food self-sufficiency ratio
        if food_self_sufficiency_ratios[-1] is not None:
            st.markdown(f"<h3 style='text-align: center;'>Latest Food Self-Sufficiency Ratio: {food_self_sufficiency_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        # Define the variables for the new formula
        recycled_water = [800, 850, 900, 950]  # Example values over time
        wastewater_production = [500, 600, 700, 800]  # Example values over time

        # Compute the recycled water ratio for each time point
        recycled_water_ratios = [
            gen / demand if demand != 0 else None
            for gen, demand in zip(recycled_water, wastewater_production)
        ]

        # Create a DataFrame for the line chart
        time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
        line_data = pd.DataFrame({
            'Time': time_points,
            'Recycled Water': recycled_water,
            'Wastewater Production': wastewater_production,
            'Recycled Water Ratio': recycled_water_ratios
        })

        # Create a line chart
        line_chart = px.line(line_data, x='Time', y=['Recycled Water', 'Wastewater Production', 'Recycled Water Ratio'],
                              labels={'value': 'Recycled Water (m³)', 'variable': 'Metrics'},
                              title='Recycled Water Metrics Over Time')
        line_chart.update_layout(
            title_x=0.5,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(line_chart, use_container_width=True)

        # Display the last calculated value for recycled water ratio
        if recycled_water_ratios[-1] is not None:
            st.markdown(f"<h3 style='text-align: center;'>Latest Recycled Water Ratio: {recycled_water_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")

        # Define the variables for the new formula
        recycled_solid_waste = [800, 850, 900, 950]  # Example values over time
        solid_waste_production = [500, 600, 700, 800]  # Example values over time

        # Compute the solid waste utilization ratio for each time point
        solid_waste_utilization_ratios = [
            gen / demand if demand != 0 else None
            for gen, demand in zip(recycled_solid_waste, solid_waste_production)
        ]

        # Create a DataFrame for the line chart
        time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
        line_data = pd.DataFrame({
            'Time': time_points,
            'Recycled Solid Waste': recycled_solid_waste,
            'Solid Waste Production': solid_waste_production,
            'Solid Waste Utilization Ratio': solid_waste_utilization_ratios
        })

        # Create a line chart
        line_chart = px.line(line_data, x='Time', y=['Recycled Solid Waste', 'Solid Waste Production', 'Solid Waste Utilization Ratio'],
                              labels={'value': 'Recycled Solid Waste (kg)', 'variable': 'Metrics'},
                              title='Solid Waste Utilization Metrics Over Time')
        line_chart.update_layout(
            title_x=0.5,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(line_chart, use_container_width=True)

        # Display the last calculated value for solid waste utilization ratio
        if solid_waste_utilization_ratios[-1] is not None:
            st.markdown(f"<h3 style='text-align: center;'>Latest Solid Waste Utilization Ratio: {solid_waste_utilization_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("")


    elif selected_team == "Facade":
        # Define the variables for daylight in different parts of the building
        time_of_day = ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM']  # Example time points
        daylight_amounts = {
            'North Side': [50, 70, 90, 60, 30],  # Example daylight amounts for the North side
            'South Side': [30, 50, 80, 100, 70],  # Example daylight amounts for the South side
            'East Side': [60, 80, 100, 90, 40],  # Example daylight amounts for the East side
            'West Side': [40, 60, 70, 80, 50]    # Example daylight amounts for the West side
        }

        # Total incoming daylight (example value)
        total_incoming_daylight = 400  # Example total incoming daylight value

        # Create a DataFrame for the line chart
        daylight_data = pd.DataFrame(daylight_amounts, index=time_of_day)

        # Calculate the total daylight amount used
        total_daylight_used = daylight_data.sum().sum()  # Sum of all daylight amounts used

        # Compute the ratio of daylight amount used to total incoming daylight
        daylight_ratio = total_daylight_used / total_incoming_daylight if total_incoming_daylight != 0 else None

        # Create a line chart
        daylight_chart = px.line(daylight_data, 
                                  title='Daylight Amount in Different Parts of the Building',
                                  labels={'value': 'Daylight Amount (lux)', 'variable': 'Building Side'},
                                  markers=True)
        daylight_chart.update_layout(
            title_x=0.35,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(daylight_chart, use_container_width=True)

        # Display the daylight ratio metric
        if daylight_ratio is not None:
            st.markdown(f"<h3 style='text-align: center;'>Daylight Utilization Ratio: {daylight_ratio:.2f}</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

        # Optionally, display a summary of the daylight amounts
        st.markdown("<h3 style='text-align: center;'>Daylight Amounts Summary</h3>", unsafe_allow_html=True)
        st.write(daylight_data)

        st.markdown("")
        st.markdown("")
        

        # Define the angles and their corresponding effectiveness for each panel
        angles = [0, 15, 30, 45, 60, 75, 90]  # Example angles in degrees
        effectiveness = [0.1, 0.5, 0.8, 1.0, 0.7, 0.4, 0.2]  # Example effectiveness values

        # Create a DataFrame for the line chart
        angle_data = pd.DataFrame({
            'Angle (degrees)': angles,
            'Effectiveness': effectiveness
        })

        # Compute the optimal angle (e.g., the angle with the highest effectiveness)
        optimal_angle = angles[effectiveness.index(max(effectiveness))]

        # Create a line chart
        angle_chart = px.line(angle_data, 
                               x='Angle (degrees)', 
                               y='Effectiveness', 
                               title='Effectiveness of Panel Angles',
                               markers=True)
        angle_chart.update_layout(
            title_x=0.5,  # Center the title
            paper_bgcolor='rgba(0,0,0,0)',  # Set paper background to transparent
            plot_bgcolor='rgba(0,0,0,0)',   # Set plot background to transparent
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )

        # Display the line chart
        st.plotly_chart(angle_chart, use_container_width=True)

        # Display the optimal angle metric
        st.markdown(f"<h3 style='text-align: center;'>Optimal Angle for Panel Movement: {optimal_angle}°</h3>", unsafe_allow_html=True)

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
