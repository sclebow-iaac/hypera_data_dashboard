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
            # Calculate how close the actual value is to the ideal value
            # Score is percentage of ideal value achieved (capped at 100%)
            if metric.ideal_value != 0:  # Avoid division by zero
                score = min((metric.value / metric.ideal_value) * 100, 100)
            else:
                score = 0
            
            team_data['kpi_scores'].append({
                'name': metric.title,
                'actual': metric.value,
                'ideal': metric.ideal_value,
                'score': score
            })
        
        # Calculate average score for the team
        team_data['total_score'] = sum(kpi['score'] for kpi in team_data['kpi_scores']) / len(team_data['kpi_scores'])

    # Prepare data for bar chart
    import plotly.graph_objects as go
    import pandas as pd

    # Create DataFrame for the bar chart
    performance_df = pd.DataFrame([
        {'Team': team_name, 'Score': data['total_score']}
        for team_name, data in team_performance.items()
    ])

    # Find the best performing team
    best_team = performance_df.loc[performance_df['Score'].idxmax()]
    
    # Create bar colors (highlight the best team)
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99FF']
    bar_colors = []
    for team in performance_df['Team']:
        if team == best_team['Team']:
            bar_colors.append('#00FF00')  # Bright green for best team
        else:
            bar_colors.append('#808080')  # Gray for other teams

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=performance_df['Team'],
            y=performance_df['Score'],
            marker_color=bar_colors,
            text=performance_df['Score'].round(1).astype(str) + '%',  # Add percentage labels
            textposition='auto',
        )
    ])

    # Update layout
    fig.update_layout(
        title={
            'text': f"Team Performance Comparison (Best: {best_team['Team']} - {best_team['Score']:.1f}%)",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Teams",
        yaxis_title="Achievement Score (%)",
        yaxis_range=[0, 100],  # Set y-axis from 0 to 100%
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )

    # Display the bar chart
    st.plotly_chart(fig, use_container_width=True)

    # Display detailed performance table
    st.subheader("Detailed Performance Analysis")
    
    # Create a DataFrame for the performance table
    performance_data = []
    for team_name, team_data in team_performance.items():
        for kpi in team_data['kpi_scores']:
            performance_data.append({
                'Team': team_name,
                'KPI': kpi['name'],
                'Actual Value': f"{kpi['actual']:.2f}",
                'Ideal Value': f"{kpi['ideal']:.2f}",
                'Achievement %': f"{kpi['score']:.1f}%"
            })
    
    df = pd.DataFrame(performance_data)
    st.dataframe(df, use_container_width=True)

    # Display overall team rankings
    st.subheader("Overall Team Rankings")
    rankings = sorted(
        [(team_name, data['total_score']) for team_name, data in team_performance.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Create columns for rankings
    cols = st.columns(len(rankings))
    for i, ((team_name, score), col) in enumerate(zip(rankings, cols)):
        with col:
            st.metric(
                label=f"{i+1}. {team_name}",
                value=f"{score:.1f}%",
                delta="Best Team" if team_name == best_team['Team'] else None
            )

def run():
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




