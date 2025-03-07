import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.service_extractor as team_extractor

from dashboards.dashboard import *

def metric_calc_occupancy_efficiency(utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
    numerator = 0
    for utilization, hours, factor, area in zip(utilization_rate, active_hours, function_exchange_factor, area_of_functions):
        numerator += float(utilization) * float(hours) * float(factor) * float(area)
    occupancy_efficiency = numerator / (float(total_available_hours_per_day) * float(total_area))
    return occupancy_efficiency

# def metric_interactive_calculator_occupancy_efficiency(container, utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
#     with container:
#         col_1, col_2 = st.columns(2)
#         with col_1:
#             n = len(utilization_rate)

#             utilization_rate = float(utilization_rate[0])
#             active_hours = float(active_hours[0])
#             function_exchange_factor = float(function_exchange_factor[0])
#             total_available_hours_per_day = float(total_available_hours_per_day)
#             total_area = float(total_area)
#             area_of_functions = float(area_of_functions[0])

#             utilization_rate_slider = st.slider("Utilization Rate (%)", 0.5, utilization_rate * 1.5, 3.0, help="Percentage of space utilization")
#             active_hours_slider = st.slider("Active Hours", active_hours * 0.5, 24.0, active_hours, help="Hours of active use per day")
#             function_exchange_factor_slider = st.slider("Function Exchange Factor", function_exchange_factor * 0.5, function_exchange_factor * 1.5, function_exchange_factor, help="Multiplier for function flexibility")
#             total_available_hours_per_day_slider = st.slider("Total Available Hours per Day", total_available_hours_per_day * 0.5, 24.0, total_available_hours_per_day, help="Total hours available per day")
#             total_area_slider = st.slider("Total Area", total_area * 0.5, total_area * 1.5, total_area, help="Total area of the building")
#             area_of_functions_slider = st.slider("Area of Functions", area_of_functions * 0.5, area_of_functions * 1.5, area_of_functions, help="Area of the specific function")

#             utilization_rate_slider = [utilization_rate_slider for _ in range(n)]
#             active_hours_slider = [active_hours_slider for _ in range(n)]
#             function_exchange_factor_slider = [function_exchange_factor_slider for _ in range(n)]
#             area_of_functions_slider = [area_of_functions_slider for _ in range(n)]
#             total_available_hours_per_day_slider = total_available_hours_per_day_slider
#             total_area_slider = total_area_slider

#             new_occupancy_efficiency = metric_calc_occupancy_efficiency(
#                 utilization_rate_slider,
#                 active_hours_slider,
#                 function_exchange_factor_slider,
#                 total_available_hours_per_day_slider,
#                 total_area_slider,
#                 area_of_functions_slider
#             )
#             st.markdown(f"### Occupancy Efficiency: {new_occupancy_efficiency:.2f}")
#         with col_2:
#             # Create dynamic sphere for occupancy efficiency
#             dynamic_occupancy_efficiency_sphere = create_sphere_visualization(
#                 "dynamic-occupancy-efficiency-sphere",
#                 new_occupancy_efficiency,
#                 "Occupancy Efficiency",
#                 height=200
#             )
#             st.components.v1.html(dynamic_occupancy_efficiency_sphere, height=250)

def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=True)

    # Call the slideshow function
    slideshow_container = st.container()
    display_image_slideshow(slideshow_container, folder_path='./front_end/dashboards/pictures')  # Update the path to your images

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
        active_hours = team_data["ActiveHoursOfFunctionPerDay"]
        function_exchange_factor = team_data["FunctionExchangeFactor"]
        total_available_hours_per_day = team_data["TotalAvailableHoursPerDay"][0]
        total_area = team_data["TotalArea"][0]
        area_of_functions = team_data["AreaOfFunctions"]

    metrics = []

    occupancy_efficiency_metric = Metric(
        "Occupancy Efficiency",
        r'\frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor \cdot AreaOfFunction_i)}{TotalAvailableHoursPerDay \cdot TotalArea}',
        "Measures the efficiency of space utilization throughout the day.",
        metric_calc_occupancy_efficiency,
        utilization_rate,
        active_hours,
        function_exchange_factor,
        total_available_hours_per_day,
        total_area,
        area_of_functions
    )

    metrics.append(occupancy_efficiency_metric)


    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## Service Design Overview
        Our service design integrates sustainable features with aesthetic considerations.
        """
    )


    st.markdown("---")

    st.write(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=True)

    # Add KPI section
    kpi_container = st.container()
    kpi_data = [
        {
            'title': 'Occupancy Efficiency',
            'image_path': './front_end/dashboards/pictures/daylight.png',
            'name': 'Natural Light Optimization',
            'metric_value': occupancy_efficiency_metric.calculate(),
            'metric_description': 'Daylight coverage ratio',
            'detailed_description': 'The Primary Daylight Factor measures how effectively our facade design maximizes natural light penetration. It considers both residential and work spaces, ensuring optimal daylight distribution while managing solar heat gain.'
        },
    ]



    # Create two columns for the iframe and STL model
    col1, col2 = st.columns(2)

    # Create an iframe for the Speckle model in the first column
    speckle_model_url = "https://macad.speckle.xyz/projects/31f8cca4e0/models/5adade2d5f"  # Replace with your actual Speckle model URL
    iframe_code = f"""
    <iframe src="{speckle_model_url}" 
            style="width: 100%; height: 600px; border: none;">
    </iframe>
    """

    # Display the iframe in the first column
    with col1:
        st.markdown(iframe_code, unsafe_allow_html=True)

    # In the second column, display the STL model
    with col2:
        display_stl_model(
            file_path='./front_end/dashboards/models/model_studio.stl',  # Use a single model path
            color="#808080",  # Change color to grey
            key='facade_stl_model_display'
        )

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Service design optimized for maximum occupancy efficiency",
        "2. Strategic service placement for maximum occupancy efficiency",
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
        title="Occupancy Efficiency",
        primary_metric_value=occupancy_efficiency_metric.calculate(),
        metric_values=[utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions],
        metric_names=["Utilization Rate", "Active Hours", "Function Exchange Factor", "Total Available Hours per Day", "Total Area", "Area of Functions"],
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
        title="Occupancy Efficiency",
        primary_metric_value=occupancy_efficiency_metric.calculate(),
        metric_values=[utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions],
        metric_names=["Utilization Rate", "Active Hours", "Function Exchange Factor", "Total Available Hours per Day", "Total Area", "Area of Functions"],
        units="m²"  # Units for panel area
    )

    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)

    # # Metrics Display - Updated with correct metrics
    # metrics_display_container = st.container()
    # display_st_metric_values(metrics_display_container, metrics)
    
    # metrics_visualization_container = st.container()
    # display_metric_visualizations(metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # # Interactive Calculators
    # metric_interactive_calculator_container = st.container()
    # display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)
    