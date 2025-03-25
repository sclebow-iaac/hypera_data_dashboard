import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pprint import pprint
import requests
import datetime

from streamlit_plotly_events import plotly_events

from dashboards.dashboard import *
import attribute_extraction

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

@st.cache_data(ttl='6h')
def fetch_github_repository_data(repository="sclebow-iaac/hypera_data_dashboard", since_date=None):
    """
    Fetch repository data from GitHub API with no commit limit
    
    Parameters:
    repository (str): Repository name in format 'owner/repo'
    since_date (str, optional): ISO format date string (YYYY-MM-DD) to filter commits from
    """
    try:
        # Base API URL
        base_url = f"https://api.github.com/repos/{repository}"
        
        # Get repository info
        repo_response = requests.get(base_url)
        if repo_response.status_code != 200:
            return None, f"Error fetching repository data: {repo_response.status_code}"
        
        repo_data = repo_response.json()
        
        # Get all commits with pagination
        all_commits = []
        page = 1
        more_commits = True
        
        while more_commits:
            # Build the commits URL with pagination and optional date filtering
            commits_url = f"{base_url}/commits?per_page=100&page={page}"
            if since_date:
                # Convert date string to proper format if needed
                if isinstance(since_date, str) and len(since_date) == 10:  # YYYY-MM-DD format
                    since_date = f"{since_date}T00:00:00Z"
                commits_url += f"&since={since_date}"
            
            # Fetch commits for current page
            commits_response = requests.get(commits_url)
            
            if commits_response.status_code != 200:
                if page == 1:
                    return repo_data, f"Error fetching commit data: {commits_response.status_code}"
                else:
                    # We've already got some commits, so just break the loop
                    break
            
            page_commits = commits_response.json()
            
            # If we got an empty list or fewer than 100 items, we've reached the end
            if not page_commits or len(page_commits) < 100:
                all_commits.extend(page_commits)
                more_commits = False
            else:
                all_commits.extend(page_commits)
                page += 1
                
            # Add a progress message every few pages
            if page % 5 == 0:
                print(f"Fetched {len(all_commits)} commits so far...")
        
        # Get contributors
        contributors_response = requests.get(f"{base_url}/contributors")
        if contributors_response.status_code != 200:
            return repo_data, all_commits, f"Error fetching contributor data: {contributors_response.status_code}"
        
        contributors_data = contributors_response.json()
        
        # Get pull requests with similar pagination approach
        all_pulls = []
        page = 1
        more_pulls = True
        
        while more_pulls:
            pulls_url = f"{base_url}/pulls?state=all&per_page=100&page={page}"
            pulls_response = requests.get(pulls_url)
            
            if pulls_response.status_code != 200:
                if page == 1:
                    return repo_data, all_commits, contributors_data, f"Error fetching pull request data: {pulls_response.status_code}"
                else:
                    break
            
            page_pulls = pulls_response.json()
            
            if not page_pulls or len(page_pulls) < 100:
                all_pulls.extend(page_pulls)
                more_pulls = False
            else:
                all_pulls.extend(page_pulls)
                page += 1
        
        # If we have a since_date, filter PRs that were created after that date
        if since_date:
            since_datetime = pd.to_datetime(since_date)
            all_pulls = [pr for pr in all_pulls if pd.to_datetime(pr['created_at']) >= since_datetime]
        
        print(f"Fetched total: {len(all_commits)} commits, {len(all_pulls)} pull requests")
        
        return {
            "repository": repo_data,
            "commits": all_commits,
            "contributors": contributors_data,
            "pulls": all_pulls,
            "filter_date": since_date
        }
    except Exception as e:
        return None, f"Error: {str(e)}"

def check_github_rate_limit():
    """Check GitHub API rate limit status"""
    try:
        response = requests.get("https://api.github.com/rate_limit")
        if response.status_code == 200:
            data = response.json()
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            limit = core.get("limit", 0)
            reset_time = datetime.datetime.fromtimestamp(core.get("reset", 0))
            
            return {
                "remaining": remaining,
                "limit": limit,
                "reset_time": reset_time
            }
    except Exception as e:
        return None
    
    return None

def fetch_branch_data(repository):
    """Fetch branch data for a repository"""
    try:
        response = requests.get(f"https://api.github.com/repos/{repository}/branches")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []
    
