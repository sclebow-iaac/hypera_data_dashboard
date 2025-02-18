import streamlit as st
import pandas as pd
import plotly.express as px

def run(metric_col1: st.delta_generator.DeltaGenerator, metric_col2: st.delta_generator.DeltaGenerator, selected_team: str) -> None:
    # Define the variables for daylight in different parts of the building
    time_of_day = ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM']  # Example time points
    daylight_amounts = {
        'North Side': [50, 70, 90, 60, 30],  # Example daylight amounts for the North side
        'South Side': [30, 50, 80, 100, 70],  # Example daylight amounts for the South side
        'East Side': [60, 80, 100, 90, 40],  # Example daylight amounts for the East side
        'West Side': [40, 60, 70, 80, 50]    # Example daylight amounts for the West side
    }

    # Total incoming daylight (example value)
    total_incoming_daylight = 400  # Example total incoming daylight value

    # Create a DataFrame for the line chart
    daylight_data = pd.DataFrame(daylight_amounts, index=time_of_day)

    # Calculate the total daylight amount used
    total_daylight_used = daylight_data.sum().sum()  # Sum of all daylight amounts used

    # Compute the ratio of daylight amount used to total incoming daylight
    daylight_ratio = total_daylight_used / total_incoming_daylight if total_incoming_daylight != 0 else None

    # Create a line chart
    daylight_chart = px.line(daylight_data, 
                                title='Daylight Amount in Different Parts of the Building',
                                labels={'value': 'Daylight Amount (lux)', 'variable': 'Building Side'},
                                markers=True)
    daylight_chart.update_layout(
        title_x=0.35,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(daylight_chart, use_container_width=True)

    # Display the daylight ratio metric
    if daylight_ratio is not None:
        st.markdown(f"<h3 style='text-align: center;'>Daylight Utilization Ratio: {daylight_ratio:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    # Optionally, display a summary of the daylight amounts
    st.markdown("<h3 style='text-align: center;'>Daylight Amounts Summary</h3>", unsafe_allow_html=True)
    st.write(daylight_data)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric
    
    # Add the new metric for Normalized Value: Combined Metric
    st.markdown("<h2>Primary Daylight Factor and Solar Loads Control for Residential and Work Spaces</h2>", unsafe_allow_html=True)

    # Example values for the calculation
    weight_residential = 0.5  
    weight_work = 0.5  
    residential_area_with_daylight = 100  
    total_residential_area = 200  
    work_area_with_daylight = 150  
    total_work_area = 300  

    # Calculate the normalized value
    normalized_value = (
        weight_residential * (residential_area_with_daylight / total_residential_area) +
        weight_work * (work_area_with_daylight / total_work_area) * (10 / 7)
    )

    # Add the formula for the normalized value
    st.markdown(r"""
        The formula for calculating the Normalized Value can be expressed as:

        $$ 
        \text{Normalized Value} = 
        weight_{\text{residential}} \cdot \frac{\text{ResidentialAreaWithDaylight}}{\text{TotalResidentialArea}} + 
        weight_{\text{work}} \cdot \frac{\text{WorkAreaWithDaylight}}{\text{TotalWorkArea}} \cdot \frac{10}{7}
        $$
""", unsafe_allow_html=True)

    # Display the normalized value
    st.metric("Normalized Value: Combined Metric", f"{normalized_value:.2f}", help="Combined metric based on residential and work areas with daylight")

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Define the angles and their corresponding effectiveness for each panel
    angles = [0, 15, 30, 45, 60, 75, 90]  # Example angles in degrees
    effectiveness = [0.1, 0.5, 0.8, 1.0, 0.7, 0.4, 0.2]  # Example effectiveness values

    # Create a DataFrame for the line chart
    angle_data = pd.DataFrame({
        'Angle (degrees)': angles,
        'Effectiveness': effectiveness
    })

    # Compute the optimal angle (e.g., the angle with the highest effectiveness)
    optimal_angle = angles[effectiveness.index(max(effectiveness))]

    # Create a line chart
    angle_chart = px.line(angle_data, 
                            x='Angle (degrees)', 
                            y='Effectiveness', 
                            title='Effectiveness of Panel Angles',
                            markers=True)
    angle_chart.update_layout(
        title_x=0.5,  # Center the title
        paper_bgcolor='rgba(0,0,0,0)',  # Set paper background to transparent
        plot_bgcolor='rgba(0,0,0,0)',   # Set plot background to transparent
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the line chart
    st.plotly_chart(angle_chart, use_container_width=True)

    # Display the optimal angle metric
    st.markdown(f"<h3 style='text-align: center;'>Optimal Angle for Panel Movement: {optimal_angle}°</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Example values for energy generation and energy required
    energy_generation = 1500  
    energy_required_by_industrial_team = 1000  

    # Calculate the ratio
    ratio = energy_generation / energy_required_by_industrial_team

    # Create a DataFrame for the bar chart
    data = {
        'Metric': ['Energy Generation', 'Energy Required by Industrial Team'],
        'Value': [energy_generation, energy_required_by_industrial_team]
    }

    df = pd.DataFrame(data)

    # Create the bar chart
    fig = px.bar(df, x='Metric', y='Value',
            labels={'Value': 'Energy (kWh)', 'Metric': 'Metrics'},
            color='Metric')

    # Add the ratio as a text annotation
    fig.add_annotation(
        x='Energy Generation',
        y=ratio,
        text=f'Ratio: {ratio:.2f}',
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
        )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"<h3 style='text-align: center;'>Energy Generation Ratio: {ratio:.2f}</h3>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric
