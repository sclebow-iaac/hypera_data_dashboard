import streamlit as st
import pandas as pd
import plotly.express as px

team_colors = {
    "Facade": "#982062",
    "Services": "#343779",
    "Industrial": "#ffa646",
    "Residential": "#33a9ac",
    "Structure": "#f86041"
}

def create_activity_timeline(timeline_data):
    # Create and display the activity timeline chart.
    st.subheader("Activity Timeline")
    
    # Convert timeline_data to pandas DataFrame
    timeline_df = pd.DataFrame(timeline_data)
    
    # Convert the createdAt column to datetime
    timeline_df['createdAt'] = pd.to_datetime(timeline_df['createdAt'])
    
    # Group by date and team, count occurrences
    timeline_df['date'] = timeline_df['createdAt'].dt.date
    timeline_grouped = timeline_df.groupby(['date', 'team_name']).size().reset_index(name='count')
    
    # Create line chart with a line for each team
    fig = px.line(
        timeline_grouped, 
        x='date', 
        y='count', 
        color='team_name',
        markers=True,
        labels={'date': 'Date', 'count': 'Number of Versions', 'team_name': 'Team'},
        color_discrete_map=team_colors  # Add this line to use team colors
    )
    
    # Improve styling
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8
        ),
        legend_title='Teams',
        margin=dict(l=1, r=40, t=10, b=1),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50",
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto Mono",
            font_color="#2c3e50",
        ),
    )
    
    # Add team name as custom data for hover info
    fig.update_traces(customdata=timeline_grouped['team_name'])
    
    # Show Chart
    st.plotly_chart(fig, use_container_width=True)

def create_activity_by_weekday_chart(project_tree):
    # Create and display the activity by weekday chart.
    st.subheader("Activity by Weekday")
    # Get the activity data
    all_versions_df = pd.DataFrame()
    for model in project_tree.values():
        for version in model["version_data"].values():
            all_versions_df = pd.concat([all_versions_df, pd.DataFrame([{
                "createdAt": version["createdAt"],
                "authorUser": version["authorUser"],
                "sourceApplication": version["sourceApplication"],
                "team_name": model["team_name"],
            }])], ignore_index=True)

    all_versions_df['createdAt'] = pd.to_datetime(all_versions_df['createdAt'])
    all_versions_df['date'] = all_versions_df['createdAt'].dt.date
    all_versions_df['weekday'] = all_versions_df['createdAt'].dt.day_name()
    all_versions_df['count'] = 1
    all_versions_df['weekday'] = pd.Categorical(all_versions_df['weekday'],
                                                 categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                                                 ordered=True)
    all_versions_df['weekday'] = all_versions_df['weekday'].astype(str)
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Monday', 'Mon')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Tuesday', 'Tue')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Wednesday', 'Wed')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Thursday', 'Thu')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Friday', 'Fri')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Saturday', 'Sat')
    all_versions_df['weekday'] = all_versions_df['weekday'].str.replace('Sunday', 'Sun')

    # Get the maximum y-axis range
    # Remember that the bars will be stacked, so we need to find the maximum count for any weekday
    y_range_max = all_versions_df.groupby('weekday')['count'].sum().max()

    # Group by weekday and team, count occurrences
    activity_by_weekday = all_versions_df.groupby(['weekday', 'team_name']).size().reset_index(name='count')

    # Sort the activity_by_weekday DataFrame by weekday
    activity_by_weekday['weekday'] = pd.Categorical(activity_by_weekday['weekday'],
                                                     categories=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                                                     ordered=True)
    activity_by_weekday = activity_by_weekday.sort_values('weekday')

    # Create bar chart with a bar for each team
    fig = px.bar(
        activity_by_weekday,
        x='weekday',
        y='count',
        range_y=[0, y_range_max * 1.1],  # Add some space above the highest bar
        color='team_name',
        labels={'weekday': 'Weekday', 'count': 'Number of Versions', 'team_name': 'Team'},
        color_discrete_map=team_colors,  # Add this line to use team colors
        text='count'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8
        ),
        legend_title='Teams',
        margin=dict(l=1, r=30, t=1, b=1),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto Mono",
            font_color="#2c3e50",
        ),
    )
    # Add team name as custom data for hover info
    fig.update_traces(customdata=activity_by_weekday['team_name'])
    # Show Chart
    st.plotly_chart(fig, use_container_width=True)

