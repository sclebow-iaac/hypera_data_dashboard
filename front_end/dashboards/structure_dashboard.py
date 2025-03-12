import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.structure_extractor as team_extractor
from dashboards.dashboard import *

def metric_calc_column_free_floor_area_ratio(total_column_free_floor_area, total_floor_area):
    return float(total_column_free_floor_area) / float(total_floor_area)


def metric_calc_load_capacity_per_square_meter(load_capacity, self_weight_of_structure):
    return float(load_capacity) / float(self_weight_of_structure)

def run(selected_team: str) -> None:

     # Create two equal columns
    col1, col2 = st.columns(2)  # Both columns will have equal width

    # In the first column, display the image slideshow
    with col1:

        # Create a container for the slideshow
        container = st.container()
        
        # Call the display_image_slideshow function
        # Example usage
        folder_path = "./front_end/dashboards/pictures"  # Update this to your actual image folder path
        display_image_slideshow(container, folder_path, "facade_slideshow")  # Change interval as needed


    # In the second column, display the iframe for the Speckle model
    with col2:
        container = st.container()
        display_speckle_viewer(container, '31f8cca4e0', 'c2df017258', is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False)
        container.markdown("https://macad.speckle.xyz/projects/31f8cca4e0/models/c2df017258" , unsafe_allow_html=True)

    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    if not verified:
        st.error(
            "Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        # Example data
        total_column_free_floor_area = 800
        total_floor_area = 1000
        load_capacity = 800
        self_weight_of_structure = 500

    else:
        # Extracted data
        total_column_free_floor_area = float(
        team_data['TotalColumnFreeFloorArea'])
        total_floor_area = float(team_data['TotalFloorArea'])
        load_capacity = float(team_data['LoadCapacity'])
        self_weight_of_structure = float(team_data['SelfWeightOfStructure'])

    metrics = []

    column_free_floor_area_metric = Metric(
        "Column-Free Floor Area Ratio",
        r'\frac{Total Column-Free Floor Area (m²)}{Total Floor Area (m²)}',
        "Ratio of column-free floor area to total floor area",
        metric_calc_column_free_floor_area_ratio,
        './front_end/dashboards/pictures/column.png',
        [
            {
                "name": "Total Column-Free Floor Area",
                "value": total_column_free_floor_area,
                "unit": "m²"
            },
            {
                "name": "Total Floor Area",
                "value": total_floor_area,
                "unit": "m²"
            }
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 0.5
    )
    metrics.append(column_free_floor_area_metric)

    load_capacity_metric = Metric(
        "Load Capacity per Square Meter",
        r'\frac{Load Capacity (kg)}{Self Weight of Structure (kg)}',
        "Ratio of load capacity to self weight of structure",
        metric_calc_load_capacity_per_square_meter,
        './front_end/dashboards/pictures/load.png',
        [
            {
                "name": "Load Capacity",
                "value": load_capacity,
                "unit": "kg"
            },
            {
                "name": "Self Weight of Structure",
                "value": self_weight_of_structure,
                "unit": "kg"
            }
        ],
        min_value = 0,
        max_value = 3,
        ideal_value = 2
    )
    metrics.append(load_capacity_metric)

    # Building Dashboard
    text_container = st.container()
    display_text_section(
        text_container,
        """
        ##
        Our structure design emphasizes safety, efficiency, and sustainability. We focus on optimizing space while ensuring structural integrity.
        """
    )

    st.markdown("---")

    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Structural integrity optimized for safety",
        "2. Efficient use of materials",
        "3. Compliance with building codes"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    st.markdown(" ")
    st.markdown(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)

    
    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")


    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    metrics_visualization_container = st.container()
    display_metric_visualizations(metrics_visualization_container, metrics, add_text=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)