import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.structure_extractor as team_extractor
from dashboards.dashboard import *

def metric_calc_column_free_floor_area_ratio(total_column_free_floor_area, total_floor_area):
    return float(total_column_free_floor_area) / float(total_floor_area)


def metric_calc_load_capacity_per_square_meter(load_capacity, self_weight_of_structure):
    return float(load_capacity) / float(self_weight_of_structure)


# def metric_calc_material_efficiency_ratio(theoretical_minimum_material_usage, actual_material_usage):
#     return theoretical_minimum_material_usage / actual_material_usage


# def metric_calc_embodied_carbon_emissions_per_square_meter(total_embodied_carbon_emissions, usable_floor_area):
#     return total_embodied_carbon_emissions / usable_floor_area


def metric_interactive_calculator_column_free_floor_area_ratio(container, total_column_free_floor_area, total_floor_area):
    with container:
        st.markdown("### Column-Free FAR Calculator")
        new_column_free_area = st.slider("Total Column-Free Floor Area (m²)", 0, 2000, int(
            total_column_free_floor_area), help="Total column-free floor area")
        new_total_area = st.slider("Total Floor Area (m²)", 1, 2000, int(
            total_floor_area), help="Total floor area")
        new_ratio = new_column_free_area / new_total_area
        st.markdown(f"### Resulting Ratio: {new_ratio:.2f}")
        # Create dynamic sphere for column-free FAR
        dynamic_column_free_far_sphere = create_sphere_visualization(
            "dynamic-column-free-far-sphere",
            new_ratio,
            "Column-Free FAR",
            height=200
        )
        st.components.v1.html(dynamic_column_free_far_sphere, height=250)
def run(selected_team: str) -> None:
    # st.title(f"{selected_team} Structure Dashboard")

    # Create two equal columns
    col1, col2 = st.columns(2)  # Both columns will have equal width

    # In the first column, display the image slideshow
    with col1:
        display_image_slideshow(col1, "./dashboards/pictures", "slideshow_1")  # Pass a unique key

    # In the second column, display the iframe for the Speckle model
    with col2:
        iframe_code = f"""
        <iframe src="https://macad.speckle.xyz/projects/31f8cca4e0/models/5adade2d5f" 
                style="width: 100%; height: 600px; border: none;">
        </iframe>
        """
        st.markdown(iframe_code, unsafe_allow_html=True)

    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    if not verified:
        st.error(
            "Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        # Example data
        total_column_free_floor_area = 800
        total_floor_area = 1000
        load_capacity = 800
        self_weight_of_structure = 500
        # theoretical_minimum_material_usage = 800
        # actual_material_usage = 500
        # total_embodied_carbon_emissions = 800
        # usable_floor_area = 1000
    else:
        # Extracted data
        total_column_free_floor_area = float(
        team_data['TotalColumnFreeFloorArea'])
        total_floor_area = float(team_data['TotalFloorArea'])
        # total_embodied_carbon_emissions = team_data['TotalEmbodiedCarbonEmissions']
        # usable_floor_area = team_data['UsableFloorArea']
        load_capacity = float(team_data['LoadCapacity'])
        self_weight_of_structure = float(team_data['SelfWeightOfStructure'])
        # theoretical_minimum_material_usage = team_data['TheoreticalMinimumMaterialUsage']
        # actual_material_usage = team_data['ActualMaterialUsage']

    metrics = []


    column_free_floor_area_metric = Metric(
        "Column-Free Floor Area Ratio",
        r'\frac{Total Column-Free Floor Area (m²)}{Total Floor Area (m²)}',
        "Ratio of column-free floor area to total floor area",
        metric_calc_column_free_floor_area_ratio,
        './dashboards/pictures/column.png',
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
        ]
    )
    metrics.append(column_free_floor_area_metric)

    load_capacity_metric = Metric(
        "Load Capacity per Square Meter",
        r'\frac{Load Capacity (kg)}{Self Weight of Structure (kg)}',
        "Ratio of load capacity to self weight of structure",
        metric_calc_load_capacity_per_square_meter,
        './dashboards/pictures/load.png',
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
        ]
    )
    metrics.append(load_capacity_metric)

    # Building Dashboard
    text_container = st.container()
    display_text_section(
        text_container,
        """
        ##
        Our structure design emphasizes safety, efficiency, and sustainability. We focus on optimizing space while ensuring structural integrity.
        """
    )

    st.markdown("---")

    st.markdown(" ")
    st.markdown(" ")

    # Now, display the custom bullet list underneath the iframe and STL model
    bullet_items = [
        "1. Structural integrity optimized for safety",
        "2. Efficient use of materials",
        "3. Compliance with building codes"
    ]
    display_custom_bullet_list(st.container(), bullet_items)  # Call the function to display the bullet list

    st.markdown(" ")
    st.markdown(" ")

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