def create_activity_by_time_of_day_chart(project_tree):
    # Create and display the activity by hour of day chart.
    st.subheader("Activity by Hour of Day")
    # Get the activity data
    all_versions_df = pd.DataFrame()
    for model in project_tree.values():
        for version in model["version_data"].values():
            all_versions_df = pd.concat([all_versions_df, pd.DataFrame([{
                "createdAt": version["createdAt"],
                "authorUser": version["authorUser"],
                "sourceApplication": version["sourceApplication"],
                "team_name": model["team_name"],
            }])], ignore_index=True)
    all_versions_df['createdAt'] = pd.to_datetime(all_versions_df['createdAt'])
    all_versions_df['hour'] = all_versions_df['createdAt'].dt.hour
    all_versions_df['count'] = 1
    all_versions_df['hour'] = all_versions_df['hour'].astype(str)
    all_versions_df['hour'] = all_versions_df['hour'].str.zfill(2)  # Add leading zero for single digit hours

    hour_conversion = {
        '00': '12 AM', '01': '1 AM', '02': '2 AM', '03': '3 AM', '04': '4 AM',
        '05': '5 AM', '06': '6 AM', '07': '7 AM', '08': '8 AM', '09': '9 AM',
        '10': '10 AM', '11': '11 AM', '12': '12 PM', '13': '1 PM', '14': '2 PM',
        '15': '3 PM', '16': '4 PM', '17': '5 PM', '18': '6 PM', '19': '7 PM',
        '20': '8 PM', '21': '9 PM', '22': '10 PM', '23': '11 PM'
    }
    all_versions_df['hour'] = all_versions_df['hour'].map(hour_conversion)
    all_versions_df['hour'] = pd.Categorical(all_versions_df['hour'],
                                                 categories=list(hour_conversion.values()),
                                                 ordered=True)
    # Group by hour and team, count occurrences
    activity_by_hour = all_versions_df.groupby(['hour', 'team_name']).size().reset_index(name='count')
    # Sort the activity_by_hour DataFrame by hour
    activity_by_hour['hour'] = pd.Categorical(activity_by_hour['hour'],
                                                 categories=list(hour_conversion.values()),
                                                 ordered=True)
    activity_by_hour = activity_by_hour.sort_values('hour')
    # Get the maximum y-axis range
    # Remember that the bars will be stacked, so we need to find the maximum count for any hour
    y_range_max = activity_by_hour.groupby('hour')['count'].sum().max()
    # Create bar chart with a bar for each team
    # Filter out zero counts
    activity_by_hour = activity_by_hour[activity_by_hour['count'] > 0]
    
    fig = px.bar(
        activity_by_hour,
        x='hour',
        y='count',
        range_y=[0, y_range_max * 1.1],  # Add some space above the highest bar
        color='team_name',
        labels={'hour': 'Hour of Day (UTC)', 'count': 'Number of Versions', 'team_name': 'Team'},
        color_discrete_map=team_colors,  # Add this line to use team colors
        text='count'
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8
        ),
        legend_title='Teams',
        margin=dict(l=1, r=30, t=1, b=1),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Roboto Mono",
        font_color="#2c3e50",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Roboto Mono",
            font_color="#2c3e50",
        ),
    )
    # Add team name as custom data for hover info
    fig.update_traces(customdata=activity_by_hour['team_name'])
    # Show Chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add a celebration message for the most active hour
    most_active_hour = activity_by_hour.groupby('hour').size().idxmax()
    most_active_count = activity_by_hour.groupby('hour').size().max()
    st.markdown(f"<div style='text-align: center;'><b>Most Active Hour: {most_active_hour} (UTC)</b> with {most_active_count} contributions!</div>", unsafe_allow_html=True)

