#IMPORT LIBRARIES
#import streamlit
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
        background-color: #982062;
        font-family: 'Roboto Mono', sans-serif;  /* Apply font family to entire app */
    }
    
    /* Main container */
    .main {
        background-color: #ffa646;
        color: white;
        font-family: 'Roboto Mono', sans-serif;
    }
    
    /* Headers */
    .css-10trblm, .css-qrbaxs {
        color: #ffffff;
        font-weight: 600;
        font-family: 'Roboto Mono', sans-serif !important;  /* Added !important */
    }
    
    /* All text elements */
    .stMarkdown, .stText, div, span, p, h1, h2, h3 {
        font-family: 'Roboto Mono', sans-serif !important;
    }
    
    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        background-color: #2d2d2d;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cards and containers */
    div.css-12w0qpk.e1tzin5v2 {
        background-color: #2d2d2d;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Text color */
    .css-1dp5vir {
        color: white;
    }
    
    /* Buttons and selectbox */
    .stButton>button, .stSelectbox {
        background-color: #2d2d2d;
        color: white;
        border-radius: 0.3rem;
    }
    
    /* Markdown text */
    .css-183lzff {
        color: white;
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
speckleToken = tokenCol.text_input("Speckle token", "b623e9b4f9889139d00e1af4bf5a4a9de444fe792b", help="If you don't know how to get your token, take a look at this [link](<https://speckle.guide/dev/tokens.html>)👈")

#-------
#CLIENT
client = SpeckleClient(host=speckleServer)
#Get account from Token
account = get_account_from_token(speckleToken, speckleServer)
#Authenticate
client.authenticate_with_account(account)
#-------

#-------
#Streams List👇
streams = client.stream.list()
#print(streams)
#Get Stream Names
streamNames = [s.name for s in streams]
#Dropdown for stream selection
sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")

#SELECTED STREAM ✅
stream = client.stream.search(sName)[0]

#Stream Branches 🌴
branches = client.branch.list(stream.id)
#Stream Commits 🏹
commits = client.commit.list(stream.id, limit=100)
test = commits[0]

transport = ServerTransport(client=client, stream_id=stream.id)
res = operations.receive(test.referencedObject, transport)   

print("RESSS\n\n\n", res  )
print("RESSS\n\n\n", res.__dict__  )
# Add branch selection
selected_branch = st.selectbox(
    label="Select branch to analyze",
    options=[b.name for b in branches],
    help="Select a specific branch to analyze its data"
)

# Get commits for selected branch
branch_commits = [
    commit for commit in client.commit.list(stream.id, limit=100)
    if commit.branchName == selected_branch
]

# Add commit selection
selected_commit = st.selectbox(
    label="Select commit to view",
    options=[(f"{c.message} - {c.authorName} - {c.createdAt}") for c in branch_commits],
    help="Select a specific commit to analyze"
)
try:
    # Get the selected commit object
    selected_commit_obj = branch_commits[[
        (f"{c.message} - {c.authorName} - {c.createdAt}") for c in branch_commits
    ].index(selected_commit)]
except:
    pass

#--------------------------
#create a definition that generates an iframe from commit id
def commit2viewer(stream, commit, height=400) -> str:
    embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
    print(embed_src)  # Print the URL to verify correctness
    return st.components.v1.iframe(src=embed_src, height=height)

#--------------------------

#VIEWER👁‍🗨
with viewer:
    st.subheader("Latest Commit👇")
    commit2viewer(stream, commits[0])

with report:
    st.subheader("Statistics")

# Columns for Cards
branchCol, commitCol, connectorCol, contributorCol = st.columns(4)

#DEFINITIONS
#create a definition to convert your list to markdown
def listToMarkdown(list, column):
    list = ["- " + i +  "\n" for i in list]
    list = "".join(list)
    return column.markdown(list)

#Branch Card 💳
branchCol.metric(label = "Number of branches", value= stream.branches.totalCount)
#branch names as markdown list
branchNames = [b.name for b in branches]
listToMarkdown(branchNames, branchCol)

#Commit Card 💳
commitCol.metric(label = "Number of commits", value= len(commits))

#Connector Card 💳
#connector list
connectorList = [c.sourceApplication for c in commits]
#number of connectors
connectorCol.metric(label="Number of connectors", value= len(dict.fromkeys(connectorList)))
#get connector names
connectorNames = list(dict.fromkeys(connectorList))
#convert it to markdown list
listToMarkdown(connectorNames, connectorCol)

#Contributor Card 💳
contributorCol.metric(label = "Number of contributors", value= len(stream.collaborators))
#unique contributor names
contributorNames = list(dict.fromkeys([col.name for col in stream.collaborators]))
#convert it to markdown list
listToMarkdown(contributorNames,contributorCol)

with graphs:
    st.subheader("Graphs")
#COLUMNS FOR CHARTS
branch_graph_col, connector_graph_col, collaborator_graph_col = st.columns([2,1,1])

#BRANCH GRAPH 📊
#branch count dataframe
branch_counts = pd.DataFrame([[branch.name, branch.commits.totalCount] for branch in branches])
#rename dataframe columns
branch_counts.columns = ["branchName", "totalCommits"]
#create graph
branch_count_graph = px.bar(branch_counts, x=branch_counts.branchName, y=branch_counts.totalCommits, color=branch_counts.branchName, labels={"branchName":"","totalCommits":""})
#update layout
branch_count_graph.update_layout(
    showlegend = False,
    margin = dict(l=1,r=1,t=1,b=1),
    height=220,
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
    font_family="Arial",
    font_color="#2c3e50"
)
#show graph
branch_graph_col.plotly_chart(branch_count_graph, use_container_width=True)

#CONNECTOR CHART 🍩
commits= pd.DataFrame.from_dict([c.dict() for c in commits])
#get apps from commits
apps = commits["sourceApplication"]
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
authors = commits["authorName"].value_counts().reset_index()
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
print("VALUE")
print(pd.to_datetime(commits["createdAt"]).dt.date.value_counts().reset_index())
cdate = pd.to_datetime(commits["createdAt"]).dt.date.value_counts().reset_index().sort_values("createdAt")
#date range to fill null dates.
null_days = pd.date_range(start=cdate["createdAt"].min(), end=cdate["createdAt"].max())
#add null days to table
cdate = cdate.set_index("createdAt").reindex(null_days, fill_value=0)
#reset index
cdate = cdate.reset_index()
#rename columns
cdate.columns = ["date", "count"]
#redate indexed dates
cdate["date"] = pd.to_datetime(cdate["date"]).dt.date

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
# TEAM SPECIFIC METRICS
st.subheader("Team Specific Metrics 👥")

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
    structure_chart = px.bar(structure_data, x='Element', y='Percentage (%)')
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