# def metric_interactive_calculator_column_free_floor_area_ratio(container, total_column_free_floor_area, total_floor_area):
#     with container:
#         st.markdown("### Column-Free FAR Calculator")
#         new_column_free_area = st.slider("Total Column-Free Floor Area (m²)", 0, 2000, int(
#             total_column_free_floor_area), help="Total column-free floor area")
#         new_total_area = st.slider("Total Floor Area (m²)", 1, 2000, int(
#             total_floor_area), help="Total floor area")
#         new_ratio = new_column_free_area / new_total_area
#         st.markdown(f"### Resulting Ratio: {new_ratio:.2f}")
#         # Create dynamic sphere for column-free FAR
#         dynamic_column_free_far_sphere = create_sphere_visualization(
#             "dynamic-column-free-far-sphere",
#             new_ratio,
#             "Column-Free FAR",
#             height=200
#         )
#         st.components.v1.html(dynamic_column_free_far_sphere, height=250)


def metric_interactive_calculator_load_capacity(container, load_capacity, self_weight_of_structure):
    with container:
        st.markdown("### Load Capacity Calculator")
        new_load_capacity = st.slider("Load Capacity (kg)", 0, 2000, int(
            load_capacity), help="Load capacity of the structure")
        new_self_weight = st.slider("Self Weight of Structure (kg)", 1, 1000, int(
            self_weight_of_structure), help="Self weight of the structure")
        new_load_ratio = new_load_capacity / new_self_weight
        st.markdown(f"### Resulting Ratio: {new_load_ratio:.2f}")
        # Create dynamic sphere for load capacity
        dynamic_load_capacity_sphere = create_sphere_visualization(
            "dynamic-load-capacity-sphere",
            new_load_ratio,
            "Load Capacity",
            height=200
        )
        st.components.v1.html(dynamic_load_capacity_sphere, height=250)


# def metric_interactive_calculator_material_efficiency(container, theoretical_minimum_material_usage, actual_material_usage):
#     with container:
#         st.markdown("### Material Efficiency Calculator")
#         new_theoretical = st.slider("Theoretical Minimum Material Usage (kg)", 0, 2000, int(
#             theoretical_minimum_material_usage), help="Theoretical minimum material usage")
#         new_actual = st.slider("Actual Material Usage (kg)", 1, 1000, int(
#             actual_material_usage), help="Actual material usage")
#         new_material_ratio = new_theoretical / new_actual
#         st.markdown(f"### Resulting Ratio: {new_material_ratio:.2f}")
#         # Create dynamic sphere for material efficiency
#         dynamic_material_efficiency_sphere = create_sphere_visualization(
#             "dynamic-material-efficiency-sphere",
#             new_material_ratio,
#             "Material Efficiency",
#             height=200
#         )
#         st.components.v1.html(dynamic_material_efficiency_sphere, height=250)


