import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
from streamlit_plotly_events import plotly_events

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

def setup_speckle_connection(models_limit=100):
    speckle_server = "macad.speckle.xyz"
    speckle_token = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckle_server)
    account = get_account_from_token(speckle_token, speckle_server)
    client.authenticate_with_account(account)

    project_id = '31f8cca4e0'
    selected_project = client.project.get(project_id=project_id)
    project = client.project.get_with_models(
        project_id=selected_project.id, models_limit=models_limit)
    models = project.models.items

    return models, client, project_id

@st.cache_data(ttl='1h')
# @st.cache_data()
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

def create_network_graph(project_tree, height=800, show_team_selector=True):
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

    if show_team_selector:
        # Add a checkbox for each team to filter the models
        st.markdown("###### Show/Hide Teams")
        teams = set()
        for model in project_tree.values():
            # Extract the team name from the model's long name
            team_name = model["team_name"]
            teams.add(team_name)
        # teams = sorted(teams)
        team_columns = st.columns(len(teams))
        selected_teams = []
        for team, col in zip(teams, team_columns):
            with col:
                if st.checkbox(team, value=True):
                    selected_teams.append(team)
        
        # Filter the project tree based on the selected teams
        filtered_project_tree = {key: value for key, value in project_tree.items() if value["team_name"] in selected_teams}
        project_tree = filtered_project_tree

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