def display_overall_metrics(project_tree):
    # Display the overall project metrics.
    st.subheader("Overall Project Statistics")
    # Get the total number of models that have versions
    total_models = sum(1 for model in project_tree.values() if model["version_count"] > 0)
    # Get the total number of versions
    total_versions = sum(model["version_count"] for model in project_tree.values())
    # Get the total number of contributors
    total_contributors = len(set(version["authorUser"].name for model in project_tree.values() for version in model["version_data"].values()))
    # Get the total number of source applications
    total_source_applications = len(set(version["sourceApplication"] for model in project_tree.values() for version in model["version_data"].values()))
    
    # Get the activity metrics
    all_versions_df = pd.DataFrame()
    for model in project_tree.values():
        for version in model["version_data"].values():
            all_versions_df = pd.concat([all_versions_df, pd.DataFrame([{
                "createdAt": version["createdAt"],
                "authorUser": version["authorUser"],
                "sourceApplication": version["sourceApplication"],
            }])], ignore_index=True)
    all_versions_df['createdAt'] = pd.to_datetime(all_versions_df['createdAt'])
    all_versions_df['date'] = all_versions_df['createdAt'].dt.date
    all_versions_df['count'] = 1
    active_days = all_versions_df.groupby('date').size().reset_index(name='count')
    active_days = len(active_days[active_days['count'] > 0])
    total_days = (all_versions_df['createdAt'].max() - all_versions_df['createdAt'].min()).days + 1
    avg_versions_per_active_day = all_versions_df.groupby('date').size().mean()
    
    # Create metrics
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    metrics_col1.metric("Total Models", total_models)
    metrics_col2.metric("Total Versions", total_versions)
    metrics_col3.metric("Total Contributors", total_contributors)
    metrics_col4.metric("Total Source Applications", total_source_applications)
    metrics_col5, metrics_col6, metrics_col7 = st.columns(3)
    metrics_col5.metric("Active Days", f"{active_days}/{total_days} days")
    metrics_col6.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
    if active_days > 0:
        most_active_day = all_versions_df.groupby('date').size().idxmax()
        most_active_count = all_versions_df.groupby('date').size().max()
        metrics_col7.metric("Most Active Day", f"{most_active_day.strftime('%Y-%m-%d')} ({most_active_count} versions)")
    else:
        metrics_col7.metric("Most Active Day", "No data")
    
    return all_versions_df

