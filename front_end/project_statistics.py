import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pprint import pprint
from streamlit_plotly_events import plotly_events

from dashboards.dashboard import *

def create_network_graph(project_tree):
    # print(f'create_network_graph(project_tree)')

    # Create a subheader for the network diagram
    st.subheader("Project Network Diagram")

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
    edge_pairs = []  # Store edge pairs for highlighting
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        edge_pairs.append((edge[0], edge[1]))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    node_names = []  # Store node names for clickData reference
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_names.append(node)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='ice',
            size=10,
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

    marker_sizes = [10 + 30 * (d / max_distance) for d in node_distances] # Marker size based on distance, larger for nodes closer to the root
    node_trace.marker.size = marker_sizes

    text_sizes = [8 + 10 * (d / max_distance) for d in node_distances] # Text size based on distance, smaller for nodes further away
    node_trace.textfont.size = text_sizes

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        height=800,  # Set the figure height here
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        clickmode='event+select'  # Enable click events
                    )
                    )
    
    # # Display the chart and capture click events
    # chart = st.plotly_chart(fig, use_container_width=True, key="network_chart")
    
    # Add expander for click instructions
    with st.expander("How to use the network diagram"):
        st.markdown("""
        - Click on any node to highlight it and all its parent nodes
        - The highlighted path shows the connection from the selected node to the root
        - Each click will update the highlighted path
        """)
    
    # Create a container for the highlighted path information
    highlight_container = st.empty()
    
    # Initialize session state for highlighted node if not exists
    if 'highlighted_node' not in st.session_state:
        st.session_state.highlighted_node = None
    
    # Create a container for the chart that we'll reuse
    chart_container = st.container()
    
    selected_model_name = None
    selected_node_children = set()  # Using a set instead of a list

    # Function to recursively get all children
    def get_all_children(node, parent_path="", visited=None):
        if visited is None:
            visited = set()
        
        # Protect against circular references
        if node in visited:
            return []
        
        visited.add(node)
        results = []
        
        if node in project_tree and "children" in project_tree[node]:
            current_path = f"{parent_path}/{node}" if parent_path else node
            
            # If this node has no children, it's a leaf node
            if not project_tree[node]["children"]:
                return [current_path]
                
            # Otherwise, get children of each child
            for child in project_tree[node]["children"]:
                child_results = get_all_children(child, current_path, visited)
                results.extend(child_results)
                
        return results

    # Check if there's a highlighted node from previous interaction
    if st.session_state.highlighted_node and st.session_state.highlighted_node in project_tree:
        # Get the selected node from session state
        selected_node = st.session_state.highlighted_node
        
        # Generate highlighted path
        path_nodes = []
        current = selected_node
        while current is not None:
            path_nodes.append(current)
            current = project_tree[current]["parent"]
        
        selected_model_name = '/'.join(reversed(path_nodes))
        
        # Get all descendants of the selected node
        if "children" in project_tree[selected_node]:
            direct_children = project_tree[selected_node]["children"]
            
            # Get recursive children for each direct child
            for child in direct_children:
                child_paths = get_all_children(child, "", None)
                # Use update instead of extend for sets
                selected_node_children.update(child_paths)
        
        # Update the info display
        highlight_container.markdown(f"""
        **Selected Model**  
        {selected_model_name}
        
        """)
        
        # Create highlighted path elements
        highlighted_edge_x = []
        highlighted_edge_y = []
        
        # Generate edges for the path
        for i in range(len(path_nodes)-1):
            child = path_nodes[i]
            parent = path_nodes[i+1]
            
            x0, y0 = pos[child]
            x1, y1 = pos[parent]
            highlighted_edge_x.extend([x0, x1, None])
            highlighted_edge_y.extend([y0, y1, None])
        
        # Create highlighted edge trace
        highlighted_edge_trace = go.Scatter(
            x=highlighted_edge_x,
            y=highlighted_edge_y,
            line=dict(width=3, color='red'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create highlighted node trace
        highlighted_node_x = [pos[node][0] for node in path_nodes]
        highlighted_node_y = [pos[node][1] for node in path_nodes]
        
        highlighted_node_trace = go.Scatter(
            x=highlighted_node_x,
            y=highlighted_node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='red',
                size=15,
                line=dict(width=2, color='darkred')
            ),
            text=path_nodes
        )
        
        # Create a new figure with the original data plus highlighted elements
        display_fig = go.Figure(data=[edge_trace, node_trace, highlighted_edge_trace, highlighted_node_trace],
                        layout=fig.layout)
    else:
        # Use the original figure if no highlights
        display_fig = fig
    
    # Use Streamlit's native click detection on the displayed figure
    with chart_container:
        selected_points = plotly_events(display_fig, click_event=True, override_height=800)
    
    # Process any new clicks
    if selected_points:
        # Get the point index from the selected point
        point_index = selected_points[0]["pointIndex"]
        
        if point_index is not None and point_index < len(node_names):
            # Update session state with the newly selected node
            st.session_state.highlighted_node = node_names[point_index]
            # Force a rerun to display the updated chart
            st.rerun()
    
    selected_node_children = list(selected_node_children)

    # Append the selected model name to the names in the list of children
    for i in range(len(selected_node_children)):
        selected_node_children[i] = f"{selected_model_name}/{selected_node_children[i]}"

    return selected_model_name, selected_node_children

@st.cache_data
def get_project_data():
    print(f'get_project_data(models, client, project_id)')
    
    models, client, project_id = setup_speckle_connection()

    # Create a dictionary to store the project data
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

        version_data = {}

        for version in versions:
            version_data[version.id] = {
                "createdAt": version.createdAt,
                "authorUser": version.authorUser,
                "sourceApplication": version.sourceApplication,
            }

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
                    "children": [],
                    "id": id,
                    "version_count": version_count,
                    "version_data": version_data,
                    "long_name": long_name,
                    "short_name": short_name,
                }
            
            # Add the child node to the parent node
            if parent is not None and parent in project_tree:
                project_tree[parent]["children"].append(node_name)
            else:
                project_tree[parent] = {
                    "parent": None,
                    "children": [node_name],
                    "id": id,
                    "version_count": version_count,
                    "version_data": version_data,
                    "long_name": long_name,
                    "short_name": short_name,
                }


    return project_tree, project_id

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

