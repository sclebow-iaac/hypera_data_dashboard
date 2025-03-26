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
    'design_overview': 'Hyper A is a visionary vertical ecosystem that redefines the idea of a 24/7 “city within a city” through a seamless fusion of computation and human-scale design. Spanning a 1 km² hyper-building divided into eight distinct neighborhoods, the concept uses 3D space syntax and Kangaroo solver to optimize connectivity, adjacency, and functionality at both macro and micro scales. At its core, Hyper A prioritizes community life—interweaving neighborhoods into a dynamic social network where space is fluid, adaptable, and engaging. A voxelized workflow supports precision collaboration across teams, while innovative circulation systems ensure experiential richness. Here, movement becomes an experience, and architecture becomes infrastructure for interaction.',
    'bullet_items': [
        "Data:",
        " 1. Collaboration with other teams",
        " 2. Research for population & benchmark",
        " 3. Eight neighborhoods concept",
        " 4. Detailed program - day/evening/night",
        " 5. Utilization rate for KPI",
        "Allocation:",
        " 1. Massing study in collaboration with structure team",
        " 2. Macro and micro adjacency",
        " 3. Kangaroo solver",
        " 4. Data gathering and extraction for function distribution",
        "Voxelization:",
        " 1. Automated process",
        " 2. Color coded functions",
        " 3. Corridor placement",
        " 4. Area calculation for KPI"
    ],
}

presentation_model_id = '76b50ad007'

def process_data(verified, team_data, model_data):
    if not verified:
        st.error("Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, model_data=model_data, header=False, show_table=False, gauge=True, simple_table=False)

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

    return (function_names, utilization_rate, active_hours, function_exchange_factor,
            total_available_hours_per_day, total_area, area_of_functions)

def metric_calc_occupancy_efficiency(utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
    numerator = 0
    for utilization, hours, factor, area in zip(utilization_rate, active_hours, function_exchange_factor, area_of_functions):
        numerator += float(utilization) * float(hours) * float(factor) * float(area)
    occupancy_efficiency = numerator / (float(total_available_hours_per_day) * float(total_area))
    return occupancy_efficiency

def generate_metrics(verified, team_data, model_data) -> list[Metric]:
    function_names, utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions = process_data(verified, team_data, model_data)

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