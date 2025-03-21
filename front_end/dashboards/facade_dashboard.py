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
    'design_overview': 'Our facade design integrates sustainable features with aesthetic considerations.',
    'bullet_items': [
        "1. Solar panels optimized for maximum energy generation",
        "2. Strategic window placement for natural daylight",
        "3. Thermal insulation systems for energy efficiency"
    ]
}

presentation_model_id = '29bc37af8e'

def process_data(verified, team_data):
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

    return (energy_generation, energy_required_by_industrial_team,
            weight_residential, weight_work,
            residential_area_with_daylight, total_residential_area,
            work_area_with_daylight, total_work_area,
            total_final_panel_area, total_initial_panel_area)

def metric_calc_daylight_factor(weight_residential, weight_work, residential_area_with_daylight, total_residential_area, work_area_with_daylight, total_work_area):
    return (
        weight_residential * (residential_area_with_daylight / total_residential_area) +
        weight_work * (work_area_with_daylight / total_work_area)
    )

def metric_calc_energy_ratio(energy_generation, energy_required_by_industrial_team):
    return energy_generation / energy_required_by_industrial_team

def metric_calc_panel_optimization(total_final_panel_area, total_initial_panel_area):
    return total_final_panel_area / total_initial_panel_area

def generate_metrics(verified, team_data) -> list[Metric]:
    (energy_generation, energy_required_by_industrial_team,
     weight_residential, weight_work,
     residential_area_with_daylight, total_residential_area,
     work_area_with_daylight, total_work_area,
     total_final_panel_area, total_initial_panel_area) = process_data(verified, team_data)

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
        max_value=3,
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
    return metrics

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(header=False, table=False, gauge=False, attribute_display=False)
    
    metrics = generate_metrics(verified, team_data)

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