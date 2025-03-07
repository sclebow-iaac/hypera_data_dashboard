import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.residential_extractor as team_extractor

from dashboards.dashboard import *

def metric_calc_index(number_of_units, unit_types, total_number_of_units):
    numerator = sum(units * (units - 1) for units in number_of_units)
    denominator = total_number_of_units * (total_number_of_units - 1)
    return 1 - (numerator / denominator) if denominator != 0 else None

def metric_interactive_calculator_index(container, number_of_units, unit_types, total_number_of_units):
    with container:
        st.markdown("### Mixed Use Index Calculator")
        number_of_units_slider = st.slider("Number of Units", 0, 100, 50, help="Adjust number of units")
        total_number_of_units_slider = st.slider("Total Number of Units", 1, 100, 50, help="Adjust total number of units")
        new_index_value = metric_calc_index([number_of_units_slider] * len(unit_types), [], total_number_of_units_slider)
        st.markdown(f"### Resulting Index: {new_index_value:.2f}")
        # Create dynamic sphere for index
        dynamic_index_sphere = create_sphere_visualization(
            "dynamic-index-sphere",
            new_index_value,
            "Mixed Use Index",
            height=200
        )
        st.components.v1.html(dynamic_index_sphere, height=250)

# Define the function to run the dashboard
def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False, header=True, show_table=True, gauge=False, simple_table=True)

    if not verified:
        st.error("Failed to extract data, proceeding with Example Data. Use Data Dashboard to Investigate.")
        team_extractor.display_data(extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)
        # Example data
        number_of_units = [40, 60, 30, 20]
        unit_types = ['Housing', 'Social', 'Commercial', 'Open Space']
        total_number_of_units = sum(number_of_units)
    
    else:
        # Extracted data
        number_of_units = team_data['NumberOfUnitsOfASingleFunction']
        unit_types = team_data['ListOfUnitFunctions']
        total_number_of_units = sum(number_of_units)

    metrics = []

    index_metric = Metric(
        "Mixed Use Index",
        r'1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}',
        "Measures the diversity of unit types in the project.",
        metric_interactive_calculator_index,
        metric_calc_index,
        number_of_units,
        unit_types,
        total_number_of_units
    )
    metrics.append(index_metric)

    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)

    metrics_visualization_container = st.container()
    display_metric_visualizations(
        metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(
        metric_interactive_calculator_container, metrics, grid=True)
