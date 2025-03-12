import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.residential_extractor as team_extractor

from dashboards.dashboard import *

# Define data for the dashboard
team_members = [
    {
        'name': 'Amira ElSaeed',
        'link': 'https://blog.iaac.net/user/amira/',
    },
    {
        'name': 'Aleyna Kırcalı',
        'link': 'https://blog.iaac.net/user/aleyna/',
    },
    {
        'name': 'Mohamed Attay',
        'link': 'https://blog.iaac.net/user/mohamed_attay/',
    },
]    

text_dict = {
    'design_overview': 'Our residential design integrates sustainable features with aesthetic considerations.',
    'bullet_items': [
        "1. Mixed Use Index optimized for safety",
        "2. Efficient use of materials",
        "3. Compliance with building codes"
    ]
}

presentation_model_id = '000e6c757a'

def metric_calc_index(number_of_units, unit_types, total_number_of_units):
    numerator = sum(float(units) * (float(units) - 1) for units in number_of_units)
    denominator = float(total_number_of_units) * (float(total_number_of_units) - 1)
    return 1 - (numerator / denominator) if denominator != 0 else None

# Define the function to run the dashboard
def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)
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
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 0.7
    )
    metrics.append(index_metric)

    generate_dashboard(
        selected_team=selected_team,
        metrics=metrics,
        project_id=project_id,
        team_members=team_members,
        team_extractor=team_extractor,
        extracted_data=team_data,
        text_dict=text_dict,
        presentation_model_id=presentation_model_id
    )

    # # Building Dashboard
    # # Dashboard Header
    # display_page_title(selected_team)
    # team_extractor.display_data(extracted_data=team_data, verbose=False,
    #                             header=False, show_table=False, gauge=False, simple_table=True)
    
    # # Create two equal columns
    # col1, col2 = st.columns(2)  # Both columns will have equal width

    # # In the first column, display the image slideshow
    # with col1:

    #     # Create a container for the slideshow
    #     container = st.container()
        
    #     # Call the display_image_slideshow function
    #     # Example usage
    #     folder_path = "./front_end/dashboards/pictures"  # Update this to your actual image folder path
    #     display_image_slideshow(container, folder_path, "facade_slideshow")  # Change interval as needed


    # # In the second column, display the iframe for the Speckle model
    # with col2:
    #     container = st.container()
    #     display_speckle_viewer(container, '31f8cca4e0', '000e6c757a', is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False)
    #     container.markdown("https://macad.speckle.xyz/projects/31f8cca4e0/models/000e6c757a" , unsafe_allow_html=True)



    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)

    # st.markdown(" ")
    # st.markdown(" ")

    # # Now, display the custom bullet list underneath the iframe and STL model

    # display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    # st.markdown(" ")
    # st.markdown(" ")
    # st.markdown(" ")
    # st.markdown(" ")
    # st.markdown(" ")

    # team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)


    # # # Display Formulas and Explanations
    # # display_formula_section_header(selected_team)
    
    # # Metrics Display - Updated with correct metrics
    # metrics_display_container = st.container()
    # display_st_metric_values(metrics_display_container, metrics)
    
    # metrics_visualization_container = st.container()
    # display_metric_visualizations(metrics_visualization_container, metrics, add_text=True)

    # # Interactive Calculators
    # metric_interactive_calculator_container = st.container()
    # display_interactive_calculators(
    #     metric_interactive_calculator_container, metrics, grid=True)
