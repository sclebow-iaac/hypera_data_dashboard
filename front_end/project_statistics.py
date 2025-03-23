import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pprint import pprint
from streamlit_plotly_events import plotly_events

from dashboards.dashboard import *

def create_network_graph(project_tree, height=800):
    st.subheader("Project Network Diagram")

    G = nx.DiGraph()  # Use a directed graph for clearer parent/child relationships

    # First, add all nodes to the graph
    for key in project_tree.keys():
        G.add_node(key)
    
    # Then, add all edges to connect parents and children
    for key, value in project_tree.items():
        # Add edge to parent if parent exists
        if value["parent"] is not None:
            # Create edges from child to parent
            G.add_edge(key, value["parent"])
            
            # Debug info to trace the edge being created
            print(f"Adding edge: {key} -> {value['parent']}")
            
            # Validate that parent exists in the tree
            if value["parent"] not in project_tree:
                print(f"WARNING: Parent {value['parent']} for {key} not found in project_tree!")

    # After adding all edges, check for any disconnected components
    components = list(nx.weakly_connected_components(G))
    print(f"Number of disconnected components: {len(components)}")
    for i, component in enumerate(components):
        print(f"Component {i} has {len(component)} nodes")
        if len(component) < 5:  # Print small components to help identify the issue
            print(f"  Nodes in component {i}: {component}")
    
    # Convert to undirected for visualization layout purposes
    G_undirected = G.to_undirected()
    
    # Use Kamada-Kawai layout for better visualization of hierarchical data
    pos = nx.kamada_kawai_layout(G_undirected)

    # Create edge traces
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
        line=dict(width=2, color='lightgrey'),
        hoverinfo='none',
        mode='lines'
    )

    # Create node traces
    node_x = []
    node_y = []
    node_names = []  # Store node names for clickData reference
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_names.append(node)

    # Calculate node distances from root for visual scaling
    node_distances = []
    node_text = []
    hover_text = []
    for node in G.nodes():
        # Use a safely guarded approach to get distances
        distance = 0
        current_node = node
        visited_nodes = set()  # Track visited nodes to prevent cycles
        
        while (current_node in project_tree and 
               project_tree[current_node]["parent"] is not None and 
               current_node not in visited_nodes):
            
            visited_nodes.add(current_node)
            distance += 1
            current_node = project_tree[current_node]["parent"]
            
            # Safety check - if we somehow end up in a loop or with a parent not in tree
            if current_node not in project_tree:
                break
                
        node_distances.append(distance)
        
        # Get display name
        if node in project_tree and "short_name" in project_tree[node]:
            display_name = project_tree[node]["short_name"]
        else:
            display_name = node.split("/")[-1] if "/" in node else node

        node_text.append(f'{display_name}')
        hover_text.append(project_tree[node]["long_name"])

    max_distance = max(node_distances) if node_distances else 0
    # Reverse the distances to get the distance from the root node
    node_distances = [max_distance - d for d in node_distances]

    # Create node trace with styling based on node distances
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=hover_text,
        marker=dict(
            showscale=False,
            colorscale='ice',
            color=node_distances,
            size=[10 + 20 * (d / max_distance) if max_distance > 0 else 20 for d in node_distances],
            line=dict(width=2, color='rgb(0, 0, 0)'),
        ),
        text=node_text,
        textfont=dict(
            family='Arial',
            size=[8 + 10 * (d / max_distance) if max_distance > 0 else 14 for d in node_distances],
            color='#000000'
        ),
        textposition='top center',
    )

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    height=height,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    clickmode='event+select'
                )
                )
    
    # Add expander for click instructions
    with st.expander("How to use the network diagram"):
        st.markdown("""
        - Click on any node to highlight it and all its parent nodes
        - The highlighted path shows the connection from the selected node to the root
        - Each click will update the highlighted path
        """)
    
    # Create containers for the highlighted path information and chart
    highlight_container = st.empty()
    chart_container = st.container()
    
    # Initialize session state for highlighted node if not exists
    if 'highlighted_node' not in st.session_state:
        st.session_state.highlighted_node = None
    
    selected_model_name = None

    # Handle highlighted node from previous interaction
    if st.session_state.highlighted_node and st.session_state.highlighted_node in project_tree:
        selected_node = st.session_state.highlighted_node
        
        # Generate highlighted path
        path_nodes = []
        current = selected_node
        while current is not None:
            path_nodes.append(current)
            current = project_tree[current]["parent"]
        
        selected_model_name = selected_node
        
        # Update the info display
        display_path = '/'.join([project_tree[node].get("short_name", node.split("/")[-1]) for node in reversed(path_nodes)])
        highlight_container.markdown(f"""
        **Selected Model**  
        {display_path}
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
        
        # Create highlighted traces
        highlighted_edge_trace = go.Scatter(
            x=highlighted_edge_x,
            y=highlighted_edge_y,
            line=dict(width=3, color='red'),
            hoverinfo='none',
            mode='lines'
        )
        
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
            text=[project_tree[node].get("short_name", node.split("/")[-1]) for node in path_nodes]
        )
        
        # Create a new figure with highlighting
        display_fig = go.Figure(
            data=[edge_trace, node_trace, highlighted_edge_trace, highlighted_node_trace],
            layout=fig.layout
        )
    else:
        # Use the original figure if no highlights
        display_fig = fig
    
    # Use Streamlit's plotly_events to handle click interactions
    with chart_container:
        selected_points = plotly_events(display_fig, click_event=True, override_height=height)
    
    # Process new clicks
    if selected_points:
        point_index = selected_points[0].get("pointIndex")
        
        if point_index is not None and point_index < len(node_names):
            # Update session state with newly selected node
            st.session_state.highlighted_node = node_names[point_index]
            st.rerun()
    
    # Get direct children of the selected model - your new implementation
    selected_node_children = []
    if selected_model_name:
        for key, value in project_tree.items():
            if value['parent'] is not None:
                if selected_model_name in value['parent']:
                    # Check if the child has versions
                    if value["version_count"] > 0:
                        selected_node_children.append(key)

    return selected_model_name, selected_node_children

@st.cache_data(ttl='60minutes')
def get_project_data():
    print(f'get_project_data(models, client, project_id)')
    
    models, client, project_id = setup_speckle_connection()

    # Create a dictionary to store the project data
    project_tree = {}
    
    # First pass: Add all models to the tree
    for model in models:
        id = model.id
        long_name = model.name
        short_name = model.name.split("/")[-1]
        parent = '/'.join(model.name.split("/")[:-1]) if "/" in model.name else None
        team_name = model.name.split("/")[1].capitalize() if len(model.name.split("/")) > 1 else "Root"

        versions = client.version.get_versions(model_id=model.id, project_id=project_id, limit=100).items
        version_count = len(versions)
        
        if version_count == 0:
            # Skip models with no versions
            print(f"Skipping model {long_name} with no versions")
            continue
        
        version_data = {}
        for version in versions:
            version_data[version.id] = {
                "createdAt": version.createdAt,
                "authorUser": version.authorUser,
                "sourceApplication": version.sourceApplication,
            }

        # Add or update the model in the project tree
        project_tree[long_name] = {
            "parent": parent if parent else None,
            "children": project_tree.get(long_name, {}).get("children", []),
            "id": id,
            "version_count": version_count,
            "version_data": version_data,
            "long_name": long_name,
            "short_name": short_name,
            "team_name": team_name
        }
    
    # Second pass: Ensure all parents exist and add children
    all_nodes = list(project_tree.keys())
    for node_name in all_nodes:
        node = project_tree[node_name]
        parent_name = node["parent"]
        
        if parent_name and parent_name not in project_tree:
            # Create a placeholder parent node with minimal information
            project_tree[parent_name] = {
                "parent": '/'.join(parent_name.split("/")[:-1]) if "/" in parent_name else None,
                "children": [],
                "id": None,  # We don't have this information
                "version_count": 0,
                "version_data": {},
                "long_name": parent_name,
                "short_name": parent_name.split("/")[-1] if "/" in parent_name else parent_name,
                "team_name": parent_name.split("/")[1].capitalize() if len(parent_name) > 1 else "Root"
            }
        
        # Add this node as a child to its parent
        if parent_name:
            if node_name not in project_tree[parent_name]["children"]:
                project_tree[parent_name]["children"].append(node_name)
    
    # Second pass: Create necessary parent nodes that don't exist as actual models
    for node_name in list(project_tree.keys()):  # Use a copy of keys to safely modify dict
        node = project_tree[node_name]
        current_parent = node["parent"]
        
        # Create parent nodes all the way up to root if needed
        while current_parent and current_parent not in project_tree:
            print(f"Creating missing parent: {current_parent}")
            parent_parts = current_parent.split("/")
            parent_of_parent = '/'.join(parent_parts[:-1]) if len(parent_parts) > 1 else None
            parent_short_name = parent_parts[-1]
            
            # Create the parent node
            project_tree[current_parent] = {
                "parent": parent_of_parent,
                "children": [],
                "id": None,
                "version_count": 0,
                "version_data": {},
                "long_name": current_parent,
                "short_name": parent_short_name,
                "team_name": parent_parts[1].capitalize() if len(parent_parts) > 1 else "Root"
            }
            
            # Move up to the next parent
            current_parent = parent_of_parent

    # Third pass: Find the root nodes (nodes with no parent) and set their parent to None
    root_nodes = []
    for node_name, node in project_tree.items():
        if node["parent"] is None or node["parent"] == "":
            root_nodes.append(node_name)
            
    # If we have more than one root, create a single project root
    if len(root_nodes) > 1:
        project_root_name = "project_root"
        project_tree[project_root_name] = {
            "parent": None,
            "children": root_nodes,
            "id": None,
            "version_count": 0,
            "version_data": {},
            "long_name": project_root_name,
            "short_name": "Project Root",
            "team_name": "Root"
        }
        
        # Update the former root nodes to point to the new project root
        for node_name in root_nodes:
            project_tree[node_name]["parent"] = project_root_name
    
    # Fourth pass: Ensure all parent references are valid
    for node_name, node in project_tree.items():
        if node["parent"] and node["parent"] not in project_tree:
            # If the parent doesn't exist, set it to None
            node["parent"] = None

    # Debug output
    print("\nProject Tree Parent Links:")
    for node_name, node in project_tree.items():
        parent = node["parent"]
        if parent:
            if parent not in project_tree:
                print(f"WARNING: {node_name} has parent {parent} that doesn't exist in tree!")
            else:
                print(f"{node_name} → {parent}")
        else:
            print(f"{node_name} (ROOT)")

    return project_tree, project_id

def run(container=None):
    # Get the project data
    project_tree, project_id = get_project_data()

    # for key, value in project_tree.items():
    #     print(f'key: {key}')
    #     print(f'children: {value["children"]}')
    #     print(f'parent: {value["parent"]}')
    #     # print(f'value: {value}')
    #     print()
    #     pass

    # # Debug print
    # pprint(project_tree)

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

                # print()
                # # Debug print
                # print(f"Selected Model Name: {selected_model_name}")
                # print(f"Selected Node Children: {selected_node_children}")

                if selected_model_name is None:
                    st.write("No model selected.")
                else:
                    combined_tab, single_tab = st.tabs([
                        "Analyze all Child Models Combined", 
                        "Analyze a Single Child Model"
                    ])


                    with single_tab:
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

                    with combined_tab:
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