# def metric_interactive_calculator_embodied_carbon(container, total_embodied_carbon_emissions, usable_floor_area):
#     with container:
#         st.markdown("### Embodied Carbon Calculator")
#         new_carbon = st.slider("Total Embodied Carbon Emissions (kg)", 0, 2000, int(
#             total_embodied_carbon_emissions), help="Total embodied carbon emissions")
#         new_floor_area = st.slider("Usable Floor Area (m²)", 1, 2000, int(
#             usable_floor_area), help="Usable floor area")
#         new_carbon_ratio = new_carbon / new_floor_area
#         st.markdown(f"### Resulting Ratio: {new_carbon_ratio:.2f}")
#         # Create dynamic sphere for embodied carbon
#         dynamic_embodied_carbon_sphere = create_sphere_visualization(
#             "dynamic-embodied-carbon-sphere",
#             new_carbon_ratio,
#             "Embodied Carbon",
#             height=200
#         )
#         st.components.v1.html(dynamic_embodied_carbon_sphere, height=250)


def run(selected_team: str) -> None:
    # Extract data
    models, client, project_id = setup_speckle_connection()
    verified, team_data = team_extractor.extract(
        models, client, project_id, header=False, table=False, gauge=False, attribute_display=False)

    # Building Dashboard
    # Dashboard Header
    display_page_title(selected_team)
    team_extractor.display_data(extracted_data=team_data, verbose=False,
                                header=True, show_table=True, gauge=False, simple_table=True)

    if not verified:
        st.error(
            "Failed to extract data, proceding with Example Data.  Use Data Dashboard to Investigate.")
        team_extractor.display_data(
            extracted_data=team_data, header=False, show_table=False, gauge=True, simple_table=False)

        # Example data
        total_column_free_floor_area = 800
        total_floor_area = 1000
        load_capacity = 800
        self_weight_of_structure = 500
        # theoretical_minimum_material_usage = 800
        # actual_material_usage = 500
        # total_embodied_carbon_emissions = 800
        # usable_floor_area = 1000
    else:
        # Extracted data
        total_column_free_floor_area = float(
            team_data['TotalColumnFreeFloorArea'])
        total_floor_area = float(team_data['TotalFloorArea'])
        # total_embodied_carbon_emissions = team_data['TotalEmbodiedCarbonEmissions']
        # usable_floor_area = team_data['UsableFloorArea']
        load_capacity = float(team_data['LoadCapacity'])
        self_weight_of_structure = float(team_data['SelfWeightOfStructure'])
        # theoretical_minimum_material_usage = team_data['TheoreticalMinimumMaterialUsage']
        # actual_material_usage = team_data['ActualMaterialUsage']

    metrics = []

    column_free_floor_area_metric = Metric(
        "Column-Free Floor Area Ratio",
        r'\frac{Total Column-Free Floor Area (m²)}{Total Floor Area (m²)}',
        "Ratio of column-free floor area to total floor area",
        metric_interactive_calculator_column_free_floor_area_ratio,
        metric_calc_column_free_floor_area_ratio,
        total_column_free_floor_area,
        total_floor_area
    )
    metrics.append(column_free_floor_area_metric)

    load_capacity_metric = Metric(
        "Load Capacity per Square Meter",
        r'\frac{Load Capacity (kg)}{Self Weight of Structure (kg)}',
        "Ratio of load capacity to self weight of structure",
        metric_interactive_calculator_load_capacity,
        metric_calc_load_capacity_per_square_meter,
        load_capacity,
        self_weight_of_structure
    )
    metrics.append(load_capacity_metric)
    # material_efficiency_metric = Metric(
    #     "Material Efficiency Ratio",
    #     r'\frac{Theoretical Minimum Material Usage (kg)}{Actual Material Usage (kg)}',
    #     "Ratio of theoretical minimum material usage to actual material usage",
    #     metric_interactive_calculator_material_efficiency,
    #     metric_calc_material_efficiency_ratio,
    #     theoretical_minimum_material_usage,
    #     actual_material_usage
    # )
    # metrics.append(material_efficiency_metric)
    # embodied_carbon_metric = Metric(
    #     "Embodied Carbon Emissions per Square Meter",
    #     r'\frac{Total Embodied Carbon Emissions (kg)}{Usable Floor Area (m²)}',
    #     "Ratio of total embodied carbon emissions to usable floor area",
    #     metric_interactive_calculator_embodied_carbon,
    #     metric_calc_embodied_carbon_emissions_per_square_meter,
    #     total_embodied_carbon_emissions,
    #     usable_floor_area
    # )
    # metrics.append(embodied_carbon_metric)

    # Display Formulas and Explanations
    display_formula_section_header(selected_team)

    # Metrics Display - Updated with correct metrics
    metrics_display_container = st.container()
    display_st_metric_values(metrics_display_container, metrics)

    metrics_visualization_container = st.container()
    display_metric_visualizations(
        metrics_visualization_container, metrics, add_text=True, add_sphere=True)

    # Interactive Calculators
    metric_interactive_calculator_container = st.container()
    display_interactive_calculators(
        metric_interactive_calculator_container, metrics, grid=True)

    # with viz_tab1:
    #     st.markdown("<h2 style='text-align: center;'>Floor Flexibility: Column-Free FAR</h2>", unsafe_allow_html=True)
    #     st.markdown(r"""
    #         The formula for calculating the Column-Free Floor Area Ratio can be expressed as:

    #         $$
    #         \text{Column-Free Floor Area Ratio} = \frac{\text{Total Column-Free Floor Area (m²)}}{\text{Total Floor Area (m²)}}
    #         $$
    #     """, unsafe_allow_html=True)
    #     st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {column_free_floor_area_ratio:.2f}</h3>", unsafe_allow_html=True)
    #     with st.container():
    #         st.components.v1.html(create_sphere_visualization("viz1", column_free_floor_area_ratio, "Column-Free FAR"), height=400)

    # with viz_tab2:
    #     st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
    #     st.markdown(r"""
    #         The formula for calculating the Load Capacity per Square Meter can be expressed as:

    #         $$
    #         \text{Load Capacity per Square Meter (kg/m²)} = \frac{\text{Load Capacity (kg)}}{\text{Self Weight of Structure (kg)}}
    #         $$
    #     """, unsafe_allow_html=True)
    #     st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {load_capacity_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
    #     with st.container():
    #         st.components.v1.html(create_sphere_visualization("viz2", load_capacity_per_square_meter, "Load Capacity"), height=400)

    # with viz_tab3:
    #     st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Material Efficiency Ratio</h2>", unsafe_allow_html=True)
    #     st.markdown(r"""
    #         The formula for calculating the Material Efficiency Ratio can be expressed as:

    #         $$
    #         \text{Material Efficiency Ratio} = \frac{\text{Theoretical Minimum Material Usage (kg)}}{\text{Actual Material Usage (kg)}}
    #         $$
    #     """, unsafe_allow_html=True)
    #     st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {material_efficiency_ratio:.2f}</h3>", unsafe_allow_html=True)
    #     with st.container():
    #         st.components.v1.html(create_sphere_visualization("viz3", material_efficiency_ratio, "Material Efficiency"), height=400)

    # with viz_tab4:
    #     st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)
    #     st.markdown(r"""
    #         The formula for calculating the Embodied Carbon Emissions per Square Meter can be expressed as:

    #         $$
    #         \text{Embodied Carbon Emissions per Square Meter (kg/m²)} = \frac{\text{Total Embodied Carbon Emissions (kg)}}{\text{Usable Floor Area (m²)}}
    #         $$
    #     """, unsafe_allow_html=True)
    #     st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {embodied_carbon_emissions_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
    #     with st.container():
    #         st.components.v1.html(create_sphere_visualization("viz4", embodied_carbon_emissions_per_square_meter, "Embodied Carbon"), height=400)
