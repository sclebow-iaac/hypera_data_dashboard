import streamlit as st
import pandas as pd
import plotly.express as px

# Define the function to run the dashboard

def run(metric_col1: st.delta_generator.DeltaGenerator, metric_col2: st.delta_generator.DeltaGenerator, selected_team: str) -> None:
    metric_col1.metric("Unit Types", "4")
    metric_col2.metric("Normalized Travel Time", "0.8 (hours)")

    number_of_units = [40, 60, 30, 20]  
    unit_types = ['Housing', 'Social', 'Commercial', 'Open Space']
    total_number_of_units = sum(number_of_units)

    # Compute the formula
    numerator = sum(
        units * (units - 1) for units in number_of_units
    )
    denominator = total_number_of_units * (total_number_of_units - 1)

    if denominator != 0:  # Avoid division by zero
        calculated_value = 1 - (numerator / denominator)
    else:
        calculated_value = None  # Handle division by zero case

    # Residential-specific chart
    residential_data = pd.DataFrame({
        'Unit Type': unit_types,
        'Number of Units': number_of_units
    })
    res_chart = px.bar(residential_data, x='Unit Type', y='Number of Units')
    res_chart.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    st.plotly_chart(res_chart, use_container_width=True)

    st.markdown("""
    <h2 style='text-align: center, font-size: 24px;'>Mixed Use Index</h2>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the metric can be expressed as:
        
        $$ 
        1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}
        $$
    """, unsafe_allow_html=True)

    st.markdown("")

    # Display the computed value
    if calculated_value is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {calculated_value:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

