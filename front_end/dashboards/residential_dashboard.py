import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.residential_extractor as team_extractor

from dashboards.dashboard import *

def metric_calc_index(number_of_units, unit_types, total_number_of_units):
    numerator = sum(float(units) * (float(units) - 1) for units in number_of_units)
    denominator = float(total_number_of_units) * (float(total_number_of_units) - 1)
    return 1 - (numerator / denominator) if denominator != 0 else None

def metric_interactive_calculator_index(container, number_of_units, unit_types, total_number_of_units):
    with container:
        st.markdown("### Mixed Use Index Calculator")
        number_of_units_slider = st.slider("Number of Units", 0, 100, 50, help="Adjust number of units")
        total_number_of_units_slider = st.slider("Total Number of Units", 1, 100, 50, help="Adjust total number of units")
        new_index_value = metric_calc_index([number_of_units_slider] * len(unit_types), [], total_number_of_units_slider)
        st.markdown(f"### Resulting Index: {new_index_value:.2f}")

# Define the function to run the dashboard
def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False,
                                header=True, show_table=True, gauge=False, simple_table=True)
    
    # Create a container for the slideshow and iframe
    container = st.container()
    
    # Create two equal columns
    col1, col2 = container.columns(2)  # Both columns will have equal width

    # In the first column, display the image slideshow
    with col1:
        display_image_slideshow(col1, "./front_end/dashboards/pictures", "slideshow_2")

    # In the second column, display the iframe for the Speckle model
    with col2:
        iframe_code = f"""
        <iframe src="https://macad.speckle.xyz/projects/31f8cca4e0/models/000e6c757a" 
                style="width: 100%; height: 600px; border: none;">
        </iframe>
        """
        st.markdown(iframe_code, unsafe_allow_html=True)



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
        total_number_of_units = sum(float(x) for x in number_of_units)

    metrics = []

    index_metric = Metric(
        "Mixed Use Index",
        r'1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}',
        "Measures the diversity of unit types in the project.",
        metric_interactive_calculator_index,
        metric_calc_index,
        './front_end/dashboards/pictures/residential.png',
        [
            {
                "name": "Number of Units",
                "value": number_of_units,
                "display_value": sum(float(x) for x in number_of_units),
                "unit": ""
            },
            {
                "name": "Unit Types",
                "value": unit_types,
                "display_value": len(unit_types),
                "unit": ""
            },
            {
                "name": "Total Number of Units",
                "value": total_number_of_units,
                "display_value": sum(float(x) for x in number_of_units),
                "unit": ""
            }
        ]
    )
    metrics.append(index_metric)

    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)

    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Mixed Use Index optimized for safety",
        "2. Efficient use of materials",
        "3. Compliance with building codes"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)


    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)
    
    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)
    
    metrics_visualization_container = st.container()
    display_metric_visualizations(metrics_visualization_container, metrics, add_text=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(
        metric_interactive_calculator_container, metrics, grid=True)
