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

def process_data(verified, team_data):
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

    return number_of_units, unit_types, total_number_of_units

def metric_calc_index(number_of_units, unit_types, total_number_of_units):
    numerator = sum(float(units) * (float(units) - 1) for units in number_of_units)
    denominator = float(total_number_of_units) * (float(total_number_of_units) - 1)
    return 1 - (numerator / denominator) if denominator != 0 else None

def generate_metrics(verified, team_data) -> list[Metric]:
    number_of_units, unit_types, total_number_of_units = process_data(verified, team_data)
    
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

    return metrics

# Define the function to run the dashboard
def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data, model_data = team_extractor.extract(attribute_display=False)

    metrics = generate_metrics(verified, team_data)

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