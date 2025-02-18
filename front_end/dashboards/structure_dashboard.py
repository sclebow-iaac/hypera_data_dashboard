import streamlit as st
import pandas as pd
import plotly.express as px

def run(metric_col1: st.delta_generator.DeltaGenerator, metric_col2: st.delta_generator.DeltaGenerator, selected_team: str) -> None:
    
    #floor flexibility:column-free FAR
    # Define the variables for the new formula
    total_column_free_floor_area = 800  # Example value for total column-free floor area
    total_floor_area = 1000  # Example value for total floor area

    # Compute the formula
    if total_floor_area != 0:  # Avoid division by zero
        column_free_floor_area_ratio = total_column_free_floor_area / total_floor_area
    else:
        column_free_floor_area_ratio = None  # Handle division by zero case

    # Structure-specific chart

    st.markdown("<h2 style='text-align: center;'>Floor Flexibility: Column-Free FAR</h2>", unsafe_allow_html=True)
    structure_data = pd.DataFrame({
        'Number of Columns': [10],
        'Total Floor Area': [1000]
    })
    structure_chart = px.bar(structure_data, x='Number of Columns', y='Total Floor Area')
    structure_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(structure_chart, use_container_width=True)

    # Add major text underneath the metrics
    st.markdown("<h2 style='text-align: center; font-size: 24px;'>Floor Flexibility: Column-Free Floor Area Ratio</h2>", unsafe_allow_html=True)

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the Column-Free Floor Area Ratio can be expressed as:
        
        $$ 
        \text{Column-Free Floor Area Ratio} = \frac{\text{Total Column-Free Floor Area (m²)}}{\text{Total Floor Area (m²)}}
        $$
    """, unsafe_allow_html=True)

    # Display the computed value
    if column_free_floor_area_ratio is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {column_free_floor_area_ratio:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    #structural efficiency: embodied carbon emissions per square meter
    # Define the variables for the new formula
    total_embodied_carbon_emissions = 800  
    usable_floor_area = 1000  

    # Compute the formula
    if usable_floor_area != 0:  # Avoid division by zero
        embodied_carbon_emissions_per_square_meter = total_embodied_carbon_emissions / usable_floor_area
    else:
        embodied_carbon_emissions_per_square_meter = None  # Handle division by zero case

    # Structure-specific chart

    st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)
    structure_data = pd.DataFrame({
        'Total Embodied Carbon Emmissions': [10],
        'Floor Area': [1000]
    })
    structure_chart = px.bar(structure_data, x='Total Embodied Carbon Emmissions', y='Floor Area')
    structure_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(structure_chart, use_container_width=True)

    # Add major text underneath the metrics
    st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the Embodied Carbon Emissions per Square Meter can be expressed as:
        
        $$ 
        \text{Embodied Carbon Emissions per Square Meter (kg/m²)} = \frac{\text{Total Embodied Carbon Emissions (kg)}}{\text{Usable Floor Area (m²)}}
        $$
    """, unsafe_allow_html=True)

    # Display the computed value
    if embodied_carbon_emissions_per_square_meter is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {embodied_carbon_emissions_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    #structural efficiency: load capacity per square meter
    # Define the variables for the new formula
    load_capacity = 800  
    self_weight_of_structure = 500  

    # Compute the formula
    if self_weight_of_structure != 0:  # Avoid division by zero
        load_capacity_per_square_meter = load_capacity / self_weight_of_structure
    else:
        load_capacity_per_square_meter = None  # Handle division by zero case

    # Structure-specific chart

    st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
    structure_data = pd.DataFrame({
        'Load Capacity': [10],
        'Self Weight of Structure': [1000]
    })
    structure_chart = px.bar(structure_data, x='Load Capacity', y='Self Weight of Structure')
    structure_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(structure_chart, use_container_width=True)

    # Add major text underneath the metrics
    st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the Load Capacity per Square Meter can be expressed as:
        
        $$ 
        \text{Load Capacity per Square Meter (kg/m²)} = \frac{\text{Load Capacity (kg)}}{\text{Self Weight of Structure (kg)}}
        $$
    """, unsafe_allow_html=True)

    # Display the computed value
    if load_capacity_per_square_meter is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {load_capacity_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    #structural efficiency: material efficiency ratio
    # Define the variables for the new formula
    theoretical_minimum_material_usage = 800  
    actual_material_usage = 500  

    # Compute the formula
    if actual_material_usage != 0:  # Avoid division by zero
        material_efficiency_ratio = theoretical_minimum_material_usage / actual_material_usage
    else:
        material_efficiency_ratio = None  # Handle division by zero case

    # Structure-specific chart

    st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
    structure_data = pd.DataFrame({
        'Theoretical Minimum Material Usage': [10],
        'Actual Material Usage': [1000]
    })
    structure_chart = px.bar(structure_data, x='Theoretical Minimum Material Usage', y='Actual Material Usage')
    structure_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(structure_chart, use_container_width=True)

    # Add major text underneath the metrics
    st.markdown("<h2 style='text-align: center; font-size: 24px;'>Structural Flexibility: Material Efficiency Ratio</h2>", unsafe_allow_html=True)

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the Material Efficiency Ratio can be expressed as:
        
        $$ 
        \text{Material Efficiency Ratio} = \frac{\text{Theoretical Minimum Material Usage (kg)}}{\text{Actual Material Usage (kg)}}
        $$
    """, unsafe_allow_html=True)

    # Display the computed value
    if material_efficiency_ratio is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {material_efficiency_ratio:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)
