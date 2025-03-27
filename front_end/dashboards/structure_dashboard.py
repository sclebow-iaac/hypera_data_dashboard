import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.structure_extractor as team_extractor
from dashboards.dashboard import *

# Define data for the dashboard
team_members = [
    {
        'name': 'Marco Durand',
        'link': 'https://blog.iaac.net/user/marcodurand/',
    },
    {
        'name': 'Joaquin Broquedis',
        'link': 'https://blog.iaac.net/user/joaquin+broquedis/',
    },
]

text_dict = {
    'design_overview': 'Our structure design emphasizes safety, efficiency, and sustainability. We focus on optimizing space while ensuring structural integrity.',
    'bullet_items': [
        "1. Topologically optimized cores receive the neighborhoods' weight and connect the node levels",
        "2. An exoskeleton wraps and supports the neighborhoods' slabs driving loads to the node levels"
    ],
}

presentation_model_id = 'c2df017258'

def process_data(verified, team_data, model_data):
    if not verified:
        st.error(
            "Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, model_data=model_data, header=False, show_table=False, gauge=True, simple_table=False)

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

    return (total_column_free_floor_area, total_floor_area,
            load_capacity, self_weight_of_structure)

def metric_calc_column_free_floor_area_ratio(total_column_free_floor_area, total_floor_area):
    return float(total_column_free_floor_area) / float(total_floor_area)


def metric_calc_load_capacity_per_square_meter(load_capacity, self_weight_of_structure):
    return float(load_capacity) / float(self_weight_of_structure)

def generate_metrics(verified, team_data, model_data) -> list[Metric]:
    # Extract data
    total_column_free_floor_area, total_floor_area, load_capacity, self_weight_of_structure = process_data(verified, team_data, model_data)

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
        ideal_value = 1.55
    )
    metrics.append(load_capacity_metric)

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