import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from dashboards.dashboard import display_st_metric_values
from dashboards import (
    service_dashboard, structure_dashboard, residential_dashboard, 
    industrial_dashboard, facade_dashboard
)
from data_extraction import (
    service_extractor, structure_extractor, residential_extractor, 
    industrial_extractor, facade_extractor
)
from datetime import datetime, timedelta

def analyze_team_performance(service_metrics, structure_metrics, residential_metrics, industrial_metrics, facade_metrics):
    st.subheader("Team Performance Analysis")

    # Create a dictionary to store team performance data
    team_performance = {
        'Service': {'metrics': service_metrics, 'total_score': 0, 'kpi_scores': []},
        'Structure': {'metrics': structure_metrics, 'total_score': 0, 'kpi_scores': []},
        'Residential': {'metrics': residential_metrics, 'total_score': 0, 'kpi_scores': []},
        'Industrial': {'metrics': industrial_metrics, 'total_score': 0, 'kpi_scores': []},
        'Facade': {'metrics': facade_metrics, 'total_score': 0, 'kpi_scores': []}
    }

    # Calculate performance scores for each team
    for team_name, team_data in team_performance.items():
        metrics = team_data['metrics']
        for metric in metrics:
            actual_value = float(metric.value) if isinstance(metric.value, (int, float)) else float(metric.value.replace('%', '')) / 100
            ideal_value = float(metric.ideal_value) if isinstance(metric.ideal_value, (int, float)) else float(metric.ideal_value.replace('%', '')) / 100
            
            if ideal_value != 0:  # Avoid division by zero
                percentage_diff = ((actual_value - ideal_value) / abs(ideal_value)) * 100
            else:
                percentage_diff = 0
            
            team_data['kpi_scores'].append({
                'name': metric.title,
                'actual': actual_value,
                'ideal': ideal_value,
                'score': percentage_diff
            })
        
        # Calculate average score for the team
        team_data['total_score'] = sum(kpi['score'] for kpi in team_data['kpi_scores']) / len(team_data['kpi_scores'])

    # Prepare data for bar chart


    # Create DataFrame for the bar chart
    performance_df = pd.DataFrame([
        {'Team': team_name, 'Score': data['total_score']}
        for team_name, data in team_performance.items()
    ])

    # Function to apply signed log transformation while preserving zero
    def signed_log(x, log_offset=1):
        if abs(x) < 1:  # Treat very small values as zero
            return 0
        sign = np.sign(x)
        log_val = np.log10(abs(x) + log_offset)
        return sign * log_val

    # Calculate log offset based on smallest non-zero absolute value
    non_zero_vals = [abs(x) for x in performance_df['Score'] if abs(x) > 0.01]
    min_non_zero = min(non_zero_vals) if non_zero_vals else 1
    log_offset = min_non_zero / 10
    
    # Create bar chart with both positive and negative bars
    fig = go.Figure()

    # Add positive bars
    fig.add_trace(go.Bar(
        x=performance_df['Team'],
        y=[signed_log(x, log_offset) if x > 0 else 0 for x in performance_df['Score']],
        marker_color='#00CC00',
        name='Above Target',
        text=[f"+{x:.1f}%" if x > 0 else "" for x in performance_df['Score']],
        textposition='auto',
    ))

    # Add negative bars
    fig.add_trace(go.Bar(
        x=performance_df['Team'],
        y=[-signed_log(-x, log_offset) if x < 0 else 0 for x in performance_df['Score']],  # Negate the log for negative values
        marker_color='#FF4444',
        name='Below Target',
        text=[f"{x:.1f}%" if x < 0 else "" for x in performance_df['Score']],
        textposition='auto',
    ))

    # Calculate tick values for the y-axis
    max_abs_log = max(abs(signed_log(x, log_offset)) for x in performance_df['Score'])
    tick_count = 11  # Odd number to include zero
    log_ticks = np.linspace(-max_abs_log, max_abs_log, tick_count)
    tick_values = [(10**abs(x) - log_offset) * np.sign(x) for x in log_ticks]

    # Update layout
    fig.update_layout(
        title={
            'text': "Team Performance Comparison (Logarithmic Scale)",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Teams",
        yaxis_title="Performance Score (%) - Log Scale",
        height=500,
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=log_ticks,
            ticktext=[f"{x:.1f}%" for x in tick_values],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            gridcolor='rgba(0,0,0,0.1)'
        )
    )

    # Add annotation explaining the scale
    fig.add_annotation(
        text="Note: Y-axis uses logarithmic scale for better visualization",
        xref="paper", yref="paper",
        x=0, y=1.05,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor='left'
    )

    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    # Display detailed performance table
    st.subheader("Detailed Performance Analysis")
    
    # Create a DataFrame for the performance table
    performance_data = []
    for team_name, team_data in team_performance.items():
        for kpi in team_data['kpi_scores']:
            # Determine status with symbols
            if kpi['score'] > 0:
                status = "✅ Exceeding"
            elif kpi['score'] < 0:
                status = "❌ Below Target"
            else:
                status = "➖ On Target"
                
            performance_data.append({
                'Team': team_name,
                'KPI': kpi['name'],
                'Actual Value': f"{kpi['actual']:.2f}",
                'Target Value': f"{kpi['ideal']:.2f}",
                'Difference %': f"{kpi['score']:.1f}%",
                'Status': status  # Added status column with symbols
            })
    
    df = pd.DataFrame(performance_data)

    # Display the DataFrame
    st.dataframe(
        df,
        height=400,
        use_container_width=True
    )

    # Add Most Overperforming Team Banner
    most_overperforming_team = max(team_performance.items(), key=lambda x: x[1]['total_score'])
    most_overperforming_metric = max(most_overperforming_team[1]['kpi_scores'], key=lambda x: x['score'])
    
    st.markdown(f"### Most Overperforming Team: **{most_overperforming_team[0]}**")
    st.markdown(f"**Total Score:** {most_overperforming_team[1]['total_score']:.1f}%")
    st.markdown(f"**Most Overperforming Metric:** {most_overperforming_metric['name']} with a score of **{most_overperforming_metric['score']:.1f}%**")

