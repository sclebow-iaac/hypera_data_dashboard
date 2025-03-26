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
from project_statistics_components.network import get_project_data
# Define data for the dashboard

team_members = [
    {
        'name': 'Scott Lebow',
        'link': 'https://blog.iaac.net/user/sclebow/',
    },
    {
        'name': 'Mahnoor Fatima',
        'link': 'https://blog.iaac.net/user/mahnoor/',
    },
    {
        'name': 'Biel Pitman',
        'link': 'https://blog.iaac.net/user/bielpitman/'
    }
]

def run(container=None):
    left_margin, content_container, right_margin = get_content_container_columns()

    with content_container:
        # Set up the page title and layout
        display_page_title('Data')

        # Display the team members
        display_team_members(st.container(), team_members)

        if container is None:
            container = st.container()

        with container:
            # Create tabs for the dashboard
            st.markdown('### Select a tab to view the project statistics')
            model_inspector_tab, overall_statistics_tab, metric_analysis_tab, dashboard_metrics_tab = \
                st.tabs(["Model Inspector", "Overall Project Statistics", "Metric Analysis", "Dashboard Analytics"])
            
            # Get the project data
            project_tree, project_id = get_project_data()

            with model_inspector_tab:
                model_inspector.run(project_tree, project_id)

            with overall_statistics_tab:
                st.write('This tab shows the overall statistics of the entire project')
                overall_statistics.run(project_tree, project_id)

            with metric_analysis_tab:
                metric_analysis.run(project_tree, project_id)

            with dashboard_metrics_tab:
                # Add dashboard metrics here
                st.subheader("Dashboard Analytics")
                st.write('This tab displays data from the Dashboard Github Repository')
                dashboard_metrics.run()
