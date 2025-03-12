import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer
# 1. Imports and Setup
import data_extraction.facade_extractor as team_extractor  # Only import the extractor module
from dashboards.dashboard import *


def metric_calc_daylight_factor(weight_residential, weight_work, residential_area_with_daylight, total_residential_area, work_area_with_daylight, total_work_area):
    return (
        weight_residential * (residential_area_with_daylight / total_residential_area) +
        weight_work * (work_area_with_daylight / total_work_area)
    )

def metric_calc_energy_ratio(energy_generation, energy_required_by_industrial_team):
    return energy_generation / energy_required_by_industrial_team

def metric_calc_panel_optimization(total_final_panel_area, total_initial_panel_area):
    return total_final_panel_area / total_initial_panel_area

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)
    if not verified:
        st.error("Failed to extract data, proceeding with Example Data. Use Data Dashboard to Investigate.")
        team_extractor.display_data(extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)
        # Example data
        energy_generation = 1500  # kWh
        energy_required_by_industrial_team = 1000  # kWh

        weight_residential = 0.5
        weight_work = 0.5
        residential_area_with_daylight = 100
        total_residential_area = 200
        work_area_with_daylight = 150
        total_work_area = 300

        total_final_panel_area = 100
        total_initial_panel_area = 200

    else:
        # Extracted data
        energy_generation = team_data['EnergyGeneration']
        energy_required_by_industrial_team = team_data['EnergyRequiredByIndustrialTeam']
        weight_residential = 0.5
        weight_work = 0.5
        residential_area_with_daylight = team_data['ResidentialAreaWithDaylight']
        total_residential_area = team_data['TotalResidentialArea']
        work_area_with_daylight = team_data['WorkAreaWithDaylight']
        total_work_area = team_data['TotalWorkArea']

        total_final_panel_area = team_data['TotalFinalPanelArea']
        total_initial_panel_area = team_data['TotalInitialPanelArea']
    
    metrics = []

    daylight_factor_metric = Metric(
        "Primary Daylight Factor & and Solar Loads Control for Residential Spaces and Work Spaces",
        r'w_{resi}\frac{ResidentialAreaWithDaylight}{TotalResidentialArea} + w_{work}\frac{WorkAreaWithDaylight}{TotalWorkArea}',
        "Measures the proportion of floor area that receives daylight.",
        metric_calc_daylight_factor,
        './front_end/dashboards/pictures/daylight.png',
        [
            {
                "name": "Weight Residential",
                "value": weight_residential,
                "unit": ""
            },
            {
                "name": "Weight Work",
                "value": weight_work,
                "unit": ""
            },
            {
                "name": "Residential Area with Daylight",
                "value": residential_area_with_daylight,
                "unit": "m²"
            },
            {
                "name": "Total Residential Area",
                "value": total_residential_area,
                "unit": "m²"
            },
            {
                "name": "Work Area with Daylight",
                "value": work_area_with_daylight,
                "unit": "m²"
            },
            {
                "name": "Total Work Area",
                "value": total_work_area,
                "unit": "m²"
            }
        ],
        min_value=0,
        max_value=0.1,
        ideal_value=0.05
    )
    metrics.append(daylight_factor_metric)

    panel_optimization_metric = Metric(
        "Panel Optimization",
        r'\frac {Total Final Panel Area}{Total Initial Panel Area}',
        "Measures the efficiency of panel area usage.",
        metric_calc_panel_optimization,
        './front_end/dashboards/pictures/panel.png',
        [
            {
                "name": "Total Final Panel Area",
                "value": total_final_panel_area,
                "min": 0,
                "max": 2000,
                "unit": "m²"
            },
            {
                "name": "Total Initial Panel Area",
                "value": total_initial_panel_area,
                "min": 1,
                "max": 2000,
                "unit": "m²"
            }
        ],
        min_value=0,
        max_value=1,
        ideal_value=1.0
    )
    metrics.append(panel_optimization_metric)
    
    energy_ratio_metric = Metric(
        "Energy Generation Ratio",
        r'\frac{Energy Produced}{Energy Needed}',
        "Measures the ratio of energy generation to energy requirements.",
        metric_calc_energy_ratio,
        './front_end/dashboards/pictures/energy.png',
        [
            {
                "name": "Energy Generation",
                "value": energy_generation,
                "unit": "kWh"
            },
            {
                "name": "Energy Required by Industrial Team",
                "value": energy_required_by_industrial_team,
                "unit": "kWh"
            }
        ],
        min_value=0,
        max_value=2,
        ideal_value=1
    )
    metrics.append(energy_ratio_metric)

    team_members = [
        {
            'name': 'Andrea Ardizzi',
            'link': 'https://blog.iaac.net/user/andrea.ardizzi/',
        },
        {
            'name': 'Christina Christoforou',
            'link': 'https://blog.iaac.net/user/christina153/',
        },
        {
            'name': 'Giulia Tortorella',
            'link': 'https://blog.iaac.net/user/giulia+tortorella/'
        }
    ]

    text_dict = {
        'design_overview': 'Our facade design integrates sustainable features with aesthetic considerations.',
        'bullet_items': [
            "1. Solar panels optimized for maximum energy generation",
            "2. Strategic window placement for natural daylight",
            "3. Thermal insulation systems for energy efficiency"
        ]
    }

    presentation_model_id = '29bc37af8e'

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

    # OLD STUFF BELOW HERE
    st.markdown('---')
    st.markdown('---')
    st.title('OLD STUFF BELOW TO BE REMOVED')
    st.markdown('---')
    st.markdown('---')
    st.title(f"{selected_team} Dashboard")

    # Create two equal columns
    col1, col2 = st.columns(2)  # Both columns will have equal width

    # # In the first column, display the image slideshow
    # with col1:

    #     # Create a container for the slideshow
    #     container = st.container()
        
        # Call the display_image_slideshow function
        # Example usage
        # folder_path = "./front_end/dashboards/pictures"  # Update this to your actual image folder path
        # display_image_slideshow(container, folder_path, "facade_slideshow")  # Change interval as needed


    # In the second column, display the iframe for the Speckle model
    with col2:
        container = st.container()
        display_speckle_viewer(container, '31f8cca4e0', '29bc37af8e', is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False)
        container.markdown("https://macad.speckle.xyz/projects/31f8cca4e0/models/29bc37af8e" , unsafe_allow_html=True)


    # Building Dashboard
    # Dashboard Header
    # display_page_title(selected_team)
    # team_extractor.display_data(extracted_data=team_data, verbose=False, header=True, show_table=False, gauge=False, simple_table=True)


    # Building Dashboard
   
    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## Facade Design Overview
        Our facade design integrates sustainable features with aesthetic considerations.
        """
    )


    st.markdown("---")

    st.write(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=True)


    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Solar panels optimized for maximum energy generation",
        "2. Strategic window placement for natural daylight",
        "3. Thermal insulation systems for energy efficiency"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    st.markdown(" ")
    st.markdown(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)

    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## Detailed KPI Explanations
        """
    )

    st.markdown(" ")
    st.markdown(" ")

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