# Add this helper function
def create_simple_git_graph(filtered_commit_df, author_colors):
    """Create a simplified git graph when enhanced version fails"""
    fig = go.Figure()
    
    # Add main branch line
    fig.add_trace(go.Scatter(
        x=filtered_commit_df["date"],
        y=[0] * len(filtered_commit_df),
        mode="lines",
        line=dict(color="rgba(0,0,255,0.5)", width=2),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Add commit nodes with author-based coloring
    fig.add_trace(go.Scatter(
        x=filtered_commit_df["date"],
        y=[0] * len(filtered_commit_df),
        mode="markers+text",
        marker=dict(
            color=[author_colors.get(author, "blue") for author in filtered_commit_df["author"]],
            size=12,
            line=dict(color="darkblue", width=1)
        ),
        text=filtered_commit_df["sha"],
        textposition="top center",
        textfont=dict(size=8),
        hovertext=filtered_commit_df.apply(
            lambda row: f"<b>{row['sha']}</b><br>" +
                        f"Author: {row['author']}<br>" +
                        f"Date: {row['date'].strftime('%Y-%m-%d %H:%M')}<br>" +
                        f"Message: {row['message']}",
            axis=1
        ),
        hoverinfo="text",
        showlegend=False
    ))
    
    # Layout customization
    fig.update_layout(
        height=300,
        xaxis_title="Commit Date",
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-1, 1]
        ),
        plot_bgcolor="rgba(240,240,240,0.2)",
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="closest"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def run(container=None):
    default_speckle_viewer_height = 600


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
            model_inspector_tab, overall_statistics_tab, metric_analysis_tab, dashboard_metrics_tab = \
                st.tabs(["Model Inspector", "Overall Project Statistics", "Metric Analysis", "Dashboard Analytics"])
            
            # Get the project data
            project_tree, project_id = get_project_data()

            with model_inspector_tab:
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

            with overall_statistics_tab:
                st.write('This tab shows the overall statistics of the entire project')

                # Create a timeline of all the version data with a different color for each team
                timeline_data = []
                for model in project_tree.values():
                    for version in model["version_data"].values():
                        created_at = version["createdAt"]
                        team_name = model["team_name"]

                        timeline_data.append({
                            "createdAt": created_at,
                            "team_name": team_name,
                        })
                #COMMIT PANDAS TABLE
                st.subheader("Activity Timeline")
                
                # Convert timeline_data to pandas DataFrame
                timeline_df = pd.DataFrame(timeline_data)
                
                # Convert the createdAt column to datetime
                timeline_df['createdAt'] = pd.to_datetime(timeline_df['createdAt'])
                
                # Group by date and team, count occurrences
                timeline_df['date'] = timeline_df['createdAt'].dt.date
                timeline_grouped = timeline_df.groupby(['date', 'team_name']).size().reset_index(name='count')
                
                # Create line chart with a line for each team
                fig = px.line(
                    timeline_grouped, 
                    x='date', 
                    y='count', 
                    color='team_name',
                    markers=True,
                    labels={'date': 'Date', 'count': 'Number of Versions', 'team_name': 'Team'}
                )
                
                # Improve styling
                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=0.8
                    ),
                    legend_title='Teams',
                    margin=dict(l=1, r=1, t=10, b=1),
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_family="Roboto Mono",
                    font_color="#2c3e50",
                    hovermode='closest',
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Roboto Mono",
                        font_color="#2c3e50",
                    ),
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>Team: %{customdata}<br>Versions: %{y}<extra></extra>'
                )
                
                # Add team name as custom data for hover info
                fig.update_traces(customdata=timeline_grouped['team_name'])
                
                # Show Chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Add metrics for overall statistics
                st.subheader("Overall Project Statistics")
                # Get the total number of models that have versions
                total_models = sum(1 for model in project_tree.values() if model["version_count"] > 0)
                # Get the total number of versions
                total_versions = sum(model["version_count"] for model in project_tree.values())
                # Get the total number of contributors
                total_contributors = len(set(version["authorUser"].name for model in project_tree.values() for version in model["version_data"].values()))
                # Get the total number of source applications
                total_source_applications = len(set(version["sourceApplication"] for model in project_tree.values() for version in model["version_data"].values()))
                
                # Get the active days
                all_versions_df = pd.DataFrame()
                for model in project_tree.values():
                    for version in model["version_data"].values():
                        all_versions_df = pd.concat([all_versions_df, pd.DataFrame([{
                            "createdAt": version["createdAt"],
                            "authorUser": version["authorUser"],
                            "sourceApplication": version["sourceApplication"],
                        }])], ignore_index=True)
                all_versions_df['createdAt'] = pd.to_datetime(all_versions_df['createdAt'])
                all_versions_df['date'] = all_versions_df['createdAt'].dt.date
                all_versions_df['count'] = 1
                active_days = all_versions_df.groupby('date').size().reset_index(name='count')
                active_days = len(active_days[active_days['count'] > 0])
                total_days = (all_versions_df['createdAt'].max() - all_versions_df['createdAt'].min()).days + 1
                avg_versions_per_active_day = all_versions_df.groupby('date').size().mean()
                # Create metrics
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                metrics_col1.metric("Total Models", total_models)
                metrics_col2.metric("Total Versions", total_versions)
                metrics_col3.metric("Total Contributors", total_contributors)
                metrics_col4.metric("Total Source Applications", total_source_applications)
                metrics_col5, metrics_col6, metrics_col7 = st.columns(3)
                metrics_col5.metric("Active Days", f"{active_days}/{total_days} days")
                metrics_col6.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
                if active_days > 0:
                    most_active_day = all_versions_df.groupby('date').size().idxmax()
                    most_active_count = all_versions_df.groupby('date').size().max()
                    metrics_col7.metric("Most Active Day", f"{most_active_day.strftime('%Y-%m-%d')} ({most_active_count} versions)")
                else:
                    metrics_col7.metric("Most Active Day", "No data")
                

                pie_height = 300
                contributer_col, source_application_col = st.columns([1, 1])
                with contributer_col:
                    # Create a pie chart of all the project contributors
                    st.subheader("Project Contributors")
                    # Get the contributors from the version data
                    all_contributors = []
                    for model in project_tree.values():
                        for version in model["version_data"].values():
                            all_contributors.append(version["authorUser"].name)
                    all_contributors = pd.Series(all_contributors).value_counts().reset_index()
                    all_contributors.columns = ['Contributor', 'Count']

                    # Update 'Contributor' column to include the percentage
                    all_contributors['Percentage'] = (all_contributors['Count'] / all_contributors['Count'].sum()) * 100
                    all_contributors['Percentage Contributor'] = all_contributors['Percentage'].round(2).astype(str) + "% " + all_contributors['Contributor']

                    # Create a pie chart of the contributors
                    fig = px.pie(all_contributors, names='Percentage Contributor', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        legend_title="Contributors",
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=pie_height,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    st.plotly_chart(fig, use_container_width=True)

                    # Add a celebration message for the most active contributor
                    most_active_contributor = all_contributors.iloc[0]['Contributor']
                    most_active_contributor_count = all_contributors.iloc[0]['Count']
                    st.markdown(f"**Most Active Contributor: {most_active_contributor}** with {most_active_contributor_count} contributions!")

                with source_application_col:
                    # Create a pie chart of all the project source applications
                    st.subheader("Project Source Applications")
                    # Get the source applications from the version data
                    all_source_applications = []
                    for model in project_tree.values():
                        for version in model["version_data"].values():
                            all_source_applications.append(version["sourceApplication"])
                    all_source_applications = pd.Series(all_source_applications).value_counts().reset_index()
                    all_source_applications.columns = ['Source Application', 'Count']

                    # Update 'Source Application' column to include the percentage
                    all_source_applications['Percentage'] = (all_source_applications['Count'] / all_source_applications['Count'].sum()) * 100
                    all_source_applications['Percentage Source Application'] = all_source_applications['Percentage'].round(2).astype(str) + "% " + all_source_applications['Source Application']

                    # Create a pie chart of the source applications
                    fig = px.pie(all_source_applications, names='Percentage Source Application', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        legend_title="Source Applications",
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=pie_height,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    st.plotly_chart(fig, use_container_width=True)

                    # Add a celebration message for the most used source application
                    most_used_source_application = all_source_applications.iloc[0]['Source Application']
                    most_used_source_application_count = all_source_applications.iloc[0]['Count']
                    st.markdown(f"**Most Used Source Application: {most_used_source_application}** with {most_used_source_application_count} contributions!")

                version_col, model_col = st.columns([1, 1])

                with version_col:
                    # Create a pie chart of all the versions by team
                    st.subheader("Project Versions by Team")
                    # Get the teams from the version data
                    all_versions_by_team = []
                    for model in project_tree.values():
                        for version in model["version_data"].values():
                            all_versions_by_team.append(model["team_name"])
                    all_versions_by_team = pd.Series(all_versions_by_team).value_counts().reset_index()
                    all_versions_by_team.columns = ['Team', 'Count']

                    # Remove the "Root" team from the list
                    all_versions_by_team = all_versions_by_team[all_versions_by_team['Team'] != 'Root']

                    # Update 'Team' column to include the percentage
                    all_versions_by_team['Percentage'] = (all_versions_by_team['Count'] / all_versions_by_team['Count'].sum()) * 100
                    all_versions_by_team['Percentage Team'] = all_versions_by_team['Percentage'].round(2).astype(str) + "% " + all_versions_by_team['Team']

                    # Create a pie chart of the teams
                    fig = px.pie(all_versions_by_team, names='Percentage Team', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        legend_title="Teams",
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=pie_height,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    st.plotly_chart(fig, use_container_width=True)

                with model_col:
                    # Create a pie chart of all the models by team
                    st.subheader("Project Models by Team")
                    # Get the teams from the version data
                    all_models_by_team = []
                    for model in project_tree.values():
                        all_models_by_team.append(model["team_name"])
                    all_models_by_team = pd.Series(all_models_by_team).value_counts().reset_index()
                    all_models_by_team.columns = ['Team', 'Count']

                    # Remove the "Root" team from the list
                    all_models_by_team = all_models_by_team[all_models_by_team['Team'] != 'Root']
                    
                    # Update 'Team' column to include the percentage
                    all_models_by_team['Percentage'] = (all_models_by_team['Count'] / all_models_by_team['Count'].sum()) * 100
                    all_models_by_team['Percentage Team'] = all_models_by_team['Percentage'].round(2).astype(str) + "% " + all_models_by_team['Team']

                    # Create a pie chart of the teams
                    fig = px.pie(all_models_by_team, names='Percentage Team', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        legend_title="Teams",
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=pie_height,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    st.plotly_chart(fig, use_container_width=True)
                
                # Add a celebration message for the most active team
                team_data = {}

                for team in all_versions_by_team['Team']:
                    if team not in team_data:
                        team_data[team] = {
                            'total_count': 0,
                            'version_count': 0,
                            'model_count': 0
                        }

                # Iterate through all_versions_by_team
                for index, row in all_versions_by_team.iterrows():
                    team = row['Team']
                    count = row['Count']
                    team_data[team]['total_count'] += count
                    team_data[team]['version_count'] += count
                
                # Iterate through all_models_by_team
                for index, row in all_models_by_team.iterrows():
                    team = row['Team']
                    count = row['Count']
                    print(f'team: {team} count: {count}')
                    team_data[team]['total_count'] += count
                    team_data[team]['model_count'] += count

                # Find the most active team
                most_active_team = max(team_data, key=lambda x: team_data[x]['total_count'])
                most_active_team_version_count = team_data[most_active_team]['version_count']
                most_active_team_model_count = team_data[most_active_team]['model_count']
                st.markdown(f"<div style='text-align: center;'><b>Most Active Team: {most_active_team}</b> with {most_active_team_version_count} versions across {most_active_team_model_count} models!</div>", unsafe_allow_html=True)

                # Calculate the most balanced team
                # The most balanced team is the one with the most equal number of versions for each team member
                balanced_data = {}

                # Manually enter the number of members per team
                team_members = {
                    "Facade": 3,
                    "Services": 3,
                    "Industrial": 3,
                    "Residential": 3,
                    "Structure": 2
                }
                
                for model in project_tree.values():
                    for version in model["version_data"].values():
                        team_name = model["team_name"]
                        author_name = version["authorUser"].name
                        if team_name not in balanced_data:
                            balanced_data[team_name] = {}
                        if author_name not in balanced_data[team_name]:
                            balanced_data[team_name][author_name] = 0
                        balanced_data[team_name][author_name] += 1
                # Calculate the average number of versions per team member for each team
                balanced_team_data = {}
                for team, members in balanced_data.items():
                    if len(members) < team_members[team]:
                        # Add missing members with 0 versions
                        for i in range(team_members[team] - len(members)):
                            members[f"Member {i+1}"] = 0
                    total_versions = sum(members.values())


                    balanced_team_data[team] = {
                        'total_versions': total_versions,
                        'members': members,
                        'team_members': team_members[team],
                        'team_score': 0,
                        'goal_percentage_per_member': 0,
                        'percentage_per_member': 0
                    }

                    percentage_per_member = []

                    for member, count in members.items():
                        percentage = (count / total_versions) * 100
                        percentage_per_member.append(percentage)
                    
                    # print(f"team: {team} percentage_per_member: {percentage_per_member} total_versions: {total_versions}")

                    # The best team has all of the contributers with the same percentage
                    # The most balanced team is the one with the most equal number of versions for each team member
                    goal_percentage_per_member = 100 / team_members[team]
                    team_score = sum(abs(percentage - goal_percentage_per_member) for percentage in percentage_per_member)

                    print(f"team: {team} team_score: {team_score} goal_percentage_per_member: {goal_percentage_per_member} percentage_per_member: {percentage_per_member}")
                    balanced_team_data[team]['team_score'] = team_score
                    balanced_team_data[team]['goal_percentage_per_member'] = goal_percentage_per_member
                    balanced_team_data[team]['percentage_per_member'] = percentage_per_member
                    balanced_team_data[team]['members'] = members
                    balanced_team_data[team]['team_members'] = team_members[team]
                
                # Find the most balanced team
                # The most balanced team is the one with the lowest team score
                st.subheader("Most Balanced Team Members")
                most_balanced_team = min(balanced_team_data, key=lambda x: balanced_team_data[x]['team_score'])
                most_balanced_team_percentage_per_member = balanced_team_data[most_balanced_team]['percentage_per_member']
                most_balanced_team_goal_percentage_per_member = balanced_team_data[most_balanced_team]['goal_percentage_per_member']
                most_balanced_team_number_of_members = team_members[most_balanced_team]
                most_balanced_team_score = balanced_team_data[most_balanced_team]['team_score']
                most_balanced_team_members = balanced_team_data[most_balanced_team]['members']
                most_balanced_team_total_versions = balanced_team_data[most_balanced_team]['total_versions']
                st.markdown(f"<div style='text-align: center;'><b>Most Balanced Team: {most_balanced_team}</b> with {most_balanced_team_total_versions} versions across {most_balanced_team_number_of_members} members!</div>", unsafe_allow_html=True)
                # Show the most balanced team members
                # Create a dataframe for the most balanced team members
                most_balanced_team_members_df = pd.DataFrame.from_dict(most_balanced_team_members, orient='index', columns=['Version Count'])
                most_balanced_team_members_df['Percentage'] = (most_balanced_team_members_df['Version Count'] / most_balanced_team_total_versions) * 100
                most_balanced_team_members_df['Goal Percentage'] = most_balanced_team_goal_percentage_per_member
                most_balanced_team_members_df['Difference'] = most_balanced_team_members_df['Percentage'] - most_balanced_team_members_df['Goal Percentage']

                # Format the columns
                most_balanced_team_members_df['Version Count'] = most_balanced_team_members_df['Version Count'].astype(int)
                most_balanced_team_members_df['Percentage'] = most_balanced_team_members_df['Percentage'].round(2).astype(str) + "%"
                most_balanced_team_members_df['Goal Percentage'] = most_balanced_team_members_df['Goal Percentage'].round(2).astype(str) + "%"
                most_balanced_team_members_df['Difference'] = most_balanced_team_members_df['Difference'].round(2).astype(str) + "%"

                st.dataframe(most_balanced_team_members_df[['Version Count', 'Percentage', 'Goal Percentage', 'Difference']], use_container_width=True)

                # Also show the balance scores of the other teams
                st.subheader("Team Balance Scores")
                # Create a dataframe for the team balance scores
                team_balance_scores_df = pd.DataFrame.from_dict(balanced_team_data, orient='index')
                team_balance_scores_df['Team'] = team_balance_scores_df.index
                team_balance_scores_df['Team Balance Score'] = team_balance_scores_df['team_score']

                # Sort the dataframe by team balance score, lowest first
                team_balance_scores_df = team_balance_scores_df.sort_values(by='Team Balance Score', ascending=True)

                st.dataframe(team_balance_scores_df[['Team', 'Team Balance Score']], use_container_width=True)
                    
            with metric_analysis_tab:
                # Add metric analysis here
                st.subheader("Metric Analysis")
                st.write("This tab is under construction. Please check back later.")
                st.write('This tab will display all the metrics across all teams and compare them to each other')

            with dashboard_metrics_tab:
                # Add this in the dashboard_metrics_tab section
                rate_limit = check_github_rate_limit()
                if rate_limit:
                    with st.expander("GitHub API Rate Limit Status"):
                        st.write(f"Remaining requests: {rate_limit['remaining']}/{rate_limit['limit']}")
                        st.write(f"Reset time: {rate_limit['reset_time'].strftime('%Y-%m-%d %H:%M:%S')}")

                # Add dashboard metrics here
                st.subheader("Dashboard Analytics")
                st.write('This tab displays data from the Dashboard Github Repository')

                github_url = "https://github.com/sclebow-iaac/hypera_data_dashboard"
                forked_url = 'https://github.com/specklesystems/specklepy'
                
                # Create a git commit history chart
                st.subheader("Repository Links")

                # Add links to repositories
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"[Dashboard GitHub Repository]({github_url})")
                with col2:
                    st.markdown(f"[Forked from SpecklePy Repository on 1/23/2024]({forked_url})")
                                
                # Add date filtering 
                st.subheader("Filter Commits")
                col1, col2 = st.columns(2)

                with col1:
                    start_date = st.date_input(
                        "Start Date", 
                        value=datetime.date(2025, 1, 1),
                        min_value=datetime.date(2020, 1, 1),
                        max_value=datetime.date.today()
                    )

                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=datetime.date.today(),
                        min_value=datetime.date(2020, 1, 1),
                        max_value=datetime.date.today()
                    )

                # Format date for API filtering - pass the selected start date to the API call
                since_date_str = start_date.strftime('%Y-%m-%d')

                repository = 'sclebow-iaac/hypera_data_dashboard'
                # Fetch GitHub data with date filtering at the API level
                with st.spinner("Fetching repository data..."):
                    github_data = fetch_github_repository_data(repository, since_date=since_date_str)

                if isinstance(github_data, tuple) and len(github_data) > 1 and isinstance(github_data[1], str):
                    # Show error message
                    st.error(github_data[1])
                else:
                    # Extract repository metrics
                    repo_data = github_data["repository"]
                    commits = github_data["commits"]
                    contributors = github_data["contributors"]
                    pulls = github_data["pulls"]
                    
                    # Display repository metrics
                    st.subheader("Repository Overview")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Stars", repo_data.get("stargazers_count", 0))
                    with col2:
                        st.metric("Forks", repo_data.get("forks_count", 0))
                    with col3:
                        st.metric("Open Issues", repo_data.get("open_issues_count", 0))
                    with col4:
                        st.metric("Watchers", repo_data.get("subscribers_count", 0))
                    
                    # Process commit data
                    commit_df = pd.DataFrame([
                        {
                            "date": pd.to_datetime(commit["commit"]["author"]["date"]),
                            "author": commit["commit"]["author"]["name"],
                            "message": commit["commit"]["message"].split("\n")[0],  # Get first line of commit message
                            "sha": commit["sha"][:7]  # Short SHA
                        }
                        for commit in commits
                    ])

                    authors = commit_df["author"].unique()
                    # Create colors for each author evenly spaced
                    author_colors = {}
                    for i, author in enumerate(authors):
                        author_colors[author] = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
                    # author_colors = px.colors.qualitative.Plotly[:len(authors)]
                    
                    if not commit_df.empty:
                        # Format end_date with time component for proper filtering
                        # Both values need to be in UTC for proper comparison with GitHub dates
                        end_timestamp = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59).tz_localize('UTC')
                        
                        # Now all dates should have matching timezone info
                        filtered_commit_df = commit_df[commit_df["date"] <= end_timestamp]
                        
                        # Show stats about filtered data
                        total_commits = len(commit_df)
                        filtered_commits = len(filtered_commit_df)
                        
                        st.markdown(f"Showing **{filtered_commits}** commits out of **{total_commits}** total commits")
                        
                        if filtered_commit_df.empty:
                            st.warning(f"No commits found between {start_date} and {end_date}")
                        else:
                            # Sort by date
                            filtered_commit_df = filtered_commit_df.sort_values("date")
                            
                            # Commit history visualization
                            st.subheader("Commit History")
                            
                            # Group by date to count commits per day
                            commit_counts = filtered_commit_df.groupby(filtered_commit_df["date"].dt.date).size().reset_index()
                            commit_counts.columns = ["date", "count"]
                            
                            # Create commit activity line chart
                            fig = px.line(
                                commit_counts, 
                                x="date", 
                                y="count",
                                labels={"date": "Date", "count": "Number of Commits"},
                                markers=True
                            )
                            
                            fig.update_layout(
                                xaxis_title="Date",
                                yaxis_title="Number of Commits",
                                height=300,
                                margin=dict(l=10, r=10, t=10, b=10),
                                hovermode="x unified"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            

                            commit_graph_col, recent_commits_col = st.columns([2, 1])
                            with commit_graph_col:

                                # Create git graph visualization
                                st.subheader("Git Commit Graph")

                                if len(filtered_commit_df) > 0:
                                    # Add branch information to the commit data if available
                                    try:
                                        # Get branch data for the repository
                                        branches_data = fetch_branch_data(repository)
                                        
                                        # Create a lookup of branch tips (the latest commit on each branch)
                                        branch_tips = {}
                                        for branch in branches_data:
                                            branch_name = branch["name"]
                                            commit_sha = branch.get("commit", {}).get("sha", "")
                                            if commit_sha:
                                                branch_tips[commit_sha] = branch_name
                                        
                                        # Attempt to get full commit history with parent information
                                        # This requires additional API calls to get full commit details
                                        commits_with_parents = {}
                                        for commit in commits:
                                            sha = commit["sha"]
                                            parents = [p["sha"] for p in commit.get("parents", [])]
                                            commits_with_parents[sha] = {
                                                "sha": sha,
                                                "short_sha": sha[:7],
                                                "parents": parents,
                                                "date": pd.to_datetime(commit["commit"]["author"]["date"]),
                                                "author": commit["commit"]["author"]["name"],
                                                "message": commit["commit"]["message"].split("\n")[0]
                                            }
                                        
                                        # Find branches in the commit graph
                                        # Simplistic approach: a commit is on a branch if it's in the path from branch tip to root
                                        branches_for_commit = {}
                                        main_branch = "main"  # Default to main
                                        
                                        # Find the main branch name (main or master)
                                        for branch in branches_data:
                                            if branch["name"] in ["main", "master"]:
                                                main_branch = branch["name"]
                                                break
                                        
                                        # Sort commits by date
                                        sorted_commits = sorted(
                                            [commits_with_parents[sha] for sha in commits_with_parents], 
                                            key=lambda x: x["date"]
                                        )
                                        
                                        # Create a prettier git graph visualization
                                        # Assign y-positions for each commit to show branching
                                        commit_positions = {}
                                        branch_positions = {main_branch: 0}  # Main branch at y=0
                                        current_branches = set([main_branch])
                                        max_branch_pos = 0
                                        
                                        for commit in sorted_commits:
                                            sha = commit["sha"]
                                            short_sha = commit["short_sha"]
                                            
                                            # Check if commit is at the tip of any branches
                                            branch_name = None
                                            for branch_sha, br_name in branch_tips.items():
                                                if sha.startswith(branch_sha) or branch_sha.startswith(sha):
                                                    branch_name = br_name
                                                    break
                                            
                                            # Assign position based on branch
                                            if branch_name and branch_name not in branch_positions:
                                                max_branch_pos += 1
                                                branch_positions[branch_name] = max_branch_pos
                                                current_branches.add(branch_name)
                                            
                                            # Assign y position (default to 0 for main branch if we can't determine)
                                            y_pos = branch_positions.get(branch_name, 0) if branch_name else 0
                                            commit_positions[short_sha] = y_pos
                                            
                                            # Store branch info for the commit
                                            branches_for_commit[short_sha] = branch_name or main_branch
                                        
                                        # Create the enhanced visualization
                                        fig = go.Figure()
                                        
                                        # Add branch lines
                                        for branch_name, y_pos in branch_positions.items():
                                            # Get commits on this branch
                                            branch_commits = [
                                                commit for commit in sorted_commits 
                                                if branches_for_commit.get(commit["short_sha"]) == branch_name
                                            ]
                                            
                                            if branch_commits:
                                                # For vertical layout, swap x and y coordinates
                                                branch_y = [commit["date"] for commit in branch_commits]
                                                branch_x = [y_pos] * len(branch_commits)
                                                
                                                fig.add_trace(go.Scatter(
                                                    y=branch_y,
                                                    x=branch_x,
                                                    mode="lines",
                                                    line=dict(
                                                        color=px.colors.qualitative.Plotly[y_pos % len(px.colors.qualitative.Plotly)],
                                                        width=2
                                                    ),
                                                    name=branch_name,
                                                    hoverinfo="name",
                                                    showlegend=False,
                                                ))

                                        # Add merge lines between commits
                                        for commit in sorted_commits:
                                            if len(commit["parents"]) > 1:  # Merge commit
                                                for parent_sha in commit["parents"]:
                                                    parent_short_sha = parent_sha[:7]
                                                    if parent_short_sha in commit_positions and commit["short_sha"] in commit_positions:
                                                        # Draw merge line from parent to this commit
                                                        parent_pos = commit_positions[parent_short_sha]
                                                        commit_pos = commit_positions[commit["short_sha"]]
                                                        
                                                        if parent_pos != commit_pos:  # Only draw if on different branches
                                                            # Find parent commit object
                                                            parent_commit = next(
                                                                (c for c in sorted_commits if c["short_sha"] == parent_short_sha), 
                                                                None
                                                            )
                                                            
                                                            if parent_commit:
                                                                fig.add_trace(go.Scatter(
                                                                    y=[parent_commit["date"], commit["date"]],
                                                                    x=[parent_pos, commit_pos],
                                                                    mode="lines",
                                                                    line=dict(color="rgba(150,150,150,0.5)", width=1, dash="dot"),
                                                                    showlegend=False
                                                                ))

                                        # Add commits with colored nodes by author
                                        for commit in sorted_commits:
                                            short_sha = commit["short_sha"]
                                            if short_sha in commit_positions:
                                                fig.add_trace(go.Scatter(
                                                    y=[commit["date"]],
                                                    x=[commit_positions[short_sha]],
                                                    mode="markers+text",
                                                    marker=dict(
                                                        color=author_colors.get(commit["author"], "blue"),
                                                        size=12,
                                                        line=dict(color="darkblue", width=1)
                                                    ),
                                                    text=short_sha,
                                                    textposition="middle right",  # Text on the right side for vertical layout
                                                    textfont=dict(size=8),
                                                    hovertext=f"<b>{short_sha}</b><br>" +
                                                            f"Branch: {branches_for_commit.get(short_sha, 'unknown')}<br>" +
                                                            f"Author: {commit['author']}<br>" +
                                                            f"Date: {commit['date'].strftime('%Y-%m-%d %H:%M')}<br>" +
                                                            f"Message: {commit['message']}",
                                                    hoverinfo="text",
                                                    name=commit["author"],
                                                    showlegend=False
                                                ))

                                        # Layout customization for vertical layout
                                        fig.update_layout(
                                            height=max(600, min(len(sorted_commits) * 15, 1400)),  # Height based on commit count
                                            width=max(500, 100 + (max_branch_pos + 1) * 50),  # Width based on branch count
                                            yaxis_title="Commit Date",
                                            xaxis=dict(
                                                title="Branches",
                                                tickmode="array",
                                                tickvals=list(branch_positions.values()),
                                                ticktext=list(branch_positions.keys()),
                                                showgrid=True,
                                                gridcolor="rgba(200,200,200,0.2)"
                                            ),
                                            plot_bgcolor="rgba(250,250,250,1)",
                                            margin=dict(l=10, r=50, t=50, b=10),  # Add more right margin for commit text
                                            hovermode="closest",
                                            legend=dict(
                                                title="Branches",
                                                orientation="h",  # Horizontal legend
                                                yanchor="bottom",
                                                y=1.02,  # Position at the top
                                                xanchor="center",
                                                x=0.5  # Center horizontally
                                            )
                                        )

                                        # Reverse y-axis so that newer commits are at the top
                                        fig.update_layout(yaxis=dict(autorange="reversed"))

                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                    except Exception as e:
                                        st.warning(f"Could not create enhanced git graph visualization: {str(e)}")
                                        # Fall back to simple visualization
                                        create_simple_git_graph(filtered_commit_df, author_colors)
                                else:
                                    st.info("No commits available to display in the graph.")
                            
                            with recent_commits_col:                            
                                # Add author legend
                                st.subheader("Commit Authors")

                                for i, (author, color) in enumerate(author_colors.items()):
                                    st.markdown(
                                        f"<div style='display: flex; align-items: center;'>"
                                        f"<div style='width: 12px; height: 12px; background-color: {color}; "
                                        f"margin-right: 8px; border-radius: 50%;'></div>"
                                        f"{author}</div>",
                                        unsafe_allow_html=True
                                    )                                # Recent commits table
                            
                                # Get branch data
                                branches = fetch_branch_data(repository)
                                branch_names = [branch["name"] for branch in branches]

                                # Display branch information
                                st.subheader("Repository Branches")
                                st.write(f"This repository has {len(branches)} branches:")
                                bullet_text = '\n'.join(['1. ' + branch_name for branch_name in branch_names])
                                st.markdown(bullet_text)

                                st.subheader("10 Most Recent Commits")
                                
                                # Format commit dataframe for display
                                display_df = filtered_commit_df.copy()
                                display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d %H:%M")
                                
                                # Show the most recent 10 commits (reversed order)
                                st.dataframe(
                                    display_df[["date", "author", "message", "sha"]].sort_values("date", ascending=False).head(10),
                                    use_container_width=True,
                                    height=400
                                )
                            
                            # Contributor analysis within date range
                            st.subheader(f"Contributor Analysis ({start_date} to {end_date})")
                            
                            # Calculate contributions within the filtered date range
                            author_counts = filtered_commit_df["author"].value_counts().reset_index()
                            author_counts.columns = ["name", "contributions"]
                            
                            if not author_counts.empty:
                                # Create contributor pie chart for filtered dates
                                fig = px.pie(
                                    author_counts,
                                    names="name",
                                    values="contributions",
                                    title="Contribution Distribution",
                                    hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Plotly
                                )
                                
                                fig.update_layout(
                                    height=400,
                                    margin=dict(l=10, r=10, t=50, b=10)
                                )
                                
                                col1, col2 = st.columns([3, 2])
                                
                                with col1:
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                with col2:
                                    # Calculate stats
                                    total_contributors = len(author_counts)
                                    total_commits = author_counts["contributions"].sum()
                                    avg_commits = total_commits / total_contributors if total_contributors > 0 else 0
                                    top_contributor = author_counts.iloc[0]["name"] if not author_counts.empty else "N/A"
                                    top_contributions = author_counts.iloc[0]["contributions"] if not author_counts.empty else 0
                                    
                                    st.metric("Contributors in Period", total_contributors)
                                    st.metric("Commits in Period", total_commits)
                                    st.metric("Average Commits per Contributor", f"{avg_commits:.1f}")
                                    st.metric("Top Contributor", f"{top_contributor} ({top_contributions} commits)")
                            else:
                                st.info("No contribution data available for the selected date range.")

                    else:
                        st.info("No commit data available for this repository.")
                    
                    # Add commit distribution by weekday
                    if not commit_df.empty and not filtered_commit_df.empty:
                        st.subheader("Commit Distribution by Weekday")
                        
                        # Add weekday to filtered dataframe
                        filtered_commit_df['weekday'] = filtered_commit_df['date'].dt.day_name()
                        
                        # Count commits by weekday
                        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        weekday_counts = filtered_commit_df['weekday'].value_counts().reindex(weekday_order).reset_index()
                        weekday_counts.columns = ['Weekday', 'Count']
                        
                        # Create weekday distribution chart
                        fig = px.bar(
                            weekday_counts,
                            x='Weekday',
                            y='Count',
                            color='Count',
                            color_continuous_scale='Viridis',
                            labels={'Count': 'Number of Commits', 'Weekday': 'Day of Week'}
                        )
                        
                        fig.update_layout(
                            xaxis_title="Day of Week",
                            yaxis_title="Number of Commits",
                            height=300,
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate which day had the most commits
                        most_active_day = weekday_counts.loc[weekday_counts['Count'].idxmax()]
                        st.markdown(f"**Most active day of the week:** {most_active_day['Weekday']} with {most_active_day['Count']} commits")