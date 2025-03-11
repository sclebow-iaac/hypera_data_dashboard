import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from viewer import display_speckle_viewer

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


def metric_interactive_calculator_energy_ratio(container, energy_generation, energy_demand):
    with container:
        st.markdown("### Energy Self-Sufficiency Calculator")
        energy_produced = st.slider("Energy Produced (kWh)", 0, 2000, int(
            energy_generation), help="Energy produced by building systems")
        energy_needed = st.slider("Energy Needed (kWh)", 1, 2000, int(
            energy_demand), help="Total energy required")

        new_energy_ratio = energy_produced / energy_needed
        st.markdown(f"### Energy Ratio: {new_energy_ratio:.2f}")


def metric_interactive_calculator_food_ratio(container, food_production, food_demand):
    with container:
        st.markdown("### Food Self-Sufficiency Calculator")
        food_produced_slider = st.slider("Food Produced (kg)", 0, 2000, int(
            food_production), help="Food produced within building")
        food_needed_slider = st.slider("Food Needed (kg)", 1, 2000, int(
            food_demand), help="Total food requirements")

        new_food_ratio = food_produced_slider / food_needed_slider
        st.markdown(f"### Food Ratio: {new_food_ratio:.2f}")



def metric_interactive_calculator_recycled_water_ratio(container, recycled_water, wastewater_production):
    with container:
        st.markdown("### Water Recycling Calculator")
        recycled_water = st.slider("Recycled Water (m³)", 0, 2000, int(
            recycled_water), help="Volume of water recycled")
        wastewater_production = st.slider("Wastewater Production (m³)", 1, 2000, int(
            wastewater_production), help="Wastewater produced")

        new_water_ratio = recycled_water / wastewater_production
        st.markdown(f"### Water Recycling Rate: {new_water_ratio:.2f}")


def metric_interactive_calculator_waste_utilization_ratio(container, recycled_solid_waste, solid_waste_production):
    with container:
        st.markdown("### Waste Production Calculator")
        waste_produced = st.slider("Waste Produced (kg/day)", 0, 400,
                                   int(recycled_solid_waste), help="Daily waste production")
        waste_target = st.slider("Maximum Target (kg/day)", 1, 400,
                                 int(solid_waste_production), help="Maximum acceptable waste")

        new_waste_ratio = 1 - (waste_produced / waste_target)
        st.markdown(f"### Waste Efficiency: {new_waste_ratio:.2f}")

def run(selected_team: str) -> None:
    # st.title(f"{selected_team} Dashboard")
    
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
        display_speckle_viewer(container, '31f8cca4e0', '89db050bc3', is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False)
        container.markdown("https://macad.speckle.xyz/projects/31f8cca4e0/models/89db050bc3" , unsafe_allow_html=True)

    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(
        models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False,
                                header=False, show_table=False, gauge=False, simple_table=True)
    

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
        metric_interactive_calculator_energy_ratio,
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
        metric_interactive_calculator_food_ratio,
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
        ideal_value = 0.5
    )
    metrics.append(food_ratio_metric)

    recycled_water_ratio_metric = Metric(
        "Water Recycling Ratio",
        r'\frac{Recycled Water}{Wastewater Production}',
        "Shows the efficiency of water recycling systems.",
        metric_interactive_calculator_recycled_water_ratio,
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
        ideal_value = 0.5
    )
    metrics.append(recycled_water_ratio_metric)
    waste_utilization_ratio_metric = Metric(
        "Waste Utilization Ratio",
        r'1 - \frac{Waste Produced}{Maximum Target}',
        "Measures the efficiency of waste management relative to targets.",
        metric_interactive_calculator_waste_utilization_ratio,
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
        ideal_value = 0.5
    )
    metrics.append(waste_utilization_ratio_metric)

    text_container = st.container()
    display_text_section(
        text_container,
        """
        ## 
        Our industrial design integrates sustainable features with aesthetic considerations.
        """
    )


    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=False, gauge=False, simple_table=True)


    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Solar panels optimized for maximum energy generation",
        "2. Strategic window placement for natural daylight",
        "3. Thermal insulation systems for energy efficiency"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    team_extractor.display_data(extracted_data=team_data, verbose=False, header=False, show_table=True, gauge=False, simple_table=True)

    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")


    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    metrics_visualization_container = st.container()
    display_metric_visualizations(metrics_visualization_container, metrics, add_text=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(metric_interactive_calculator_container, metrics, grid=True)

