import streamlit as st
import pandas as pd
import plotly.express as px

def run(metric_col1: st.delta_generator.DeltaGenerator, metric_col2: st.delta_generator.DeltaGenerator, selected_team: str) -> None:
    # Define the variables for the new formula
    energy_generation = [800, 850, 900, 950]  # Example values over time
    energy_demand = [500, 600, 700, 800]  # Example values over time

    # Compute the energy self-sufficiency ratio for each time point
    energy_self_sufficiency_ratios = [
        gen / demand if demand != 0 else None
        for gen, demand in zip(energy_generation, energy_demand)
    ]

    # Create a DataFrame for the line chart
    time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
    line_data = pd.DataFrame({
        'Time': time_points,
        'Energy Generation': energy_generation,
        'Energy Demand': energy_demand,
        'Energy Self-Sufficiency Ratio': energy_self_sufficiency_ratios
    })

    # Create a line chart
    line_chart = px.line(line_data, x='Time', y=['Energy Generation', 'Energy Demand', 'Energy Self-Sufficiency Ratio'],
                            labels={'value': 'Energy (kWh)', 'variable': 'Metrics'},
                            title='Energy Metrics Over Time')
    line_chart.update_layout(
        title_x=0.5,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(line_chart, use_container_width=True)

    # Display the last calculated value for energy self-sufficiency ratio
    if energy_self_sufficiency_ratios[-1] is not None:
        st.markdown(f"<h3 style='text-align: center;'>Latest Energy Self-Sufficiency Ratio: {energy_self_sufficiency_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Define the variables for the new formula
    food_production = [800, 850, 900, 950]  # Example values over time
    food_demand = [500, 600, 700, 800]  # Example values over time

    # Compute the food self-sufficiency ratio for each time point
    food_self_sufficiency_ratios = [
        gen / demand if demand != 0 else None
        for gen, demand in zip(food_production, food_demand)
    ]

    # Create a DataFrame for the line chart
    time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
    line_data = pd.DataFrame({
        'Time': time_points,
        'Food Production': food_production,
        'Food Demand': food_demand,
        'Food Self-Sufficiency Ratio': food_self_sufficiency_ratios
    })

    # Create a line chart
    line_chart = px.line(line_data, x='Time', y=['Food Production', 'Food Demand', 'Food Self-Sufficiency Ratio'],
                            labels={'value': 'Food (kg)', 'variable': 'Metrics'},
                            title='Food Metrics Over Time')
    line_chart.update_layout(
        title_x=0.5,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(line_chart, use_container_width=True)

    # Display the last calculated value for food self-sufficiency ratio
    if food_self_sufficiency_ratios[-1] is not None:
        st.markdown(f"<h3 style='text-align: center;'>Latest Food Self-Sufficiency Ratio: {food_self_sufficiency_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Define the variables for the new formula
    recycled_water = [800, 850, 900, 950]  # Example values over time
    wastewater_production = [500, 600, 700, 800]  # Example values over time

    # Compute the recycled water ratio for each time point
    recycled_water_ratios = [
        gen / demand if demand != 0 else None
        for gen, demand in zip(recycled_water, wastewater_production)
    ]

    # Create a DataFrame for the line chart
    time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
    line_data = pd.DataFrame({
        'Time': time_points,
        'Recycled Water': recycled_water,
        'Wastewater Production': wastewater_production,
        'Recycled Water Ratio': recycled_water_ratios
    })

    # Create a line chart
    line_chart = px.line(line_data, x='Time', y=['Recycled Water', 'Wastewater Production', 'Recycled Water Ratio'],
                            labels={'value': 'Recycled Water (m³)', 'variable': 'Metrics'},
                            title='Recycled Water Metrics Over Time')
    line_chart.update_layout(
        title_x=0.5,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(line_chart, use_container_width=True)

    # Display the last calculated value for recycled water ratio
    if recycled_water_ratios[-1] is not None:
        st.markdown(f"<h3 style='text-align: center;'>Latest Recycled Water Ratio: {recycled_water_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Define the variables for the new formula
    recycled_solid_waste = [800, 850, 900, 950]  # Example values over time
    solid_waste_production = [500, 600, 700, 800]  # Example values over time

    # Compute the solid waste utilization ratio for each time point
    solid_waste_utilization_ratios = [
        gen / demand if demand != 0 else None
        for gen, demand in zip(recycled_solid_waste, solid_waste_production)
    ]

    # Create a DataFrame for the line chart
    time_points = ['Q1', 'Q2', 'Q3', 'Q4']  # Example time points
    line_data = pd.DataFrame({
        'Time': time_points,
        'Recycled Solid Waste': recycled_solid_waste,
        'Solid Waste Production': solid_waste_production,
        'Solid Waste Utilization Ratio': solid_waste_utilization_ratios
    })

    # Create a line chart
    line_chart = px.line(line_data, x='Time', y=['Recycled Solid Waste', 'Solid Waste Production', 'Solid Waste Utilization Ratio'],
                            labels={'value': 'Recycled Solid Waste (kg)', 'variable': 'Metrics'},
                            title='Solid Waste Utilization Metrics Over Time')
    line_chart.update_layout(
        title_x=0.5,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(line_chart, use_container_width=True)

    # Display the last calculated value for solid waste utilization ratio
    if solid_waste_utilization_ratios[-1] is not None:
        st.markdown(f"<h3 style='text-align: center;'>Latest Solid Waste Utilization Ratio: {solid_waste_utilization_ratios[-1]:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
