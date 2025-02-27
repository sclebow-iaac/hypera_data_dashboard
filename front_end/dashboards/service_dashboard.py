import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.service_extractor as team_extractor
import pandas as pd
import plotly.express as px

from dashboards.dashboard import *

def metric_calc_occupancy_efficiency(utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_spaces_available):
    return (utilization_rate * active_hours * function_exchange_factor) / (total_available_hours_per_day * total_spaces_available)

def metric_interactive_calculator_occupancy_efficiency(container, utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_spaces_available):
    with container:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("### Occupancy Efficiency Calculator")
            utilization_rate_slider = st.slider("Utilization Rate (%)", 0, 100, int(utilization_rate), help="Percentage of space utilization")
            active_hours_slider = st.slider("Active Hours", 0, 24, int(active_hours), help="Hours of active use per day")
            function_exchange_factor_slider = st.slider("Function Exchange Factor", 1, 10, int(function_exchange_factor), help="Multiplier for function flexibility")
            total_available_hours_per_day_slider = st.slider("Total Available Hours per Day", 1, 24, int(total_available_hours_per_day), help="Total hours available per day")
            total_spaces_available_slider = st.slider("Total Spaces Available", 1, 100, int(total_spaces_available), help="Total number of spaces")
            new_occupancy_efficiency = metric_calc_occupancy_efficiency(
                utilization_rate_slider,
                active_hours_slider,
                function_exchange_factor_slider,
                total_available_hours_per_day_slider,
                total_spaces_available_slider
            )
            st.markdown(f"### Occupancy Efficiency: {new_occupancy_efficiency:.2f}")
        with col_2:
            # Create dynamic sphere for occupancy efficiency
            dynamic_occupancy_efficiency_sphere = create_sphere_visualization(
                "dynamic-occupancy-efficiency-sphere",
                new_occupancy_efficiency,
                "Occupancy Efficiency",
                height=200
            )
            st.components.v1.html(dynamic_occupancy_efficiency_sphere, height=250)

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False, header=True, show_table=True, gauge=False, simple_table=True)

    if not verified:
        st.error("Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        occupancy_efficiency = 80
        utilization_rate = 34
        n = 5
        active_hours = 12
        function_exchange_factor = 4
        total_available_hours_per_day = 13
        total_spaces_available = 50
    else:
        
        occupancy_efficiency = 80
        utilization_rate = 34
        n = 5
        active_hours = 12
        function_exchange_factor = 4
        total_available_hours_per_day = 13
        total_spaces_available = 50

    metrics = []

    occupancy_efficiency_metric = Metric(
        "Occupancy Efficiency",
        r'\frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor)}{TotalAvailableHoursPerDay \cdot TotalSpacesAvailable}',
        "Measures the efficiency of space utilization throughout the day.",
        metric_interactive_calculator_occupancy_efficiency,
        metric_calc_occupancy_efficiency,
        utilization_rate, 
        active_hours, 
        function_exchange_factor, 
        total_available_hours_per_day, 
        total_spaces_available    
    )

    metrics.append(occupancy_efficiency_metric)

    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)
    
    metrics_visualization_container = st.container()
    display_metric_visualizations(metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)
    