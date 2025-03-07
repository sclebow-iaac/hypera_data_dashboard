import streamlit as st
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.residential_extractor as team_extractor
# import pandas
import pandas as pd
# import plotly express
import plotly.express as px

from dashboards.dashboard import *

model_id = '000e6c757a'

def metric_calc_index(number_of_units, unit_types, total_number_of_units):
    numerator = sum(units * (units - 1) for units in number_of_units)
    denominator = total_number_of_units * (total_number_of_units - 1)
    return 1 - (numerator / denominator) if denominator != 0 else None


def metric_interactive_calculator_index(container, number_of_units, unit_types, total_number_of_units):
    with container:
        st.markdown("### Mixed Use Index Calculator")
        number_of_units_slider = st.slider(
            "Number of Units", 0, 100, 50, help="Adjust number of units")
        total_number_of_units_slider = st.slider(
            "Total Number of Units", 1, 100, 50, help="Adjust total number of units")
        new_index_value = metric_calc_index(
            [number_of_units_slider] * len(unit_types), [], total_number_of_units_slider)
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
    verified, team_data = team_extractor.extract(
        models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Display the Speckle model in an iframe
    viewer_container = st.container()
    speckle_model_url = display_speckle_viewer(
        container=viewer_container,
        project_id=project_id,
        model_id=model_id
    )

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False,
                                header=True, show_table=True, gauge=False, simple_table=True)

    print(f"Speckle Model URL: {speckle_model_url}")
   # # Call the slideshow function
    # slideshow_container = st.container()
    # display_image_slideshow(slideshow_container, folder_path='./front_end/dashboards/pictures')  # Update the path to your images

    if not verified:
        st.error(
            "Failed to extract data, proceeding with Example Data. Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)
        # Example data
        number_of_units = [40, 60, 30, 20]
        unit_types = ['Housing', 'Social', 'Commercial', 'Open Space']
        total_number_of_units = sum(number_of_units)

    else:
        # Extracted data
        number_of_units_strs = team_data['NumberOfUnitsOfASingleFunction']
        number_of_units = [int(number_of_units_str)
                           for number_of_units_str in number_of_units_strs]
        unit_types = team_data['ListOfUnitFunctions']
        total_number_of_units = sum(number_of_units)

    metrics = []

    index_metric = Metric(
        "Mixed Use Index",
        r'1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}',
        "Measures the diversity of unit types in the project.",
        metric_calc_index,
        number_of_units,
        unit_types,
        total_number_of_units
    )
    metrics.append(index_metric)

     # Building Dashboard
    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## Residential Design Overview
        Our residential design emphasizes safety, efficiency, and sustainability. We focus on optimizing space while ensuring structural integrity.
        """
    )

    st.markdown("---")
    

    # # In the second column, display the STL model
    # with col2:
    #     display_stl_model(
    #         file_path='./front_end/dashboards/models/model_studio.stl',  # Use a single model path
    #         color="#808080",  # Change color to grey
    #         key='structure_stl_model_display'
    #     )

    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Mixed Use Index optimized for safety",
        "2. Efficient use of materials",
        "3. Compliance with building codes"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    # Add KPI section
    kpi_data = [
        {
            'title': 'Mixed Use Index',
            'image_path': './front_end/dashboards/pictures/energy.png',
            'name': 'Mixed Use Index',
            'metric_value': index_metric.calculate(),
            'metric_description': 'Ratio of column-free floor area to total floor area.',
            'detailed_description': 'This metric indicates the efficiency of the floor space in the structure.'
        }
    ]    
    # Display detailed KPI explanations
    kpi_details_container = st.container()
    display_kpi_details(kpi_details_container, kpi_data)

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)

    # Calculate the sum of number_of_units for display
    total_units = sum(number_of_units)  # Sum of all units
    max_units = max(number_of_units)    # Maximum units in any category

    display_metric_circles_and_tape(
        st.container(),
        title="Mixed Use Index",
        primary_metric_value=index_metric.calculate(),
        metric_values=[max_units, total_units],  # Use scalar values instead of lists
        metric_names=["Maximum Units in Category", "Total Units"],
        units=""
    )

    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)
    
    # # Metrics Display - Updated with correct metrics
    # metrics_display_container = st.container()
    # display_st_metric_values(metrics_display_container, metrics)
    
    # metrics_visualization_container = st.container()
    # display_metric_visualizations(metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # # Interactive Calculators
    # metric_interactive_calculator_container = st.container()
    # display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)