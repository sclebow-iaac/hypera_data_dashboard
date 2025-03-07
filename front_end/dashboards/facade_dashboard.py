import streamlit as st
from pythreejs import *

# 1. Imports and Setup
import data_extraction.facade_extractor as team_extractor  # Only import the extractor module
from dashboards.dashboard import (
    display_stl_model,
    display_metric_circles_and_tape,
    display_image_slideshow,
    display_kpi_details
)

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
    st.title(f"{selected_team} Dashboard")

    # Call the slideshow function
    slideshow_container = st.container()
    display_image_slideshow(slideshow_container, folder_path='./front_end/dashboards/pictures')  # Update the path to your images


    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Check if data extraction was successful
    if not verified:
        st.error("Failed to extract data, proceeding with Example Data. Use Data Dashboard to Investigate.")
        return  # Exit if data extraction fails

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
        weight_residential, 
        weight_work, 
        residential_area_with_daylight, 
        total_residential_area, 
        work_area_with_daylight, 
        total_work_area
    )
    metrics.append(daylight_factor_metric)

    panel_optimization_metric = Metric(
        "Panel Optimization",
        r'\frac {Total Final Panel Area}{Total Initial Panel Area}',
        "Measures the efficiency of panel area usage.",
        metric_calc_panel_optimization,
        total_final_panel_area,
        total_initial_panel_area
    )
    metrics.append(panel_optimization_metric)
    
    energy_ratio_metric = Metric(
        "Energy Generation Ratio",
        r'\frac{Energy Produced}{Energy Needed}',
        "Measures the ratio of energy generation to energy requirements.",
        metric_calc_energy_ratio,
        energy_generation,
        energy_required_by_industrial_team
    )
    metrics.append(energy_ratio_metric)

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

    # Add KPI section
    kpi_container = st.container()
    kpi_data = [
        {
            'title': 'Primary Daylight Factor',
            'image_path': './front_end/dashboards/pictures/daylight.png',
            'name': 'Natural Light Optimization',
            'metric_value': daylight_factor_metric.calculate(),
            'metric_description': 'Daylight coverage ratio',
            'detailed_description': 'The Primary Daylight Factor measures how effectively our facade design maximizes natural light penetration. It considers both residential and work spaces, ensuring optimal daylight distribution while managing solar heat gain.'
        },
        {
            'title': 'Panel Optimization',
            'image_path': './front_end/dashboards/pictures/panel.png',
            'name': 'Solar Panel Efficiency',
            'metric_value': panel_optimization_metric.calculate(),
            'metric_description': 'Panel area optimization ratio',
            'detailed_description': 'Panel Optimization quantifies how efficiently we utilize solar panel area. This metric compares the final panel configuration against the initial layout, showing improvements in energy generation capacity per square meter.'
        },
        {
            'title': 'Energy Generation',
            'image_path': './front_end/dashboards/pictures/energy.png',
            'name': 'Energy Production',
            'metric_value': energy_ratio_metric.calculate(),
            'metric_description': 'Energy generation ratio',
            'detailed_description': 'The Energy Generation metric represents the ratio between energy produced and energy needed. This helps us understand how well our facade-integrated solar solutions meet the building\'s energy demands.'
        }
    ]



    # # Create two columns for the iframe and STL model
    # col1, col2 = st.columns(2)

    # # Create an iframe for the Speckle model in the first column
    # speckle_model_url = "https://macad.speckle.xyz/projects/31f8cca4e0/models/5adade2d5f"  # Replace with your actual Speckle model URL
    # iframe_code = f"""
    # <iframe src="{speckle_model_url}" 
    #         style="width: 100%; height: 600px; border: none;">
    # </iframe>
    # """

    # # Display the iframe in the first column
    # with col1:
    #     st.markdown(iframe_code, unsafe_allow_html=True)

    # # In the second column, display the STL model
    # with col2:
    #     display_stl_model(
    #         file_path='./front_end/dashboards/models/model_studio.stl',  # Use a single model path
    #         color="#808080",  # Change color to grey
    #         key='facade_stl_model_display'
    #     )

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Solar panels optimized for maximum energy generation",
        "2. Strategic window placement for natural daylight",
        "3. Thermal insulation systems for energy efficiency"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    
    
    # Display detailed KPI explanations
    kpi_details_container = st.container()
    display_kpi_details(kpi_details_container, kpi_data)


    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
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


    # Call the display function for the Primary Daylight Factor
    display_metric_circles_and_tape(
        st.container(),
        title="Primary Daylight Factor",
        primary_metric_value=daylight_factor_metric.calculate(),
        metric_values=[weight_residential, weight_work, residential_area_with_daylight, total_residential_area, work_area_with_daylight, total_work_area],
        metric_names=["Weight Residential", "Weight Work", "Residential Area with Daylight", "Total Residential Area", "Work Area with Daylight", "Total Work Area"],
        units="m²"  # All units are in meters
    )

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # Call the panel optimization metric display
    display_metric_circles_and_tape(
        st.container(),
        title="Panel Optimization",
        primary_metric_value=panel_optimization_metric.calculate(),
        metric_values=[total_final_panel_area, total_initial_panel_area],
        metric_names=["Total Final Panel Area", "Total Initial Panel Area"],
        units="m²"  # Units for panel area
    )

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # Call the display function for the Energy Ratio
    display_metric_circles_and_tape(
        container=st.container(),
        title="Energy Generation Ratio",
        primary_metric_value=energy_ratio_metric.calculate(),
        metric_values=[energy_generation, energy_required_by_industrial_team],
        metric_names=["Energy Generation", "Energy Required by Industrial Team"],
        units="kWh"  # Adjust units as necessary
    )