def run(container=None):
    # Get the project data
    project_tree, project_id = get_project_data()

    left_margin, content_container, right_margin = get_content_container_columns()
    with content_container:
        if container is None:
            container = st.container()

        with container:
            # Create tabs for the dashboard
            model_inspector_tab, overall_statistics_tab = st.tabs(["Model Inspector", "Overall Project Statistics"])

            with model_inspector_tab:

                # Create the network diagram
                selected_model_name, selected_node_children = create_network_graph(project_tree)

                if selected_model_name is None:
                    st.write("No model selected.")
                else:
                    # cleaned_node_children = []
                    # # Remove selected_model_name that are not in the project tree long names
                    # all_long_names = [value["long_name"] for value in project_tree.values()]
                    # for name in selected_node_children:
                    #     if name in all_long_names:
                    #         cleaned_node_children.append(name)
                    # selected_node_children = cleaned_node_children

                    # cleaned_node_children = []
                    # # Remove any selected_node_children that have no versions
                    # for name in selected_node_children:
                    #     # Get the project tree entry for the long name
                    #     for key, value in project_tree.items():
                    #         if value["long_name"] == name:
                    #             # Check if the version count is greater than 0
                    #             if value["version_count"] > 0:
                    #                 cleaned_node_children.append(name)
                    #             break
                    # selected_node_children = cleaned_node_children

                    selected_analysis_mode = 'Analyze all Child Models Combined'
                    default_analysis_index = 1
                    if len(selected_node_children) > 0:
                        st.write(f'There are {len(selected_node_children)} child models of {selected_model_name}')
                        # Add a radio button to select a Child Model or View a Combined Model of all children
                        selected_analysis_mode = st.radio(
                            "Select Analysis Mode",
                            ("Analyze a Single Child Model", 
                            "Analyze all Child Models Combined"),
                            index=default_analysis_index
                        )

                    if selected_analysis_mode == "Analyze a Single Child Model":
                        # Create a dropdown to select a model from the children
                        selected_child_name = st.selectbox(f'**Select a child model to analyze, there is/are {len(selected_node_children)}**', selected_node_children)
                        selected_model_name = selected_child_name

                        # Get the model ID from the selected model name
                        # Check the long name of the model
                        selected_model_id = None
                        version_data = None
                        for key, value in project_tree.items():
                            if value["long_name"] == selected_model_name:
                                selected_model_id = value["id"]
                                version_data = value["version_data"]
                                break

                        # Create a dropdown to select a version from the selected model
                        selected_version_id = st.selectbox(f"Select a version, there is/are {len(version_data)}", list(version_data.keys()), format_func=lambda x: version_data[x]["createdAt"])
                        
                        # Create two columns for the speckle viewer and the version data
                        viewer_col, version_data_col = st.columns([1, 1])
                        with viewer_col:
                            # Create a Speckle Viewer
                            st.subheader("Speckle Viewer")
                            speckle_model_id = selected_model_id + '@' + selected_version_id
                            display_speckle_viewer(container=viewer_col, project_id=project_id, model_id=speckle_model_id, header_text='Selected Model')

                        with version_data_col:
                            # Display the version data
                            st.subheader("Version Data")

                            creator = version_data[selected_version_id]["authorUser"]
                            created_at = version_data[selected_version_id]["createdAt"]
                            source_application = version_data[selected_version_id]["sourceApplication"]
                            st.markdown(f"**Created By:** {creator.name}")
                            st.markdown(f"**Created At:** {created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                            st.markdown(f"**Source Application:** {source_application}")

                        st.header("Selected Model Data:")
                        # Create a dataframe from the version data
                        version_data_df = pd.DataFrame.from_dict(version_data, orient='index')
                        # Convert the createdAt column to datetime
                        version_data_df['createdAt'] = pd.to_datetime(version_data_df['createdAt'])
                        # Sort the dataframe by createdAt
                        version_data_df = version_data_df.sort_values(by='createdAt')

                        # Add timeline for single model versions
                        st.subheader(f'Timeline for {len(version_data)} version(s)')
                        
                        # Prepare data for timeline
                        timeline_df = version_data_df.copy()
                        timeline_df['author_name'] = timeline_df['authorUser'].apply(lambda x: x.name)
                        
                        # Calculate appropriate height based on number of versions
                        height = max(30 * len(version_data), 200)
                        
                        # Create a timeline showing version commits
                        fig = px.scatter(timeline_df, 
                                        x='createdAt', 
                                        y=[selected_model_name.split('/')[-1]] * len(timeline_df),
                                        color='sourceApplication',
                                        hover_data=['sourceApplication', 'author_name'],
                                        labels={'createdAt': 'Date', 'y': 'Model', 'author_name': 'Author'},
                                        height=height)
                        
                        # Add connecting lines to visualize sequence
                        fig.add_trace(go.Scatter(
                            x=timeline_df['createdAt'],
                            y=[selected_model_name.split('/')[-1]] * len(timeline_df),
                            mode='lines',
                            line=dict(width=1.5, dash='dot'),
                            showlegend=False,
                            opacity=0.7,
                            hoverinfo='skip'
                        ))
                        
                        # Improve visualization
                        fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='black')))
                        fig.update_layout(
                            xaxis_title="Version Creation Date",
                            yaxis_title="Model",
                            legend_title="Source Applications",
                            font_family="Roboto Mono",
                            font_color="#2c3e50",
                            plot_bgcolor='rgba(240,240,240,0.2)',
                            hovermode='closest',
                            showlegend=False,
                        )
                        
                        # Show the chart
                        st.plotly_chart(fig, use_container_width=True)

                        # Create a pie chart of the contributors in a column
                        # Create a pie chart of the Source Applications in a column
                        contributor_col, source_application_col = st.columns([1, 1])
                        with contributor_col:
                            st.subheader("Model Contributors")
                            # Get the contributors from the version data
                            contributors = version_data_df['authorUser'].apply(lambda x: x.name).value_counts().reset_index()
                            contributors.columns = ['Contributor', 'Count']
                            # Create a pie chart of the contributors
                            fig = px.pie(contributors, names='Contributor', values='Count', hole=0.5)
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(l=1, r=1, t=1, b=1),
                                height=200,
                                font_family="Roboto Mono",
                                font_color="#2c3e50"
                            )
                            fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                            # Show the chart
                            contributor_col.plotly_chart(fig, use_container_width=True)
                        with source_application_col:
                            st.subheader("Model Source Applications")
                            # Get the source applications from the version data
                            source_applications = version_data_df['sourceApplication'].value_counts().reset_index()
                            source_applications.columns = ['Source Application', 'Count']
                            # Create a pie chart of the source applications
                            fig = px.pie(source_applications, names='Source Application', values='Count', hole=0.5)
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(l=1, r=1, t=1, b=1),
                                height=200,
                                font_family="Roboto Mono",
                                font_color="#2c3e50"
                            )
                            fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                            # Show the chart
                            source_application_col.plotly_chart(fig, use_container_width=True)

                        # Add information about version frequency
                        st.markdown("### Version Frequency Analysis")
                        versions_per_day = version_data_df.set_index('createdAt').groupby(pd.Grouper(freq='D')).size()
                        versions_per_day = versions_per_day[versions_per_day > 0]  # Only days with versions

                        active_days = len(versions_per_day)
                        total_days = (version_data_df['createdAt'].max() - version_data_df['createdAt'].min()).days + 1
                        avg_versions_per_active_day = versions_per_day.mean()

                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        metrics_col1.metric("Active Days", f"{active_days}/{total_days} days")
                        metrics_col2.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
                        if not versions_per_day.empty:
                            metrics_col3.metric("Most Active Day", f"{versions_per_day.idxmax().strftime('%Y-%m-%d')} ({versions_per_day.max()} versions)")
                        else:
                            metrics_col3.metric("Most Active Day", "No data")

                    elif selected_analysis_mode == "Analyze all Child Models Combined":
                        viewer_col, version_data_col = st.columns([1, 1])
                        # Combine all child model ids for the speckle viewer
                        child_model_ids = []
                        latest_version_data_per_model = {}
                        all_version_data_per_model = {}
                        for child in selected_node_children:
                            # Get the model ID from the selected model name
                            # Check the long name of the model
                            for key, value in project_tree.items():
                                if value["long_name"] == child:
                                    child_model_ids.append(value["id"])
                                    # Get the latest version data
                                    latest_version_data = None
                                    soonest_date = None
                                    for version_id, version_info in value["version_data"].items():
                                        if latest_version_data is None or version_info["createdAt"] < soonest_date:
                                            latest_version_data = version_info
                                            soonest_date = version_info["createdAt"]
                                    latest_version_data_per_model[child] = latest_version_data
                                    all_version_data_per_model[child] = value["version_data"]
                                    break

                        combined_model_id = ','.join(child_model_ids)

                        with viewer_col:
                            # Create a Speckle Viewer
                            st.subheader("Speckle Viewer")
                            speckle_model_id = combined_model_id
                            height = 200 * len(child_model_ids)
                            display_speckle_viewer(
                                                    container=viewer_col, 
                                                    project_id=project_id, 
                                                    model_id=speckle_model_id, 
                                                    is_transparent=False,
                                                    hide_controls=False,
                                                    hide_selection_info=False,
                                                    no_scroll=False,
                                                    height=height,
                                                    header_text='Combined Model',
                                                )


                        with version_data_col:
                            # Display the version data
                            st.subheader("Latest Version Data")

                            for child, version_info in latest_version_data_per_model.items():
                                st.markdown(f"**Latest Version for {child}:**")
                                st.markdown(f"**Created By:** {version_info['authorUser'].name}")
                                st.markdown(f"**Created At:** {version_info['createdAt'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
                                st.markdown(f"**Source Application:** {version_info['sourceApplication']}")
                                st.markdown("---")

                        st.header("Combined Model Data:")
                        
                        # Create a timeline of all version data with a different color for each model
                        total_version_count = sum(len(value) for value in all_version_data_per_model.values())
                        st.subheader(f'Timeline for {total_version_count} version(s) across {len(all_version_data_per_model)} models')

                        # Create a dataframe to store all version data
                        all_versions_df = pd.DataFrame()

                        # Process each model's versions and add them to the dataframe
                        for child_model, version_data in all_version_data_per_model.items():
                            # Create a dataframe for this model's versions
                            model_df = pd.DataFrame.from_dict(version_data, orient='index')
                            # Add model name column
                            model_df['model_name'] = child_model
                            # Convert timestamps to datetime
                            model_df['createdAt'] = pd.to_datetime(model_df['createdAt'])
                            # Extract author name from authorUser object
                            model_df['author_name'] = model_df['authorUser'].apply(lambda x: x.name)
                            # Add to the combined dataframe
                            all_versions_df = pd.concat([all_versions_df, model_df])

                        # Sort by creation date
                        all_versions_df = all_versions_df.sort_values(by='createdAt')

                        height = max(7 * total_version_count, 200)

                        # Create a timeline showing version commits by model
                        fig = px.scatter(all_versions_df, 
                                        x='createdAt', 
                                        y='model_name',
                                        color='model_name',
                                        hover_data=['sourceApplication', 'author_name'],  # Use author_name instead of authorUser
                                        labels={'createdAt': 'Date', 'model_name': 'Model Name', 'author_name': 'Author'},
                                        height=height)

                        # Improve the visualization
                        fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='black')))
                        fig.update_layout(
                            xaxis_title="Version Creation Date",
                            yaxis_title="Model",
                            legend_title="Models",
                            font_family="Roboto Mono",
                            font_color="#2c3e50",
                            plot_bgcolor='rgba(240,240,240,0.2)',
                            hovermode='closest',
                            showlegend=False,
                        )

                        # Add connecting lines for each model to better visualize the sequence
                        for model_name in all_versions_df['model_name'].unique():
                            model_data = all_versions_df[all_versions_df['model_name'] == model_name].sort_values('createdAt')
                            
                            fig.add_trace(go.Scatter(
                                x=model_data['createdAt'],
                                y=[model_name] * len(model_data),
                                mode='lines',
                                line=dict(width=1.5, dash='dot'),
                                showlegend=False,
                                opacity=0.7,
                                hoverinfo='skip'
                            ))

                        # Show the chart
                        st.plotly_chart(fig, use_container_width=True)

                        # Create a pie chart of the contributors in a column
                        # Create a pie chart of the Source Applications in a column
                        contributor_col, source_application_col = st.columns([1, 1])
                        with contributor_col:
                            st.subheader("Model Contributors")
                            # Get the contributors from the version data
                            contributors = all_versions_df['authorUser'].apply(lambda x: x.name).value_counts().reset_index()
                            contributors.columns = ['Contributor', 'Count']
                            # Create a pie chart of the contributors
                            fig = px.pie(contributors, names='Contributor', values='Count', hole=0.5)
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(l=1, r=1, t=1, b=1),
                                height=200,
                                font_family="Roboto Mono",
                                font_color="#2c3e50"
                            )
                            fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                            # Show the chart
                            contributor_col.plotly_chart(fig, use_container_width=True)
                        with source_application_col:
                            st.subheader("Model Source Applications")
                            # Get the source applications from the version data
                            source_applications = all_versions_df['sourceApplication'].value_counts().reset_index()
                            source_applications.columns = ['Source Application', 'Count']
                            # Create a pie chart of the source applications
                            fig = px.pie(source_applications, names='Source Application', values='Count', hole=0.5)
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(l=1, r=1, t=1, b=1),
                                height=200,
                                font_family="Roboto Mono",
                                font_color="#2c3e50"
                            )
                            fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                            # Show the chart
                            source_application_col.plotly_chart(fig, use_container_width=True)

                        # Add information about version frequency
                        st.markdown("### Version Frequency Analysis")
                        versions_per_day = all_versions_df.set_index('createdAt').groupby(pd.Grouper(freq='D')).size()
                        versions_per_day = versions_per_day[versions_per_day > 0]  # Only days with versions

                        active_days = len(versions_per_day)
                        total_days = (all_versions_df['createdAt'].max() - all_versions_df['createdAt'].min()).days + 1
                        avg_versions_per_active_day = versions_per_day.mean()

                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        metrics_col1.metric("Active Days", f"{active_days}/{total_days} days")
                        metrics_col2.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
                        metrics_col3.metric("Most Active Day", f"{versions_per_day.idxmax().strftime('%Y-%m-%d')} ({versions_per_day.max()} versions)")

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
                version_user_names.append(user.name)

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
