import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.industrial_extractor as team_extractor

from dashboards.dashboard import *


def metric_calc_energy_ratio(energy_generation, energy_demand):
    return energy_generation / energy_demand


def metric_calc_food_ratio(food_production, food_demand):
    return food_production / food_demand


def metric_calc_recycled_water_ratio(recycled_water, wastewater_production):
    return recycled_water / wastewater_production


def metric_calc_waste_utilization_ratio(recycled_solid_waste, solid_waste_production):
    return 1 - (recycled_solid_waste / solid_waste_production)


# def metric_interactive_calculator_energy_ratio(container, energy_generation, energy_demand):
#     with container:
#         st.markdown("### Energy Self-Sufficiency Calculator")
#         energy_produced = st.slider("Energy Produced (kWh)", 0, 2000, int(
#             energy_generation), help="Energy produced by building systems")
#         energy_needed = st.slider("Energy Needed (kWh)", 1, 2000, int(
#             energy_demand), help="Total energy required")

#         new_energy_ratio = energy_produced / energy_needed
#         st.markdown(f"### Energy Ratio: {new_energy_ratio:.2f}")

#         # Create dynamic sphere for energy
#         dynamic_energy_sphere = create_sphere_visualization(
#             "dynamic-energy-sphere",
#             new_energy_ratio,
#             "Energy Self-Sufficiency",
#             height=200
#         )
#         st.components.v1.html(dynamic_energy_sphere, height=250)


# def metric_interactive_calculator_food_ratio(container, food_production, food_demand):
#     with container:
#         st.markdown("### Food Self-Sufficiency Calculator")
#         food_produced_slider = st.slider("Food Produced (kg)", 0, 2000, int(
#             food_production), help="Food produced within building")
#         food_needed_slider = st.slider("Food Needed (kg)", 1, 2000, int(
#             food_demand), help="Total food requirements")

#         new_food_ratio = food_produced_slider / food_needed_slider
#         st.markdown(f"### Food Ratio: {new_food_ratio:.2f}")

#         # Create dynamic sphere for food
#         dynamic_food_sphere = create_sphere_visualization(
#             "dynamic-food-sphere",
#             new_food_ratio,
#             "Food Self-Sufficiency",
#             height=200
#         )
#         st.components.v1.html(dynamic_food_sphere, height=250)


# def metric_interactive_calculator_recycled_water_ratio(container, recycled_water, wastewater_production):
#     with container:
#         st.markdown("### Water Recycling Calculator")
#         recycled_water = st.slider("Recycled Water (m³)", 0, 2000, int(
#             recycled_water), help="Volume of water recycled")
#         total_water = st.slider("Total Water Used (m³)", 1, 2000, int(
#             wastewater_production), help="Total water consumption")

#         new_water_ratio = recycled_water / total_water
#         st.markdown(f"### Water Recycling Rate: {new_water_ratio:.2f}")

#         # Create dynamic sphere for water
#         dynamic_water_sphere = create_sphere_visualization(
#             "dynamic-water-sphere",
#             new_water_ratio,
#             "Water Recycling Rate",
#             height=200
#         )
#         st.components.v1.html(dynamic_water_sphere, height=250)


# def metric_interactive_calculator_waste_utilization_ratio(container, recycled_solid_waste, solid_waste_production):
#     with container:
#         st.markdown("### Waste Production Calculator")
#         waste_produced = st.slider("Waste Produced (kg/day)", 0, 400,
#                                    int(recycled_solid_waste), help="Daily waste production")
#         waste_target = st.slider("Maximum Target (kg/day)", 1, 400,
#                                  int(solid_waste_production), help="Maximum acceptable waste")

#         new_waste_ratio = 1 - (waste_produced / waste_target)
#         st.markdown(f"### Waste Efficiency: {new_waste_ratio:.2f}")

#         # Create dynamic sphere for waste
#         dynamic_waste_sphere = create_sphere_visualization(
#             "dynamic-waste-sphere",
#             new_waste_ratio,
#             "Waste Production Efficiency",
#             height=200
#         )
#         st.components.v1.html(dynamic_waste_sphere, height=250)


