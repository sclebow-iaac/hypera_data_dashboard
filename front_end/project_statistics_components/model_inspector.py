import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
from streamlit_plotly_events import plotly_events

import attribute_extraction
from dashboards.dashboard import *

default_speckle_viewer_height = 600

def create_network_graph(project_tree, height=800):
    st.subheader("Project Network Diagram")

    # Add expander for click instructions
    with st.expander("How to use the network diagram"):
        st.markdown("""
        - Click on any node to highlight it and all its parent nodes
        - The highlighted path shows the connection from the selected node to the root
        - Each click will update the highlighted path
        - Use the Plotly UI controls in the top-right corner of the chart:
            - The magnifying glass icon allows you to zoom in on a selected region
            - The home icon resets the zoom level to the default view
            - The pan icon lets you drag the view to explore different parts of the diagram
        """)

        # Add controls in a row
        control_col1, control_col2 = st.columns([3, 1])
        
        with control_col1:
            # Add a weight adjustment factor to fine-tune the graph layout
            # Higher values (>1.0) increase separation between depths
            # Lower values (<1.0) decrease separation between depths
            weight_adjustment_factor = st.slider("Weight Adjustment Factor", min_value=0.1, max_value=2.0, value=1.2, step=0.1, help="Adjust the weight of edges based on node depth. Higher values increase separation between nodes at different depths.")
        
        with control_col2:
            # Add reset button that clears the selection
            if st.button("Reset Selection", help="Clear the current selection and reset the network view"):
                # Reset the highlighted node in session state
                st.session_state.highlighted_node = None
                st.rerun()

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
    
    # Calculate node depths from root
    node_depths = {}
    roots = [n for n, d in G.in_degree() if d == 0]
    
    if roots:
        # Use BFS to calculate depth from root
        for root in roots:
            bfs_edges = list(nx.bfs_edges(G, root))
            node_depths[root] = 0
            for u, v in bfs_edges:
                node_depths[v] = node_depths[u] + 1

    # Assign weights to edges based on node depths
    # We want children of the root to be further from root (smaller weight)
    # and deeper nodes to be closer to their parents (larger weight)
    edge_weights = {}
    for u, v in G.edges():
        # Check if both nodes have depth information
        if u in node_depths and v in node_depths:
            # Base weight - deeper nodes get higher weights (closer to parents)
            depth_weight = min(node_depths[u], node_depths[v])
            
            # For edges connected to root or near-root, use much smaller weights
            if depth_weight <= 1:
                edge_weights[(u, v)] = 0.5 / weight_adjustment_factor  # Weight for root connections
            else:
                # Progressive weighting - deeper nodes get higher weights
                edge_weights[(u, v)] = 0.5 + (depth_weight * 0.3 * weight_adjustment_factor)
    
    # Convert to undirected for visualization layout purposes
    G_undirected = G.to_undirected()

    # Apply edge weights to the undirected graph
    for (u, v), weight in edge_weights.items():
        if G_undirected.has_edge(u, v):
            G_undirected[u][v]['weight'] = weight

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
            colorscale='rainbow',
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

def run(project_tree, project_id):
    st.write('This tab allows you to explore the project tree and select models for analysis.')

    # Create the network diagram
    selected_model_name, selected_node_children = create_network_graph(project_tree)

    # Sort the children by their long name
    selected_node_children.sort()

    # print()
    # # Debug print
    # print(f"Selected Model Name: {selected_model_name}")
    # print(f"Selected Node Children: {selected_node_children}")

    if selected_model_name is None:
        st.write("No model selected.")
    else:
        if len(selected_node_children) == 0:
            st.write("No child models available for this node.")
            single_tab = st.container()
            combined_tab = None
        else:
            st.write(f'The selected node has {len(selected_node_children)} child model(s)')
            combined_tab, single_tab = st.tabs([
                "Analyze all Child Models Combined", 
                "Analyze a Single Child Model"
            ])


        with single_tab:
            if len(selected_node_children) != 0:
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
                    print(f'version_data: {version_data}')
                    break

            selected_version_id = st.selectbox(f"Select a version, there is/are {len(version_data)}", list(version_data.keys()), format_func=lambda x: version_data[x]["createdAt"])
            
            
            attribute_extraction.run_from_version_id(version_id=selected_version_id, model_id=selected_model_id)

            # Create two columns for the speckle viewer and the version data
            viewer_col, version_data_col = st.columns([1, 1])
            with viewer_col:
                # Create a Speckle Viewer
                st.subheader("Speckle Viewer")
                speckle_model_id = selected_model_id + '@' + selected_version_id
                display_speckle_viewer(container=viewer_col, project_id=project_id, model_id=speckle_model_id, header_text='Selected Model', height=default_speckle_viewer_height)

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

        if combined_tab is not None:
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
                    height = min(max(50 * len(child_model_ids), default_speckle_viewer_height), 1000)
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
                        with st.expander(f"**Latest Version for {child}:**"):
                            st.markdown(f"**Created By:** {version_info['authorUser'].name}")
                            st.markdown(f"**Created At:** {version_info['createdAt'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
                            st.markdown(f"**Source Application:** {version_info['sourceApplication']}")

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

                height = min(800, max(150 + 7 * total_version_count, 200))

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