def run(project_tree, project_id):
    # Get metrics from extractors
    extractors = [
        service_extractor, structure_extractor, residential_extractor, 
        industrial_extractor, facade_extractor
    ]
    dashboards = [
        service_dashboard, structure_dashboard, residential_dashboard, 
        industrial_dashboard, facade_dashboard
    ]
    team_metrics = []
    for extractor, dashboard in zip(extractors, dashboards):
        # Extract data
        verified, team_data, model_data = extractor.extract(attribute_display=False)
        metrics = dashboard.generate_metrics(verified, team_data, model_data)
        team_metrics.append(metrics)
        
    # Unpack the metrics
    service_metrics, structure_metrics, residential_metrics, industrial_metrics, facade_metrics = team_metrics

    # Create 9 columns: 5 for content and 4 for padding
    cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])

    # Display team names
    for idx, team in enumerate(['services', 'structure', 'residential', 'industrial', 'facade']):
        with cols[idx * 2]:
            st.markdown(f"<h3 style='text-align: center;'>{team.capitalize()}</h3>", unsafe_allow_html=True)

    # Create another set of columns for metrics
    cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])

    with cols[0]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Service KPIs</strong></p>", unsafe_allow_html=True)

    with cols[2]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Structure KPIs</strong></p>", unsafe_allow_html=True)

    with cols[4]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Residential KPIs</strong></p>", unsafe_allow_html=True)

    with cols[6]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Industrial KPIs</strong></p>", unsafe_allow_html=True)

    with cols[8]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Facade KPIs</strong></p>", unsafe_allow_html=True)

    # Create another set of columns for metrics
    cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])
    
    # Service column (index 0)
    with cols[0]:
        display_st_metric_values(container=cols[0], metrics=service_metrics, use_columns=False, include_header=False)
        
    # Structure column (index 2)
    with cols[2]:
        display_st_metric_values(container=cols[2], metrics=structure_metrics, use_columns=False, include_header=False)
    
    # Residential column (index 4)
    with cols[4]:
        display_st_metric_values(container=cols[4], metrics=residential_metrics, use_columns=False, include_header=False)
    
    # Industrial column (index 6)
    with cols[6]:
        display_st_metric_values(container=cols[6], metrics=industrial_metrics, use_columns=False, include_header=False)

    # Facade column (index 8)
    with cols[8]:
        display_st_metric_values(container=cols[8], metrics=facade_metrics, use_columns=False, include_header=False)

    # After displaying the KPIs, add the performance analysis
    st.markdown("---")  # Add a separator

    # Analyze and display team performance
    analyze_team_performance(
        service_metrics,
        structure_metrics,
        residential_metrics,
        industrial_metrics,
        facade_metrics
    )




