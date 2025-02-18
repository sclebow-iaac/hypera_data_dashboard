import streamlit as st

def run(metric_col1: st.delta_generator.DeltaGenerator, metric_col2: st.delta_generator.DeltaGenerator, selected_team: str) -> None:
    occupancy_efficiency = 80
    utilization_rate = 34
    n = 5
    active_hours = 12
    function_exchange_factor = 4
    total_available_hours_per_day = 13
    total_spaces_available = 50

    metric_col1.metric("Number of Spaces", n)

    metrics_data = {
        "Occupancy Efficiency": occupancy_efficiency,  # No units here for calculations
        "Utilization Rate": utilization_rate,  # No units here for calculations
        "Active Hours": active_hours,  # No units here for calculations
        "Function Exchange Factor": function_exchange_factor,  # No units here for calculations
        "Total Available Hours per Day": total_available_hours_per_day,  # No units here for calculations
        "Total Spaces Available": total_spaces_available  # No units here for calculations
    }

    # Create columns for metrics based on the number of metrics to display
    metric_cols = st.columns(len(metrics_data))  # Create a column for each metric

    for i, (metric_name, value) in enumerate(metrics_data.items()):
        col = metric_cols[i]  # Access the corresponding column

        # Display the metric with units in the name
        if metric_name == "Occupancy Efficiency":
            col.metric(metric_name, f"{value}%", help="Percentage of occupancy efficiency")
        elif metric_name == "Utilization Rate":
            col.metric(metric_name, f"{value}%", help="Percentage of utilization rate")
        elif metric_name == "Active Hours":
            col.metric(metric_name, f"{value} hours", help="Total active hours")
        elif metric_name == "Function Exchange Factor":
            col.metric(metric_name, f"{value}", help="Unitless function exchange factor")
        elif metric_name == "Total Available Hours per Day":
            col.metric(metric_name, f"{value} hours", help="Total available hours per day")
        elif metric_name == "Total Spaces Available":
            col.metric(metric_name, f"{value}", help="Total number of spaces available")

        # Ensure value is a valid number before conversion
        try:
            # Use the raw value for calculations
            raw_value = float(value)  # Convert to float for calculations
            if metric_name in ["Occupancy Efficiency", "Utilization Rate"]:
                max_value = 100
            elif metric_name == "Active Hours":
                max_value = 24
            elif metric_name == "Function Exchange Factor":
                max_value = 10
            elif metric_name == "Total Available Hours per Day":
                max_value = 24
            elif metric_name == "Total Spaces Available":
                max_value = 100
            
            progress_bar = col.progress(raw_value / max_value)  # Use raw_value for progress bar
        except (ValueError, TypeError) as e:
            print(f"Error converting value for {metric_name}: {value}. Error: {e}")
            progress_bar = col.progress(0)  # Default to 0 if conversion fails

        col.markdown(f"""
        <div style="text-align: center; font-size: 24px;">
        {value} / {max_value}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")


    # Compute the formula
    numerator = utilization_rate * active_hours * function_exchange_factor # what kind of summation we need to do here
    denominator = total_available_hours_per_day * total_spaces_available

    if denominator != 0:  # Avoid division by zero
        calculated_value = numerator / denominator
    else:
        calculated_value = None  # Handle division by zero case

    st.markdown("")
    st.markdown("")

    st.markdown("<hr>", unsafe_allow_html=True)  # Add a line after the metric

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the metric can be expressed as:
        
        $$ 
        \frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor)}{TotalAvailableHoursPerDay \cdot TotalSpacesAvailable}
        $$
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    if calculated_value is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Occupancy Efficiency: {calculated_value:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)