def create_contributor_chart(project_tree, pie_height=300):
    # Create and display a pie chart of project contributors.
    st.subheader("Project Contributors")
    # Get the contributors from the version data
    all_contributors = []
    for model in project_tree.values():
        for version in model["version_data"].values():
            all_contributors.append(version["authorUser"].name)
    all_contributors = pd.Series(all_contributors).value_counts().reset_index()
    all_contributors.columns = ['Contributor', 'Count']

    # Update 'Contributor' column to include the percentage
    all_contributors['Percentage'] = (all_contributors['Count'] / all_contributors['Count'].sum()) * 100
    all_contributors['Percentage Contributor'] = all_contributors['Percentage'].round(2).astype(str) + "% " + all_contributors['Contributor']

    # Create a pie chart of the contributors
    fig = px.pie(all_contributors, names='Percentage Contributor', values='Count', hole=0.5)
    fig.update_layout(
        showlegend=True,
        legend_title="Contributors",
        margin=dict(l=1, r=1, t=1, b=1),
        height=pie_height,
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    # Show the chart
    st.plotly_chart(fig, use_container_width=True)

    # Add a celebration message for the most active contributor
    most_active_contributor = all_contributors.iloc[0]['Contributor']
    most_active_contributor_count = all_contributors.iloc[0]['Count']
    st.markdown(f"**Most Active Contributor: {most_active_contributor}** with {most_active_contributor_count} contributions!")

def create_source_app_chart(project_tree, pie_height=300):
    # Create and display a pie chart of source applications.
    st.subheader("Project Source Applications")
    # Get the source applications from the version data
    all_source_applications = []
    for model in project_tree.values():
        for version in model["version_data"].values():
            all_source_applications.append(version["sourceApplication"])
    all_source_applications = pd.Series(all_source_applications).value_counts().reset_index()
    all_source_applications.columns = ['Source Application', 'Count']

    # Update 'Source Application' column to include the percentage
    all_source_applications['Percentage'] = (all_source_applications['Count'] / all_source_applications['Count'].sum()) * 100
    all_source_applications['Percentage Source Application'] = all_source_applications['Percentage'].round(2).astype(str) + "% " + all_source_applications['Source Application']

    # Create a pie chart of the source applications
    fig = px.pie(all_source_applications, names='Percentage Source Application', values='Count', hole=0.5)
    fig.update_layout(
        showlegend=True,
        legend_title="Source Applications",
        margin=dict(l=1, r=1, t=1, b=1),
        height=pie_height,
        font_family="Roboto Mono",
        font_color="#2c3e50"
    )
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    # Show the chart
    st.plotly_chart(fig, use_container_width=True)

    # Add a celebration message for the most used source application
    most_used_source_application = all_source_applications.iloc[0]['Source Application']
    most_used_source_application_count = all_source_applications.iloc[0]['Count']
    st.markdown(f"**Most Used Source Application: {most_used_source_application}** with {most_used_source_application_count} contributions!")

def create_team_charts(project_tree, pie_height=300, bar_height=600):
    # Create a bar chart of total versions by team.
    st.subheader("Project Versions by Team Bar Chart")
    # Get the teams from the version data
    all_versions_by_team = {}

    for model in project_tree.values():
        for version in model["version_data"].values():
            team_name = model["team_name"]
            if team_name not in all_versions_by_team:
                all_versions_by_team[team_name] = 0
            all_versions_by_team[team_name] += 1
    all_versions_by_team = pd.Series(all_versions_by_team).reset_index()
    all_versions_by_team.columns = ['Team', 'Count']
    # Remove the "Root" team from the list
    all_versions_by_team = all_versions_by_team[all_versions_by_team['Team'] != 'Root']
    # Sort the teams by count
    all_versions_by_team = all_versions_by_team.sort_values('Count', ascending=False)

    # Create a bar chart of the teams
    fig = px.bar(all_versions_by_team, x='Team', y='Count', color='Team', color_discrete_map=team_colors)
    fig.update_layout(
        showlegend=True,
        legend_title="Teams",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,  # Center the legend
        ),
        yaxis_title="Version Count",
        margin=dict(l=1, r=40, t=1, b=1),
        height=bar_height * 0.5,
        font_family="Roboto Mono",
        font_color="#2c3e50",
    )
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    # Show the chart
    st.plotly_chart(fig, use_container_width=True)

    # Create a bar chart of all the models
    # Color the bars by team
    # Create a separate bar for each model and group by team
    st.subheader("Project Models by Team Bar Chart")
    all_models = []
    for model in project_tree.values():
        all_models.append({
            "model_name": model["long_name"],
            "label_name": '/'.join(model["long_name"].split('/')[2:]),
            "team_name": model["team_name"],
            "version_count": model["version_count"]
        })

    # Convert all_models to DataFrame and calculate total versions per team for sorting teams
    all_models = pd.DataFrame(all_models)
    all_models = all_models[all_models['version_count'] > 0]  # Filter out models with no versions

    team_versions = all_models.groupby('team_name')['version_count'].sum().reset_index()
    team_versions = team_versions.sort_values('version_count', ascending=False)
    team_order = team_versions['team_name'].tolist()
    
    # Create a category for team_name based on the sorted order
    all_models['team_order'] = all_models['team_name'].apply(lambda x: team_order.index(x) if x in team_order else len(team_order))
    
    # Sort the dataframe: first by team order, then by version count within each team
    all_models = all_models.sort_values(by=['team_order', 'version_count'], ascending=[True, False])
    
    # Make each label_name unique by appending team name if there are duplicates
    label_counts = all_models['label_name'].value_counts()
    duplicate_labels = label_counts[label_counts > 1].index.tolist()

    # For duplicate labels, append team name
    for i, row in all_models.iterrows():
        if row['label_name'] in duplicate_labels:
            all_models.at[i, 'label_name'] = f"{row['label_name']} ({row['team_name']})"

    # Create a bar chart of the models
    fig = px.bar(
        all_models,
        x='label_name',
        y='version_count',
        color='team_name',
        labels={'model_name': 'Model Name', 'version_count': 'Version Count', 'team_name': 'Team'},
        text='version_count',
        category_orders={'team_name': team_order},
        range_y=[0, all_models['version_count'].max() * 1.1],  # Add some space above the highest bar
        color_discrete_map=team_colors  # Add this line to use team colors
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        showlegend=True,
        legend_title="Teams",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",  # Changed from "right" to "center"
            x=0.5,  # Changed from 0.8 to 0.5 to center the legend
        ),
        margin=dict(l=1, r=50, t=1, b=1),
        height=bar_height,
        font_family="Roboto Mono",
        font_color="#2c3e50",
        xaxis=dict(
            title=None,  # Hide x-axis title
            automargin=True
        ),
    )
    # Add this line to make sure y-axis scaling provides enough room for labels
    fig.update_yaxes(rangemode='tozero', automargin=True)
    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    # Show the chart
    st.plotly_chart(fig, use_container_width=True)
    # Create and display pie charts for team versions and models.
    version_col, model_col = st.columns([1, 1])

    with version_col:
        # Create a pie chart of all the versions by team
        st.subheader("Project Versions by Team")
        # Get the teams from the version data
        all_versions_by_team = []
        for model in project_tree.values():
            for version in model["version_data"].values():
                all_versions_by_team.append(model["team_name"])
        all_versions_by_team = pd.Series(all_versions_by_team).value_counts().reset_index()
        all_versions_by_team.columns = ['Team', 'Count']

        # Remove the "Root" team from the list
        all_versions_by_team = all_versions_by_team[all_versions_by_team['Team'] != 'Root']

        # Update 'Team' column to include the percentage
        all_versions_by_team['Percentage'] = (all_versions_by_team['Count'] / all_versions_by_team['Count'].sum()) * 100
        all_versions_by_team['Percentage Team'] = all_versions_by_team['Percentage'].round(2).astype(str) + "% " + all_versions_by_team['Team']

        # Create a pie chart of the teams
        fig = px.pie(all_versions_by_team, names='Percentage Team', values='Count', hole=0.5, 
                     color='Team', color_discrete_map=team_colors)  # Add color parameters
        fig.update_layout(
            showlegend=True,
            legend_title="Teams",
            margin=dict(l=1, r=1, t=1, b=1),
            height=pie_height,
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
        # Show the chart
        st.plotly_chart(fig, use_container_width=True)

    with model_col:
        # Create a pie chart of all the models by team
        st.subheader("Project Models by Team")
        # Get the teams from the version data
        all_models_by_team = []
        for model in project_tree.values():
            all_models_by_team.append(model["team_name"])
        all_models_by_team = pd.Series(all_models_by_team).value_counts().reset_index()
        all_models_by_team.columns = ['Team', 'Count']

        # Remove the "Root" team from the list
        all_models_by_team = all_models_by_team[all_models_by_team['Team'] != 'Root']
        
        # Update 'Team' column to include the percentage
        all_models_by_team['Percentage'] = (all_models_by_team['Count'] / all_models_by_team['Count'].sum()) * 100
        all_models_by_team['Percentage Team'] = all_models_by_team['Percentage'].round(2).astype(str) + "% " + all_models_by_team['Team']

        # Create a pie chart of the teams
        fig = px.pie(all_models_by_team, names='Percentage Team', values='Count', hole=0.5,
                     color='Team', color_discrete_map=team_colors)  # Add color parameters
        fig.update_layout(
            showlegend=True,
            legend_title="Teams",
            margin=dict(l=1, r=1, t=1, b=1),
            height=pie_height,
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
        # Show the chart
        st.plotly_chart(fig, use_container_width=True)
        
    return all_versions_by_team, all_models_by_team

def find_most_active_team(all_versions_by_team, all_models_by_team):
    # Find and display the most active team.
    team_data = {}

    for team in all_versions_by_team['Team']:
        if team not in team_data:
            team_data[team] = {
                'total_count': 0,
                'version_count': 0,
                'model_count': 0
            }

    # Iterate through all_versions_by_team
    for index, row in all_versions_by_team.iterrows():
        team = row['Team']
        count = row['Count']
        team_data[team]['total_count'] += count
        team_data[team]['version_count'] += count
    
    # Iterate through all_models_by_team
    for index, row in all_models_by_team.iterrows():
        team = row['Team']
        count = row['Count']
        team_data[team]['total_count'] += count
        team_data[team]['model_count'] += count

    # Find the most active team
    most_active_team = max(team_data, key=lambda x: team_data[x]['total_count'])
    most_active_team_version_count = team_data[most_active_team]['version_count']
    most_active_team_model_count = team_data[most_active_team]['model_count']
    st.markdown(f"<div style='text-align: center;'><b>Most Active Team: {most_active_team}</b> with {most_active_team_version_count} versions across {most_active_team_model_count} models!</div>", unsafe_allow_html=True)
    
    return team_data

def analyze_team_balance(project_tree):
    # Analyze and display team balance metrics.
    # Calculate the most balanced team
    # The most balanced team is the one with the most equal number of versions for each team member
    balanced_data = {}

    # Manually enter the number of members per team
    team_members = {
        "Facade": 3,
        "Services": 3,
        "Industrial": 3,
        "Residential": 3,
        "Structure": 2
    }
    
    for model in project_tree.values():
        for version in model["version_data"].values():
            team_name = model["team_name"]
            author_name = version["authorUser"].name
            if team_name not in balanced_data:
                balanced_data[team_name] = {}
            if author_name not in balanced_data[team_name]:
                balanced_data[team_name][author_name] = 0
            balanced_data[team_name][author_name] += 1

    # Calculate the average number of versions per team member for each team
    balanced_team_data = {}
    for team, members in balanced_data.items():
        if team in team_members:  # Only process teams with defined member counts
            if len(members) < team_members[team]:
                # Add missing members with 0 versions
                for i in range(team_members[team] - len(members)):
                    members[f"Member {i+1}"] = 0
            total_versions = sum(members.values())
            if total_versions == 0:  # Skip teams with zero versions
                continue

            balanced_team_data[team] = {
                'total_versions': total_versions,
                'members': members,
                'team_members': team_members[team],
                'team_score': 0,
                'goal_percentage_per_member': 0,
                'percentage_per_member': 0
            }

            percentage_per_member = []

            for member, count in members.items():
                percentage = (count / total_versions) * 100
                percentage_per_member.append(percentage)

            # The best team has all of the contributers with the same percentage
            # The most balanced team is the one with the most equal number of versions for each team member
            goal_percentage_per_member = 100 / team_members[team]
            team_score = sum(abs(percentage - goal_percentage_per_member) for percentage in percentage_per_member)

            balanced_team_data[team]['team_score'] = team_score
            balanced_team_data[team]['goal_percentage_per_member'] = goal_percentage_per_member
            balanced_team_data[team]['percentage_per_member'] = percentage_per_member
            balanced_team_data[team]['members'] = members
            balanced_team_data[team]['team_members'] = team_members[team]
    
    return balanced_team_data

def display_most_balanced_team(balanced_team_data, team_members):
    # Display information about the most balanced team.
    st.subheader("Most Balanced Team Members")
    
    if not balanced_team_data:
        st.write("No team balance data available.")
        return
        
    # Find the most balanced team
    most_balanced_team = min(balanced_team_data, key=lambda x: balanced_team_data[x]['team_score'])
    most_balanced_team_percentage_per_member = balanced_team_data[most_balanced_team]['percentage_per_member']
    most_balanced_team_goal_percentage_per_member = balanced_team_data[most_balanced_team]['goal_percentage_per_member']
    most_balanced_team_number_of_members = team_members[most_balanced_team]
    most_balanced_team_score = balanced_team_data[most_balanced_team]['team_score']
    most_balanced_team_members = balanced_team_data[most_balanced_team]['members']
    most_balanced_team_total_versions = balanced_team_data[most_balanced_team]['total_versions']
    
    st.markdown(f"<div style='text-align: center;'><b>Most Balanced Team: {most_balanced_team}</b> with {most_balanced_team_total_versions} versions across {most_balanced_team_number_of_members} members!</div>", unsafe_allow_html=True)
    
    # Show the most balanced team members
    most_balanced_team_members_df = pd.DataFrame.from_dict(most_balanced_team_members, orient='index', columns=['Version Count'])
    most_balanced_team_members_df['Percentage'] = (most_balanced_team_members_df['Version Count'] / most_balanced_team_total_versions) * 100
    most_balanced_team_members_df['Goal Percentage'] = most_balanced_team_goal_percentage_per_member
    most_balanced_team_members_df['Difference'] = most_balanced_team_members_df['Percentage'] - most_balanced_team_members_df['Goal Percentage']

    # Format the columns
    most_balanced_team_members_df['Version Count'] = most_balanced_team_members_df['Version Count'].astype(int)
    most_balanced_team_members_df['Percentage'] = most_balanced_team_members_df['Percentage'].round(2).astype(str) + "%"
    most_balanced_team_members_df['Goal Percentage'] = most_balanced_team_members_df['Goal Percentage'].round(2).astype(str) + "%"
    most_balanced_team_members_df['Difference'] = most_balanced_team_members_df['Difference'].round(2).astype(str) + "%"

    st.dataframe(most_balanced_team_members_df[['Version Count', 'Percentage', 'Goal Percentage', 'Difference']], use_container_width=True)

def display_team_balance_scores(balanced_team_data):
    # Display the balance scores for all teams.
    st.subheader("Team Balance Scores")
    st.write('Team Balance Score is the Sum of Difference from ideal percentage per member. Ideal percentage is 100% / number of members. The lower the score, the more balanced the team.')
    
    if not balanced_team_data:
        st.write("No team balance data available.")
        return
        
    # Create a dataframe for the team balance scores
    team_balance_scores_df = pd.DataFrame.from_dict(balanced_team_data, orient='index')
    team_balance_scores_df['Team'] = team_balance_scores_df.index
    team_balance_scores_df['Team Balance Score'] = team_balance_scores_df['team_score']

    # Sort the dataframe by team balance score, lowest first
    team_balance_scores_df = team_balance_scores_df.sort_values(by='Team Balance Score', ascending=True)
    team_balance_scores_df.reset_index(drop=True, inplace=True)
    team_balance_scores_df['Ranking'] = team_balance_scores_df.index + 1

    st.dataframe(team_balance_scores_df[['Team', 'Ranking', 'Team Balance Score']], use_container_width=True, hide_index=True)

def run(project_tree, project_id, detail_level='all'):
    # Main function to display overall project statistics.
    # Collect timeline data
    timeline_data = []
    for model in project_tree.values():
        for version in model["version_data"].values():
            timeline_data.append({
                "createdAt": version["createdAt"],
                "team_name": model["team_name"],
            })
    
    # Create and display visualizations
    create_activity_timeline(timeline_data)
    all_versions_df = display_overall_metrics(project_tree)

    # Create Activity by Weekday chart
    create_activity_by_weekday_chart(project_tree)

    # Create Activity by Time of Day chart
    create_activity_by_time_of_day_chart(project_tree)
    
    pie_height = 300
    contributer_col, source_application_col = st.columns([1, 1])
    
    with contributer_col:
        create_contributor_chart(project_tree, pie_height)
        
    with source_application_col:
        create_source_app_chart(project_tree, pie_height)
    
    st.markdown('---')
    all_versions_by_team, all_models_by_team = create_team_charts(project_tree, pie_height)
    team_data = find_most_active_team(all_versions_by_team, all_models_by_team)
    
    if detail_level == 'all':
        st.markdown('---')

        # Team members dictionary
        team_members = {
            "Facade": 3,
            "Services": 3, 
            "Industrial": 3,
            "Residential": 3,
            "Structure": 2
        }
        
        balanced_team_data = analyze_team_balance(project_tree)
        display_most_balanced_team(balanced_team_data, team_members)
        display_team_balance_scores(balanced_team_data)
        
