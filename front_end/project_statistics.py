import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pprint import pprint

from dashboards.dashboard import *

def create_network_graph(project_tree):
    print(f'create_network_graph(project_tree)')

    # with st.spinner("Creating network graph..."):
    G = nx.Graph() # Create a new graph

    for key, value in project_tree.items():
        print(f"Key: {key}, Value: {value}")
        
        if value["parent"] is not None:
            G.add_edge(key, value["parent"])

    # k = 1 / math.sqrt(len(G.nodes())) * 3 # optimal distance between nodes
    # pos = nx.spring_layout(G, k=k, seed=0)  # positions for all nodes

    pos = nx.kamada_kawai_layout(G)  # positions for all nodes

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(thickness=15, title='Distance From HyperA', xanchor='left', titleside='right'),
            line_width=2,
        ),
        textfont=dict(
            family='Arial',
            size=16,
            color='#000000'
        ),
        textposition='top center',
    )

    node_distances = []
    node_text = []
    for node in G.nodes():
        distance = 0
        current_node = node
        while project_tree[current_node]["parent"] is not None:
            distance += 1
            current_node = project_tree[current_node]["parent"]
        node_distances.append(distance)
        node_text.append(f'{node}')

    max_distance = max(node_distances)
    # Reverse the distances to get the distance from the root node
    node_distances = [max_distance - d for d in node_distances]

    node_trace.marker.color = node_distances
    node_trace.marker.line.color = 'rgb(0, 0, 0)'
    node_trace.text = node_text

    marker_sizes = [10 + 20 * (d / max_distance) for d in node_distances] # Marker size based on distance, larger for nodes closer to the root
    node_trace.marker.size = marker_sizes

    text_sizes = [5 + 10 * (d / max_distance) for d in node_distances] # Text size based on distance, smaller for nodes further away
    node_trace.textfont.size = text_sizes

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Speckle Model Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        height=800,  # Set the figure height here
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    )
                    )
        
    st.plotly_chart(fig, use_container_width=True)

    return None


def get_project_data(models, client, project_id):
    print(f'get_project_data(models, client, project_id)')

    # Create a dictionary to store the project data
    project_data = {}
    project_tree = {}
        
    # Get the versions of all models in the project
    for model in models:
        print(f'model: {model.name}')
        id = model.id
        long_name = model.name
        short_name = model.name.split("/")[-1]
        parent = model.name.split("/")[-2]
        versions = client.version.get_versions(model_id=model.id, project_id=project_id, limit=100).items
        # Get the number of versions
        version_count = len(versions)

        # print(f'id: {id}, long_name: {long_name}, short_name: {short_name}, parent: {parent}, version_count: {version_count}') 

        # print(long_name.split('/'))

        for index, node_name in enumerate(long_name.split('/')):
            # print(f'node_name: {node_name}, index: {index}')
            if index == 0:
                parent = None
            else:
                parent = long_name.split('/')[index - 1]

            # Add the node to the project tree
            if node_name not in project_tree:
                project_tree[node_name] = {
                    "parent": parent,
                    "children": []
                }
            
            # Add the child node to the parent node
            if parent is not None and parent in project_tree:
                project_tree[parent]["children"].append(node_name)
            else:
                project_tree[parent] = {
                    "parent": None,
                    "children": [node_name]
                }


    return project_tree

def build_network_diagram(models):
    pass

def create_test_tree():
    test_project_tree = {}

    test_project_tree['project'] = {
        "parent": None,
        "children": ['team_0', 'team_1', 'team_2']
    }
    test_project_tree['team_0'] = {
        "parent": 'project',
        "children": ['model_0', 'model_1']
    }
    test_project_tree['team_1'] = {
        "parent": 'project',
        "children": ['model_2']
    }
    test_project_tree['team_2'] = {
        "parent": 'project',
        "children": ['model_3']
    }
    test_project_tree['model_0'] = {
        "parent": 'team_0',
        "children": []
    }
    test_project_tree['model_1'] = {
        "parent": 'team_0',
        "children": []
    }
    test_project_tree['model_2'] = {
        "parent": 'team_1',
        "children": []
    }
    test_project_tree['model_3'] = {
        "parent": 'team_2',
        "children": []
    }

    return test_project_tree

def run():
    # Setup speckle connection
    models, client, project_id = setup_speckle_connection()

    # Get the project data
    project_tree = get_project_data(models, client, project_id)
    # Create the network diagram
    # project_tree = create_test_tree() # for testing
    network_diagram = create_network_graph(project_tree)
    # Display the network diagram
    # st.plotly_chart(network_diagram, use_container_width=True)

def show(container, client, project, models, versions, verbose=False):
    with container:
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
        # listToMarkdown(modelNames, modelCol)

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
        #unique contributor names
        contributorNames = list(dict.fromkeys([col.name for col in all_collaborators]))
        contributorCol.metric(label = "Number of Contributors to Project", value= len(contributorNames))
        #convert it to markdown list
        listToMarkdown(contributorNames,contributorCol)

        #COLUMNS FOR CHARTS
        connector_graph_col, collaborator_graph_col = st.columns([1,1])

        #model GRAPH 📊
        #model count dataframe
        model_names = []
        version_counts = []
        for model in models:
            model_names.append(model.name)
            version_count = len(client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items)
            # print(f'Model: {model.name} - Version count: {version_count}\n')
            version_counts.append(version_count)

        model_counts = pd.DataFrame([[model_name, version_count] for model_name, version_count in zip(model_names, version_counts)])

        # Create a new row for the pie charts
        pie_col1, pie_col2 = st.columns(2)

        # CONNECTOR CHART 🍩
        with pie_col1:
            st.subheader("Connector Chart")
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

        # COLLABORATOR CHART 🍩
        with pie_col2:
            st.subheader("Collaborator Chart")
            #get authors from commits
            version_user_names = []
            for user in version_frame["authorUser"]:
                # # print(f'type: {type(user)}')
                # # print(f'user: {user.get('name')}\n')
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

        st.markdown("---")

        #COMMIT PANDAS TABLE 🔲
        st.subheader("Commit Activity Timeline 🕒")
        #created at parameter to dataframe with counts
        # # print("VALUE")
        # # print(pd.to_datetime(commits["createdAt"]).dt.date.value_counts().reset_index())

        timestamps = [version.createdAt.date() for version in all_versions_in_project]
        # print(f'timestamps: {timestamps}\n')

        #convert to pandas dataframe and
        # rename the column of the timestamps frame to createdAt
        timestamps_frame = pd.DataFrame(timestamps, columns=["createdAt"]).value_counts().reset_index().sort_values("createdAt")

        # print(f'timestamps_frame: {timestamps_frame}\n')

        cdate = timestamps_frame
        #rename columns
        cdate.columns = ["date", "count"]
        #redate indexed dates
        cdate["date"] = pd.to_datetime(cdate["date"]).dt.date

        # print(f'cdate: {cdate}\n')

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
