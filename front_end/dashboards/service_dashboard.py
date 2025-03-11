import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

import data_extraction.service_extractor as team_extractor
from dashboards.dashboard import *

def metric_calc_occupancy_efficiency(utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
    numerator = 0
    for utilization, hours, factor, area in zip(utilization_rate, active_hours, function_exchange_factor, area_of_functions):
        numerator += float(utilization) * float(hours) * float(factor) * float(area)
    occupancy_efficiency = numerator / (float(total_available_hours_per_day) * float(total_area))
    return occupancy_efficiency

def metric_interactive_calculator_occupancy_efficiency(container, utilization_rate, active_hours, function_exchange_factor, total_available_hours_per_day, total_area, area_of_functions):
    with container:
            
        n = len(utilization_rate)

        utilization_rate = float(utilization_rate[0])
        active_hours = float(active_hours[0])
        function_exchange_factor = float(function_exchange_factor[0])
        total_available_hours_per_day = float(total_available_hours_per_day)
        total_area = float(total_area)
        area_of_functions = float(area_of_functions[0])

        def create_slider(label, value, help_text):
            return st.slider(label, value * 0.5, value * 1.5, value, help=help_text)

        utilization_rate_slider = create_slider("Utilization Rate (%)", utilization_rate, "Percentage of space utilization")
        active_hours_slider = create_slider("Active Hours", active_hours, "Hours of active use per day")
        function_exchange_factor_slider = create_slider("Function Exchange Factor", function_exchange_factor, "Multiplier for function flexibility")
        total_area_slider = create_slider("Total Area", total_area, "Total area of the building")
        area_of_functions_slider = create_slider("Area of Functions", area_of_functions, "Area of the specific function")

        utilization_rate_slider = [utilization_rate_slider for _ in range(n)]
        active_hours_slider = [active_hours_slider for _ in range(n)]
        function_exchange_factor_slider = [function_exchange_factor_slider for _ in range(n)]
        area_of_functions_slider = [area_of_functions_slider for _ in range(n)]
        total_area_slider = total_area_slider

        new_occupancy_efficiency = metric_calc_occupancy_efficiency(
            utilization_rate_slider,
            active_hours_slider,
            function_exchange_factor_slider,
            total_available_hours_per_day,
            total_area_slider,
            area_of_functions_slider
        )
        st.markdown(f"### Occupancy Efficiency: {new_occupancy_efficiency:.2f}")

def run(selected_team: str) -> None:
    
     # Create two equal columns
    col1, col2 = st.columns(2)  # Both columns will have equal width

    # In the first column, display the image slideshow
    with col1:

        # Create a container for the slideshow
        container = st.container()
        
        # Call the display_image_slideshow function
        # Example usage
        folder_path = "./front_end/dashboards/pictures"  # Update this to your actual image folder path
        display_image_slideshow(container, folder_path, "facade_slideshow")  # Change interval as needed


    # In the second column, display the iframe for the Speckle model
    with col2:
        container = st.container()
        display_speckle_viewer(container, '31f8cca4e0', '76b50ad007', is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False)
        container.markdown("https://macad.speckle.xyz/projects/31f8cca4e0/models/76b50ad007" , unsafe_allow_html=True)

    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=False)

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
        metric_interactive_calculator_occupancy_efficiency,
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
                "unit": "hours"
            },
            {
                "name": "Function Exchange Factor",
                "value": function_exchange_factor,
                "display_value": sum(float(x) for x in function_exchange_factor),
                "unit": "hours"
            },
            {
                "name": "Total Available Hours per Day",
                "value": total_available_hours_per_day,
                "unit": "hours"
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

    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)


    text_container = st.container()
    display_text_section(
        text_container,
        """
        ##
        Our service design integrates sustainable features with aesthetic considerations.
        """
    )


    st.markdown("---")

    st.write(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=False)
    
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


    # # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)
    
    metrics_visualization_container = st.container()
    display_metric_visualizations(metrics_visualization_container, metrics, add_text=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)
    