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

import project_statistics_components.dashboard_metrics as dashboard_metrics
import project_statistics_components.model_inspector as model_inspector
import project_statistics_components.overall_statistics as overall_statistics
import project_statistics_components.metric_analysis as metric_analysis

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

def run(container=None):


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
                model_inspector.run(project_tree, project_id)

            with overall_statistics_tab:
                overall_statistics.run(project_tree, project_id)

            with metric_analysis_tab:
                metric_analysis.run(project_tree, project_id)

            with dashboard_metrics_tab:
                dashboard_metrics.run()
