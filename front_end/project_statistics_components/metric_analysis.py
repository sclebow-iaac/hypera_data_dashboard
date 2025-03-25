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
    st.subheader("Team Overperformance Analysis")

    # Create a dictionary to store team performance data
    team_performance = {
        'Service': {'metrics': service_metrics, 'overperformance_score': 0, 'kpi_scores': []},
        'Structure': {'metrics': structure_metrics, 'overperformance_score': 0, 'kpi_scores': []},
        'Residential': {'metrics': residential_metrics, 'overperformance_score': 0, 'kpi_scores': []},
        'Industrial': {'metrics': industrial_metrics, 'overperformance_score': 0, 'kpi_scores': []},
        'Facade': {'metrics': facade_metrics, 'overperformance_score': 0, 'kpi_scores': []}
    }

    # Calculate overperformance scores for each team
    for team_name, team_data in team_performance.items():
        metrics = team_data['metrics']
        for metric in metrics:
            if metric.ideal_value != 0:  # Avoid division by zero
                # Calculate percentage above ideal value
                performance_ratio = (metric.value / metric.ideal_value) * 100
                overperformance = max(performance_ratio - 100, 0)  # Only count values above 100%
            else:
                overperformance = 0
            
            team_data['kpi_scores'].append({
                'name': metric.title,
                'actual': metric.value,
                'ideal': metric.ideal_value,
                'overperformance': overperformance
            })
        
        # Calculate average overperformance for the team
        team_data['overperformance_score'] = sum(kpi['overperformance'] for kpi in team_data['kpi_scores']) / len(team_data['kpi_scores'])

    # Prepare data for visualization
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np

    # Create DataFrame for the visualization
    performance_df = pd.DataFrame([
        {'Team': team_name, 'Overperformance': data['overperformance_score']}
        for team_name, data in team_performance.items()
    ])

    # Add a small constant to avoid log(0)
    min_non_zero = performance_df['Overperformance'][performance_df['Overperformance'] > 0].min()
    log_offset = min_non_zero / 10 if min_non_zero > 0 else 0.1
    
    # Calculate logarithmic values for visualization
    performance_df['Log_Overperformance'] = np.log10(performance_df['Overperformance'] + log_offset)

    # Create bar chart
    fig = go.Figure()

    # Add bars using logarithmic values
    fig.add_trace(go.Bar(
        x=performance_df['Team'],
        y=performance_df['Log_Overperformance'],
        text=performance_df['Overperformance'].round(1).astype(str) + '%',  # Show actual percentages in labels
        textposition='auto',
        marker_color=['#00CC00' if score > 0 else '#808080' for score in performance_df['Overperformance']],
    ))

    # Calculate tick values and labels for logarithmic scale
    max_value = performance_df['Overperformance'].max()
    log_max = np.log10(max_value + log_offset)
    tick_values = np.linspace(0, log_max, 6)
    tick_labels = [f"{(10**val - log_offset):.1f}%" for val in tick_values]

    # Update layout
    fig.update_layout(
        title={
            'text': "Team Overperformance Analysis (Logarithmic Scale)",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Teams",
        yaxis_title="Overperformance (log scale)",
        yaxis=dict(
            tickvals=tick_values,
            ticktext=tick_labels,
            title="Overperformance (logarithmic scale)"
        ),
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Add annotation explaining the scale
    fig.add_annotation(
        text="Note: Y-axis uses logarithmic scale for better visualization",
        xref="paper", yref="paper",
        x=0, y=1.1,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor='left'
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Display detailed overperformance table
    st.subheader("Detailed Overperformance Analysis")
    
    # Create a DataFrame for the performance table
    performance_data = []
    for team_name, team_data in team_performance.items():
        for kpi in team_data['kpi_scores']:
            performance_data.append({
                'Team': team_name,
                'KPI': kpi['name'],
                'Actual Value': f"{kpi['actual']:.2f}",
                'Ideal Value': f"{kpi['ideal']:.2f}",
                'Overperformance': f"{kpi['overperformance']:.1f}%"
            })
    
    df = pd.DataFrame(performance_data)
    st.dataframe(df, use_container_width=True)

    # Display summary of overperforming teams
    st.subheader("Overperformance Summary")
    cols = st.columns(len(team_performance))
    for (team_name, data), col in zip(team_performance.items(), cols):
        with col:
            delta = None
            if data['overperformance_score'] > 0:
                delta = f"Exceeding by {data['overperformance_score']:.1f}%"
            st.metric(
                label=team_name,
                value=f"{data['overperformance_score']:.1f}%",
                delta=delta
            )

    # After the existing summary section
    st.markdown("---")
    st.subheader("Team Performance Analysis")

    # Radar chart in full width
    all_values = [kpi['overperformance'] 
                 for team_data in team_performance.values() 
                 for kpi in team_data['kpi_scores']]
    min_non_zero = min([x for x in all_values if x > 0]) if any(x > 0 for x in all_values) else 0.1
    log_offset = min_non_zero / 10

    fig_radar = go.Figure()

    for team_name, team_data in team_performance.items():
        kpi_scores = [kpi['overperformance'] for kpi in team_data['kpi_scores']]
        # Apply log transformation
        log_scores = [np.log10(score + log_offset) if score > 0 else 0 for score in kpi_scores]
        kpi_names = [kpi['name'] for kpi in team_data['kpi_scores']]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=log_scores,
            theta=kpi_names,
            name=team_name,
            fill='toself',
            opacity=0.6,
            hovertemplate="<b>%{theta}</b><br>" +
                        "Overperformance: %{text}%<br>" +
                        "<extra></extra>",
            text=[f"{score:.1f}" for score in kpi_scores]
        ))

    # Calculate tick values for logarithmic scale
    max_value = max(all_values)
    log_max = np.log10(max_value + log_offset)
    tick_values = np.linspace(0, log_max, 5)
    tick_labels = [f"{(10**val - log_offset):.1f}%" for val in tick_values]

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, log_max],
                tickvals=tick_values,
                ticktext=tick_labels,
                title="Overperformance (log scale)",
                tickfont={'size': 12}
            ),
            angularaxis=dict(
                tickfont={'size': 12}
            )
        ),
        showlegend=True,
        height=600,
        font_family="Roboto Mono",
        legend=dict(
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            orientation="v",
            font=dict(size=12)
        ),
        margin=dict(
            l=50,
            r=150,
            t=80,
            b=80
        )
    )

    # Add annotation explaining the scale
    fig_radar.add_annotation(
        text="Note: Radial axis uses logarithmic scale for better visualization",
        xref="paper", yref="paper",
        x=0, y=-0.15,
        showarrow=False,
        font=dict(size=12, color="gray"),
        xanchor='left'
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Add a detailed breakdown table with sorting capabilities
    st.subheader("Sortable Performance Matrix")
    
    # Create a more detailed DataFrame for analysis
    detailed_df = pd.DataFrame([
        {
            'Team': team_name,
            'KPI': kpi['name'],
            'Actual Value': kpi['actual'],
            'Target Value': kpi['ideal'],
            'Overperformance %': round(kpi['overperformance'], 1),
            'Status': '🟢 Exceeding' if kpi['overperformance'] > 0 else '🔸 At Target' if kpi['overperformance'] == 0 else '🔴 Below Target'
        }
        for team_name, team_data in team_performance.items()
        for kpi in team_data['kpi_scores']
    ])

    # Add styling to the DataFrame
    st.dataframe(
        detailed_df.style.background_gradient(
            subset=['Overperformance %'],
            cmap='RdYlGn',
            vmin=0,
            vmax=detailed_df['Overperformance %'].max()
        ),
        height=400,
        use_container_width=True
    )

    # Add key statistics
    st.subheader("Key Performance Statistics")
    stats_cols = st.columns(3)
    
    with stats_cols[0]:
        top_performer = max(team_performance.items(), key=lambda x: x[1]['overperformance_score'])
        st.metric(
            "Top Performing Team",
            top_performer[0],
            f"{top_performer[1]['overperformance_score']:.1f}% above target"
        )
        
    with stats_cols[1]:
        avg_overperformance = np.mean([team_data['overperformance_score'] 
                                     for team_data in team_performance.values()])
        st.metric(
            "Average Team Overperformance",
            f"{avg_overperformance:.1f}%"
        )
        
    with stats_cols[2]:
        best_kpi = max(
            [(team_name, kpi['name'], kpi['overperformance']) 
             for team_name, team_data in team_performance.items()
             for kpi in team_data['kpi_scores']],
            key=lambda x: x[2]
        )
        st.metric(
            "Highest Individual KPI",
            f"{best_kpi[0]} - {best_kpi[1]}",
            f"{best_kpi[2]:.1f}% above target"
        )

def run(project_tree, project_id):
    # Create 9 columns: 5 for content and 4 for padding
    cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])

    # Display team names
    for idx, team in enumerate(['services', 'structure', 'residential', 'industrial', 'facade']):
        with cols[idx * 2]:
            st.markdown(f"<h3 style='text-align: center;'>{team.capitalize()}</h3>", unsafe_allow_html=True)

    # Create another set of columns for metrics
    cols = st.columns([10, 1, 10, 1, 10, 1, 10, 1, 10])

    # Service column (index 0)
    with cols[0]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Service KPIs</strong></p>", unsafe_allow_html=True)
        
        # Call the service dashboard to get the metrics
        verified, team_data, model_data = service_extractor.extract(attribute_display=False)
        service_metrics = service_dashboard.generate_metrics(verified, team_data)
        display_st_metric_values(container=cols[0], metrics=service_metrics, use_columns=False, include_header=False)
        
    # Structure column (index 2)
    with cols[2]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Structure KPIs</strong></p>", unsafe_allow_html=True)
        
        verified, team_data, model_data = structure_extractor.extract(attribute_display=False)
        structure_metrics = structure_dashboard.generate_metrics(verified, team_data)
        display_st_metric_values(container=cols[2], metrics=structure_metrics, use_columns=False, include_header=False)
    
    # Residential column (index 4)
    with cols[4]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Residential KPIs</strong></p>", unsafe_allow_html=True)
        
        verified, team_data, model_data = residential_extractor.extract(attribute_display=False)
        residential_metrics = residential_dashboard.generate_metrics(verified, team_data)
        display_st_metric_values(container=cols[4], metrics=residential_metrics, use_columns=False, include_header=False)
    
    # Industrial column (index 6)
    with cols[6]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Industrial KPIs</strong></p>", unsafe_allow_html=True)
        
        verified, team_data, model_data = industrial_extractor.extract(attribute_display=False)
        industrial_metrics = industrial_dashboard.generate_metrics(verified, team_data)
        display_st_metric_values(container=cols[6], metrics=industrial_metrics, use_columns=False, include_header=False)

    # Facade column (index 8)
    with cols[8]:
        # Caption
        st.markdown("<p style='text-align: center;'><strong>Facade KPIs</strong></p>", unsafe_allow_html=True)
        
        verified, team_data, model_data = facade_extractor.extract(attribute_display=False)
        facade_metrics = facade_dashboard.generate_metrics(verified, team_data)
        display_st_metric_values(container=cols[8], metrics=facade_metrics, use_columns=False, include_header=False)

    # After displaying the KPIs, add the performance analysis
    st.markdown("---")  # Add a separator
    
    # Get metrics from extractors
    verified, team_data, model_data = service_extractor.extract(attribute_display=False)
    service_metrics = service_dashboard.generate_metrics(verified, team_data)
    
    verified, team_data, model_data = structure_extractor.extract(attribute_display=False)
    structure_metrics = structure_dashboard.generate_metrics(verified, team_data)
    
    verified, team_data, model_data = residential_extractor.extract(attribute_display=False)
    residential_metrics = residential_dashboard.generate_metrics(verified, team_data)
    
    verified, team_data, model_data = industrial_extractor.extract(attribute_display=False)
    industrial_metrics = industrial_dashboard.generate_metrics(verified, team_data)
    
    verified, team_data, model_data = facade_extractor.extract(attribute_display=False)
    facade_metrics = facade_dashboard.generate_metrics(verified, team_data)

    # Analyze and display team performance
    analyze_team_performance(
        service_metrics,
        structure_metrics,
        residential_metrics,
        industrial_metrics,
        facade_metrics
    )




