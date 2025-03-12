import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.service_extractor as team_extractor
from dashboards.dashboard import *

# Define data for the dashboard
team_members = [
    {
        'name': 'Seda Soylu',
        'link': 'https://blog.iaac.net/user/sedasoylu/',
    },
    {
        'name': 'Francesco Visconti Prasca',
        'link': 'https://blog.iaac.net/user/f.visconti.prasca/',
    },
    {
        'name': 'Matea Pinjusic',
        'link': 'https://blog.iaac.net/user/mateapinjusic/',
    },
]

text_dict = {
    'design_overview': "Our service design integrates sustainable features with aesthetic considerations.",
    'bullet_items': [
        "1. Service design optimized for maximum occupancy efficiency",
        "2. Strategic service placement for maximum occupancy efficiency",
    ],
}

presentation_model_id = '76b50ad007'

def metric_calc_occupancy_efficiency(utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
    numerator = 0
    for utilization, hours, factor, area in zip(utilization_rate, active_hours, function_exchange_factor, area_of_functions):
        numerator += float(utilization) * float(hours) * float(factor) * float(area)
    occupancy_efficiency = numerator / (float(total_available_hours_per_day) * float(total_area))
    return occupancy_efficiency

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)
   
    if not verified:
        st.error("Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        function_names = ["Function1", "Function2", "Function3"]
        utilization_rate = [0.8, 0.6, 0.7]
        active_hours = [12, 24, 24]
        function_exchange_factor = [1, 1.5, 2]
        total_available_hours_per_day = 24
        total_area = 1000
        area_of_functions = [100, 200, 300]

    else:
        function_names = team_data["ListOfFunctionNames"]
        utilization_rate = team_data["UtilizationRateOfFunction"]
        utilization_rate = [float(x) for x in utilization_rate]
        active_hours = team_data["ActiveHoursOfFunctionPerDay"]
        active_hours = [float(x) for x in active_hours]
        function_exchange_factor = team_data["FunctionExchangeFactor"]
        function_exchange_factor = [float(x) for x in function_exchange_factor]
        total_available_hours_per_day = float(team_data["TotalAvailableHoursPerDay"][0])
        total_area = float(team_data["TotalArea"][0])
        area_of_functions = team_data["AreaOfFunctions"]
        area_of_functions = [float(x) for x in area_of_functions]

    metrics = []

    occupancy_efficiency_metric = Metric(
        "Occupancy Efficiency",
        r'\frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor \cdot AreaOfFunction_i)}{TotalAvailableHoursPerDay \cdot TotalArea}',
        "Measures the efficiency of space utilization throughout the day.",
        metric_calc_occupancy_efficiency,
        './front_end/dashboards/pictures/service.png',
        [
            {
                "name": "Utilization Rate",
                "value": utilization_rate,
                "display_value": sum(float(x) for x in utilization_rate),
                "unit": "%"
            },
            {
                "name": "Active Hours",
                "value": active_hours,
                "display_value": sum(float(x) for x in active_hours),
                "unit": "hrs"
            },
            {
                "name": "Function Exchange Factor",
                "value": function_exchange_factor,
                "display_value": sum(float(x) for x in function_exchange_factor) / len(function_exchange_factor),
                "unit": "Average"
            },
            {
                "name": "Total Available Hours per Day",
                "value": total_available_hours_per_day,
                "unit": "hrs"
            },
            {
                "name": "Total Area",
                "value": total_area,
                "unit": "m²"
            },
            {
                "name": "Area of Functions",
                "value": area_of_functions,
                "display_value": sum(float(x) for x in area_of_functions),
                "unit": "m²"
            }
        ],
        min_value = 0,
        max_value = 1,
        ideal_value = 0.5
    )

    metrics.append(occupancy_efficiency_metric)
    
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
