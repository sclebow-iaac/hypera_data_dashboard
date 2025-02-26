import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.industrial_extractor as industrial_extractor
import pandas as pd
import plotly.express as px

from dashboards.dashboard import *

def metric_calc_energy_ratio(energy_generation, energy_demand):
    return energy_generation / energy_demand

def metric_calc_food_ratio(food_production, food_demand):
    return food_production / food_demand

def metric_calc_recycled_water_ratio(recycled_water, wastewater_production):
    return recycled_water / wastewater_production

def metric_calc_waste_utilization_ratio(recycled_solid_waste, solid_waste_production):
    return 1 - (recycled_solid_waste / solid_waste_production)

def run(selected_team: str) -> None:
    #Dashboard Header
    display_page_title("Industrial")

    # Extract industrial data
    models, client, project_id = setup_speckle_connection()
    verified, industrial_data = industrial_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)
    industrial_extractor.display_data(extracted_data=industrial_data, model_name=industrial_extractor.model_name, verbose=False, header=True, show_table=True, gauge=False, simple_table=True)

    if not verified:
        st.error("Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        industrial_extractor.display_data(extracted_data=industrial_data, model_name=industrial_extractor.model_name, header=False, show_table=False, gauge=True, simple_table=False)
    
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
        energy_generation = industrial_data['EnergyGeneration']
        energy_demand = industrial_data['EnergyDemand']
        food_production = industrial_data['FoodProduction']
        food_demand = industrial_data['FoodDemand']
        recycled_water = industrial_data['RecycledWater']
        wastewater_production = industrial_data['WasteWaterProduction']
        recycled_solid_waste = industrial_data['RecycledSolidWaste']
        solid_waste_production = industrial_data['SolidWasteProduction']

    # Display Formulas and Explanations
    display_formula_section_header("Industrial")

    # Calculate Primary Indices
    energy_ratio = metric_calc_energy_ratio(energy_generation, energy_demand)
    food_ratio = metric_calc_food_ratio(food_production, food_demand)
    recycled_water_ratio = metric_calc_recycled_water_ratio(recycled_water, wastewater_production)
    waste_utilization_ratio = metric_calc_waste_utilization_ratio(recycled_solid_waste, solid_waste_production) # Inverted so higher is better

    # Metrics Display - Updated with correct metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Energy Self-Sufficiency Ratio", f'{energy_ratio:.2f}')
    metric_col2.metric("Food Self-Sufficiency Ratio", f'{food_ratio:.2f}')
    metric_col3.metric("Water Recycling Ratio", f'{recycled_water_ratio:.2f}')
    metric_col4.metric("Waste Utilization Ratio", f'{waste_utilization_ratio}')
    
    energy_ratio_container = st.container()
    display_metric(
        energy_ratio_container,
        "Energy Self-Sufficiency Ratio", 
        r'\frac{Energy Produced}{Energy Needed}', 
        "Measures the building's ability to meet its own energy demands.", 
        energy_ratio
    )

    # Food Metric and Sphere
    food_ratio_container = st.container()
    display_metric(
        food_ratio_container,
        "Food Self-Sufficiency Ratio", 
        r'\frac{Food Produced}{Food Needed}', 
        "Indicates the proportion of food requirements met through internal production.", 
        food_ratio
    )

    # Water Metric and Sphere
    water_ratio_container = st.container()
    display_metric(
        water_ratio_container,
        "Water Recycling Ratio", 
        r'\frac{Recycled Water}{Total Water Used}', 
        "Shows the efficiency of water recycling systems.", 
        recycled_water_ratio
    )

    waste_ratio_container = st.container()
    display_metric(
        waste_ratio_container,
        "Waste Utilization Ratio", 
        r'1 - \frac{Waste Produced}{Maximum Target}', 
        "Measures the efficiency of waste management relative to targets.", 
        waste_utilization_ratio
    )

    # Add a divider before the interactive calculators
    st.markdown("---")

    # Interactive Calculators
    st.markdown("""
    <h3 style='text-align: center;'>Interactive Sustainability Calculators</h3>
    """, unsafe_allow_html=True)

    calc_row1_col1, calc_row1_col2 = st.columns(2)
    calc_row2_col1, calc_row2_col2 = st.columns(2)

    with calc_row1_col1:
        st.markdown("### Energy Self-Sufficiency Calculator")
        energy_produced = st.slider("Energy Produced (kWh)", 0, 2000, int(energy_generation), help="Energy produced by building systems")
        energy_needed = st.slider("Energy Needed (kWh)", 1, 2000, int(energy_demand), help="Total energy required")
        
        new_energy_ratio = energy_produced / energy_needed
        st.markdown(f"### Energy Ratio: {new_energy_ratio:.2f}")

        # Create dynamic sphere for energy
        dynamic_energy_sphere = create_sphere_visualization(
            "dynamic-energy-sphere",
            new_energy_ratio,
            "Energy Self-Sufficiency",
            height=200
        )
        st.components.v1.html(dynamic_energy_sphere, height=250)

    with calc_row1_col2:
        st.markdown("### Food Self-Sufficiency Calculator")
        food_produced_slider = st.slider("Food Produced (kg)", 0, 2000, int(food_production), help="Food produced within building")
        food_needed_slider = st.slider("Food Needed (kg)", 1, 2000, int(food_demand), help="Total food requirements")
        
        new_food_ratio = food_produced_slider / food_needed_slider
        st.markdown(f"### Food Ratio: {new_food_ratio:.2f}")

        # Create dynamic sphere for food
        dynamic_food_sphere = create_sphere_visualization(
            "dynamic-food-sphere",
            new_food_ratio,
            "Food Self-Sufficiency",
            height=200
        )
        st.components.v1.html(dynamic_food_sphere, height=250)

    with calc_row2_col1:
        st.markdown("### Water Recycling Calculator")
        recycled_water = st.slider("Recycled Water (m³)", 0, 2000, int(recycled_water), help="Volume of water recycled")
        total_water = st.slider("Total Water Used (m³)", 1, 2000, int(wastewater_production), help="Total water consumption")
        
        new_water_ratio = recycled_water / total_water
        st.markdown(f"### Water Recycling Rate: {new_water_ratio:.2f}")

        # Create dynamic sphere for water
        dynamic_water_sphere = create_sphere_visualization(
            "dynamic-water-sphere",
            new_water_ratio,
            "Water Recycling Rate",
            height=200
        )
        st.components.v1.html(dynamic_water_sphere, height=250)

    with calc_row2_col2:
        st.markdown("### Waste Production Calculator")
        waste_produced = st.slider("Waste Produced (kg/day)", 0, 400, int(recycled_solid_waste), help="Daily waste production")
        waste_target = st.slider("Maximum Target (kg/day)", 1, 400, int(solid_waste_production), help="Maximum acceptable waste")
        
        new_waste_ratio = 1 - (waste_produced / waste_target)
        st.markdown(f"### Waste Efficiency: {new_waste_ratio:.2f}")

        # Create dynamic sphere for waste
        dynamic_waste_sphere = create_sphere_visualization(
            "dynamic-waste-sphere",
            new_waste_ratio,
            "Waste Production Efficiency",
            height=200
        )
        st.components.v1.html(dynamic_waste_sphere, height=250)
