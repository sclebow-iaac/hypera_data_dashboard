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

    st.subheader("Team Performance Above Goal (Logarithmic Scale)")

    # Add a metric card for each team in columns
    cols = st.columns(len(team_performance))
    for idx, (team_name, data) in enumerate(team_performance.items()):
        with cols[idx]:
            # Determine background color based on score
            bg_color = "#D6F6D6" if data['total_score'] > 0 else "#FFD6D6"  # Light green for positive, light red for negative
            text_color = "#006400" if data['total_score'] > 0 else "#8B0000"  # Dark green for positive, dark red for negative
            
            # Create a styled metric with colored background
            st.markdown(
                f"""
                <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 5px;">{team_name}</div>
                    <div style="font-size: 1.5rem; color: {text_color};">{data['total_score']:.1f}%</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            # Add a hidden tooltip since custom HTML doesn't support native tooltips
            st.markdown(
                """<div style="font-size: 0.7rem; text-align: center; color: gray;">Average performance across all KPIs</div>""",
                unsafe_allow_html=True
            )

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

    # Add positive bars with team-specific colors
    fig.add_trace(go.Bar(
        x=performance_df['Team'],
        y=[signed_log(x, log_offset) if x > 0 else 0 for x in performance_df['Score']],
        marker_color='#00CC00',
        name='Above Target',
        text=[f"+{x:.1f}%" if x > 0 else "" for x in performance_df['Score']],
        textposition='auto',
    ))

    # Add negative bars with team-specific colors but darker shade
    fig.add_trace(go.Bar(
        x=performance_df['Team'],
        y=[-signed_log(-x, log_offset) if x < 0 else 0 for x in performance_df['Score']],
        marker_color='#FF4444',
        name='Below Target',
        text=[f"{x:.1f}%" if x < 0 else "" for x in performance_df['Score']],
        textposition='auto',
    ))

    # Calculate tick values for the y-axis
    max_abs_log = max(abs(signed_log(x, log_offset)) for x in performance_df['Score'])
    # Round up to the next integer to get a clean range
    max_abs_log_rounded = np.ceil(max_abs_log)
    
    # Create ticks at powers of 10 in both positive and negative directions
    pos_log_ticks = [0]  # Start with zero
    for i in range(int(max_abs_log_rounded) + 1):
        if i > 0:  # Skip 0 as we already added it
            pos_log_ticks.append(i)  # Add powers of 10: 1, 2, 3... (log10(10), log10(100), log10(1000))
    
    # Create negative counterparts
    log_ticks = sorted([-x for x in pos_log_ticks if x > 0] + pos_log_ticks)
    
    # Calculate the actual percentage values these log ticks represent - EXACT powers of 10
    tick_values = []
    for x in log_ticks:
        if x == 0:
            tick_values.append(0)
        else:
            # Use exact powers of 10 for the tick labels
            sign = np.sign(x)
            value = sign * (10 ** abs(x))
            tick_values.append(value)

    # Update layout to match overall_statistics.py style
    fig.update_layout(
        xaxis_title="Teams",
        yaxis_title="Performance Above Goal (%) - Log Scale",
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
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=log_ticks,
            ticktext=[f"{x:.1f}%" for x in tick_values],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            gridcolor='rgba(0,0,0,0.1)',
            range=[-1, max_abs_log * 1.2],  # Extend the range a bit for better visualization
        ),
        margin=dict(l=1, r=40, t=10, b=1),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto Mono",
            font_color="#2c3e50",
        )
    )

    # Add black outlines to bars to match overall_statistics.py style
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))

    # Add annotation explaining the scale
    fig.add_annotation(
        text="Note: Y-axis uses logarithmic scale for better visualization",
        xref="paper", yref="paper",
        x=0, y=1.02,
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
    
    st.markdown(f"<div style='text-align: center;'><b>Most Overperforming Team: {most_overperforming_team[0]}</b> with a score of <b>{most_overperforming_team[1]['total_score']:.1f}%</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><b>Most Overperforming Metric:</b> {most_overperforming_metric['name']} with a score of <b>{most_overperforming_metric['score']:.1f}%</b></div>", unsafe_allow_html=True)

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




