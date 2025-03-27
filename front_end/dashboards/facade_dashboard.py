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

# Define data for the dashboard
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
    'design_overview': 'We chose to frame our KEYPOINTS as open questions, the same ones that guided our design process. These questions reflect the challenges we faced and the strategies we developed to create a responsive, efficient, and integrated facade system. Through our project, we will explore and attempt to answer them',
    'bullet_items': [
        "1. Can a kinetic component applied to a facade help to improve thermal comfort and reduce glare and overheating?",
        "2. Can a facade concept be adapted to respond to different functions and light requirements?",
        "3. Can we optimize the number of different panels to create a buildable and cost-efficient design?",
        "4. Can a facade generate energy while optimizing the number of photovoltaic panels?",
        "5. How does collaboration between disciplines influence facade design decisions?"
    ]
}

presentation_model_id = '29bc37af8e'

def process_data(verified, team_data, model_data):
    if not verified:
        st.error("Failed to extract data, proceeding with Example Data. Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, model_data=model_data, header=False, show_table=False, gauge=True, simple_table=False)
        # Example data
        energy_generation = 1500  # kWh
        energy_required_by_industrial_team = 1000  # kWh

        # weight_residential = 0.5
        weight_residential = 1.0
        weight_work = 0.5
        residential_area_with_daylight = 100
        total_residential_area = 200
        # work_area_with_daylight = 150
        # total_work_area = 300

        number_optimized_panel_type = 100
        number_starting_panel_type = 200

    else:
        # Extracted data
        energy_generation = team_data['EnergyGeneration']
        energy_required_by_industrial_team = team_data['EnergyRequiredByIndustrialTeam']
        weight_residential = 1.0
        weight_work = 0.5
        residential_area_with_daylight = team_data['ResidentialAreaWithDaylight']
        total_residential_area = team_data['TotalResidentialArea']
        # work_area_with_daylight = team_data['WorkAreaWithDaylight']
        # total_work_area = team_data['TotalWorkArea']

        number_optimized_panel_type = team_data['NumberOptimizedPanelType']
        number_starting_panel_type = team_data['NumberStartingPanelType']

    # Cast to float
    energy_generation = float(energy_generation)
    energy_required_by_industrial_team = float(energy_required_by_industrial_team)
    weight_residential = float(weight_residential)
    weight_work = float(weight_work)
    residential_area_with_daylight = float(residential_area_with_daylight)
    total_residential_area = float(total_residential_area)
    # work_area_with_daylight = float(work_area_with_daylight)
    # total_work_area = float(total_work_area)
    number_optimized_panel_type = float(number_optimized_panel_type)
    number_starting_panel_type = float(number_starting_panel_type)

    return (energy_generation, energy_required_by_industrial_team,
            weight_residential, weight_work,
            residential_area_with_daylight, total_residential_area,
            # work_area_with_daylight, total_work_area,
            number_optimized_panel_type, number_starting_panel_type)

# def metric_calc_daylight_factor(weight_residential, weight_work, residential_area_with_daylight, total_residential_area, work_area_with_daylight, total_work_area):
def metric_calc_daylight_factor(weight_residential, weight_work, residential_area_with_daylight, total_residential_area):
    # Avoid division by zero
    if total_residential_area == 0:
        total_residential_area = 1
        st.warning("Total Residential Area is zero, setting to 1 to avoid division by zero.")
    # if total_work_area == 0:
    #     total_work_area = 1
    #     st.warning("Total Work Area is zero, setting to 1 to avoid division by zero.")
    return (
        (residential_area_with_daylight / total_residential_area)
    )

def metric_calc_energy_ratio(energy_generation, energy_required_by_industrial_team):
    # Avoid division by zero
    if energy_required_by_industrial_team == 0:
        energy_required_by_industrial_team = 1
        st.warning("Energy Required by Industrial Team is zero, setting to 1 to avoid division by zero.")

    return energy_generation / energy_required_by_industrial_team

def metric_calc_panel_optimization(number_optimized_panel_type, number_starting_panel_type):
    # Avoid division by zero
    if number_starting_panel_type == 0:
        number_starting_panel_type = 1
        st.warning("Number of Starting Panel Type is zero, setting to 1 to avoid division by zero.")

    return 1 - number_optimized_panel_type / number_starting_panel_type

def generate_metrics(verified, team_data, model_data) -> list[Metric]:
    (energy_generation, energy_required_by_industrial_team,
     weight_residential, weight_work,
     residential_area_with_daylight, total_residential_area,
    #  work_area_with_daylight, total_work_area,
     number_optimized_panel_type, number_starting_panel_type) = process_data(verified, team_data, model_data)

    metrics = []

    daylight_factor_metric = Metric(
        "Daylight Factor",
        # r'w_{resi}\frac{ResidentialAreaWithDaylight}{TotalResidentialArea} + w_{work}\frac{WorkAreaWithDaylight}{TotalWorkArea}',
        r'\frac{TotalAreaWithTargetDaylight}{TotalArea}',
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
                "name": "Area with Target Daylight",
                "value": residential_area_with_daylight,
                "unit": "m²"
            },
            {
                "name": "Total Area",
                "value": total_residential_area,
                "unit": "m²"
            },
            # {
            #     "name": "Work Area with Daylight",
            #     "value": work_area_with_daylight,
            #     "unit": "m²"
            # },
            # {
            #     "name": "Total Work Area",
            #     "value": total_work_area,
            #     "unit": "m²"
            # }
        ],
        min_value=0,
        max_value=0.1,
        ideal_value=0.8
    )
    metrics.append(daylight_factor_metric)

    panel_optimization_metric = Metric(
        "Panel Optimization Ratio",
        r'1 - \frac {Number of Optimized Panel Type}{Number of Starting Panel Type}',
        "Measures the efficiency of panel area usage.",
        metric_calc_panel_optimization,
        './front_end/dashboards/pictures/panel.png',
        [
            {
                "name": "Number of Optimized Panel Type",
                "value": number_optimized_panel_type,
                "min": 0,
                "max": 2000,
                "unit": "m²"
            },
            {
                "name": "Number of Starting Panel Type",
                "value": number_starting_panel_type,
                "min": 1,
                "max": 2000,
                "unit": "m²"
            }
        ],
        min_value=0,
        max_value=1,
        ideal_value=0.2
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
    return metrics

# Define the function to run the dashboard
def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data, model_data = team_extractor.extract(attribute_display=False)

    metrics = generate_metrics(verified, team_data, model_data)

    generate_dashboard(
        selected_team=selected_team,
        metrics=metrics,
        project_id=project_id,
        team_members=team_members,
        team_extractor=team_extractor,
        extracted_data=team_data,
        model_data=model_data,
        text_dict=text_dict,
        presentation_model_id=presentation_model_id
    )