def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(
        models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False,
                                header=False, show_table=False, gauge=False, simple_table=True)
    
    # Call the slideshow function
    slideshow_container = st.container()
    display_image_slideshow(slideshow_container, folder_path='./front_end/dashboards/pictures')  # Update the path to your images

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
        recycled_water = 800   # m³
        wastewater_production = 1000     # m³
        recycled_solid_waste = 120   # kg/day
        solid_waste_production = 200        # kg/day

    else:
        # Extracted data
        energy_generation = float(team_data['EnergyGeneration'])
        energy_demand = float(team_data['EnergyDemand'])
        food_production = float(team_data['FoodProduction'])
        food_demand = float(team_data['FoodDemand'])
        recycled_water = float(team_data['RecycledWater'])
        wastewater_production = float(team_data['WasteWaterProduction'])
        recycled_solid_waste = float(team_data['RecycledSolidWaste'])
        solid_waste_production = float(team_data['SolidWasteProduction'])

    metrics = []

    energy_ratio_metric = Metric(
        "Energy Self-Sufficiency Ratio",
        r'\frac{Energy Produced}{Energy Needed}',
        "Measures the building's ability to meet its own energy demands.",
        metric_calc_energy_ratio,
        energy_generation,
        energy_demand
    )
    metrics.append(energy_ratio_metric)

    food_ratio_metric = Metric(
        "Food Self-Sufficiency Ratio",
        r'\frac{Food Produced}{Food Needed}',
        "Indicates the proportion of food requirements met through internal production.",
        metric_calc_food_ratio,
        food_production,
        food_demand
    )
    metrics.append(food_ratio_metric)

    recycled_water_ratio_metric = Metric(
        "Water Recycling Ratio",
        r'\frac{Recycled Water}{Total Water Used}',
        "Shows the efficiency of water recycling systems.",
        metric_calc_recycled_water_ratio,
        recycled_water,
        wastewater_production
    )
    metrics.append(recycled_water_ratio_metric)

    waste_utilization_ratio_metric = Metric(
        "Waste Utilization Ratio",
        r'1 - \frac{Waste Produced}{Maximum Target}',
        "Measures the efficiency of waste management relative to targets.",
        metric_calc_waste_utilization_ratio,
        recycled_solid_waste,
        solid_waste_production
    )
    metrics.append(waste_utilization_ratio_metric)

    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## Industrial Design Overview
        Our industrial design integrates sustainable features with aesthetic considerations.
        """
    )


    st.markdown("---")

    st.write(" ")

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=True)

    # Add KPI section
    kpi_container = st.container()
    kpi_data = [
        {
            'title': 'Energy Self-Sufficiency Ratio',
            'image_path': './front_end/dashboards/pictures/daylight.png',
            'name': 'Natural Light Optimization',
            'metric_value': energy_ratio_metric.calculate(),
            'metric_description': 'Daylight coverage ratio',
            'detailed_description': 'The Primary Daylight Factor measures how effectively our facade design maximizes natural light penetration. It considers both residential and work spaces, ensuring optimal daylight distribution while managing solar heat gain.'
        },
        {
            'title': 'Food Self-Sufficiency Ratio',
            'image_path': './front_end/dashboards/pictures/panel.png',
            'name': 'Solar Panel Efficiency',
            'metric_value': food_ratio_metric.calculate(),
            'metric_description': 'Panel area optimization ratio',
            'detailed_description': 'Panel Optimization quantifies how efficiently we utilize solar panel area. This metric compares the final panel configuration against the initial layout, showing improvements in energy generation capacity per square meter.'
        },
        {
            'title': 'Water Recycling Ratio',
            'image_path': 'dashboards/pictures/energy.png',
            'name': 'Energy Production',
            'metric_value': recycled_water_ratio_metric.calculate(),
            'metric_description': 'Energy generation ratio',
            'detailed_description': 'The Energy Generation metric represents the ratio between energy produced and energy needed. This helps us understand how well our facade-integrated solar solutions meet the building\'s energy demands.'
        },
        {
            'title': 'Waste Utilization Ratio',
            'image_path': './front_end/dashboards/pictures/energy.png',
            'name': 'Energy Production',
            'metric_value': waste_utilization_ratio_metric.calculate(),
            'metric_description': 'Energy generation ratio',
            'detailed_description': 'The Energy Generation metric represents the ratio between energy produced and energy needed. This helps us understand how well our facade-integrated solar solutions meet the building\'s energy demands.'
        }
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
        title="Energy Self-Sufficiency Ratio",
        primary_metric_value=energy_ratio_metric.calculate(),
        metric_values=[energy_generation, energy_demand],
        metric_names=["Energy Generation", "Energy Demand"],
        units="kWh"  # All units are in meters
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
        title="Food Self-Sufficiency Ratio",
        primary_metric_value=food_ratio_metric.calculate(),
        metric_values=[food_production, food_demand],
        metric_names=["Food Production", "Food Demand"],
        units="kg"  # Units for panel area
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
        title="Water Recycling Ratio",
        primary_metric_value=recycled_water_ratio_metric.calculate(),
        metric_values=[recycled_water, wastewater_production],
        metric_names=["Recycled Water", "Wastewater Production"],
        units="m³"  # Adjust units as necessary
        )
    
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # Call the display function for the Waste Utilization Ratio
    display_metric_circles_and_tape(
        container=st.container(),
        title="Waste Utilization Ratio",
        primary_metric_value=waste_utilization_ratio_metric.calculate(),
        metric_values=[recycled_solid_waste, solid_waste_production],
        metric_names=["Recycled Solid Waste", "Solid Waste Production"],
        units="kg/day"  # Adjust units as necessary
    )



    # # Display Formulas and Explanations
    # display_formula_section_header(selected_team)

    # # Metrics Display - Updated with correct metrics
    # metrics_display_container = st.container()
    # display_st_metric_values(metrics_display_container, metrics)

    # metrics_visualization_container = st.container()
    # display_metric_visualizations(
    #     metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # # Interactive Calculators
    # metric_interactive_calculator_container = st.container()
    # display_interactive_calculators(
    #     metric_interactive_calculator_container, metrics, grid=True)
