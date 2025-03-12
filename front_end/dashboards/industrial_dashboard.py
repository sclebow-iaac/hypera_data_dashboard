import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.industrial_extractor as team_extractor

from dashboards.dashboard import *

# Define data for the dashboard
team_members = [
    {
        'name': 'Andres Espinosa',
        'link': 'https://blog.iaac.net/user/a_espinosa/',
    },
    {
        'name': 'Cesar Diego Herbosa',
        'link': 'https://blog.iaac.net/user/cesar/',
    },
    {
        'name': 'Aymeric Brouez',
        'link': 'https://blog.iaac.net/user/aymeric+brouez/',
    },
]

text_dict = {
    'design_overview': 'Our industrial design integrates sustainable features with aesthetic considerations.',
    'bullet_items': [
        "1. Energy generation optimized for maximum efficiency",
        "2. Food production systems to meet dietary needs",
        "3. Water recycling systems for sustainability"
    ],
}

presentation_model_id = '89db050bc3'

def metric_calc_energy_ratio(energy_generation, energy_demand):
    return energy_generation / energy_demand

def metric_calc_food_ratio(food_production, food_demand):
    return food_production / food_demand

def metric_calc_recycled_water_ratio(recycled_water, wastewater_production):
    return recycled_water / wastewater_production

def metric_calc_waste_utilization_ratio(recycled_solid_waste, solid_waste_production):
    return 1 - (recycled_solid_waste / solid_waste_production)

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    if not verified:
        st.error(
            "Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        # Example data
        energy_generation = 750  # kWh
        energy_demand = 1000   # kWh
        food_production = 600    # kg
        food_demand = 1000     # kg
        recycled_solid_waste = 120   # kg/day
        solid_waste_production = 200        # kg/day
        recycled_water = 100   # m³
        wastewater_production = 200        # m³

    else:
        # Extracted data
        energy_generation = float(team_data['EnergyGeneration'])
        energy_demand = float(team_data['EnergyDemand'])
        food_production = float(team_data['FoodProduction'])
        food_demand = float(team_data['FoodDemand'])
        recycled_solid_waste = float(team_data['RecycledSolidWaste'])
        solid_waste_production = float(team_data['SolidWasteProduction'])
        recycled_water = float(team_data['RecycledWater'])
        wastewater_production = float(team_data['WasteWaterProduction'])

    metrics = []

    energy_ratio_metric = Metric(
        "Energy Self-Sufficiency Ratio",
        r'\frac{Energy Produced}{Energy Needed}',
        "Measures the building's ability to meet its own energy demands.",
        metric_calc_energy_ratio,
        './front_end/dashboards/pictures/energy_industrial.png',
        [
            {
                "name": "Energy Generation",
                "value": energy_generation,
                "unit": "kWh"
            },
            {
                "name": "Energy Demand",
                "value": energy_demand,
                "unit": "kWh"
            }
        ],
        min_value = 0,
        max_value = 150,
        ideal_value = 100
    )
    print("APPENDING METRIC", energy_ratio_metric.inputs)
    metrics.append(energy_ratio_metric)

    food_ratio_metric = Metric(
        "Food Self-Sufficiency Ratio",
        r'\frac{Food Produced}{Food Needed}',
        "Indicates the proportion of food requirements met through internal production.",
        metric_calc_food_ratio,
        './front_end/dashboards/pictures/food.png',
        [
            {
                "name": "Food Production",
                "value": food_production,
                "unit": "kg"
            },
            {
                "name": "Food Demand",
                "value": food_demand,
                "unit": "kg"
            }
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 1
    )
    metrics.append(food_ratio_metric)

    recycled_water_ratio_metric = Metric(
        "Water Recycling Ratio",
        r'\frac{Recycled Water}{Wastewater Production}',
        "Shows the efficiency of water recycling systems.",
        metric_calc_recycled_water_ratio,
        './front_end/dashboards/pictures/water.png',
        [
            {
                "name": "Recycled Water",
                "value": recycled_water,
                "unit": "m³"
            },
            {
                "name": "Wastewater Production",
                "value": wastewater_production,
                "unit": "m³"
            }
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 1
    )
    metrics.append(recycled_water_ratio_metric)
    waste_utilization_ratio_metric = Metric(
        "Waste Utilization Ratio",
        r'1 - \frac{Waste Produced}{Maximum Target}',
        "Measures the efficiency of waste management relative to targets.",
        metric_calc_waste_utilization_ratio,
        './front_end/dashboards/pictures/waste.png',
        [
            {
                "name": "Recycled Solid Waste",
                "value": recycled_solid_waste,
                "unit": "kg/day"
            },
            {
                "name": "Solid Waste Production",
                "value": solid_waste_production,
                "unit": "kg/day"
            }
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 1
    )
    metrics.append(waste_utilization_ratio_metric)

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