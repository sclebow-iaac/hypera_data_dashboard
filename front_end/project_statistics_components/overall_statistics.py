import streamlit as st
import pandas as pd
import plotly.express as px

def create_activity_timeline(timeline_data):
    """Create and display the activity timeline chart."""
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
        labels={'date': 'Date', 'count': 'Number of Versions', 'team_name': 'Team'}
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
        margin=dict(l=1, r=1, t=10, b=1),
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
    
    # Add hover information
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Team: %{customdata}<br>Versions: %{y}<extra></extra>'
    )
    
    # Add team name as custom data for hover info
    fig.update_traces(customdata=timeline_grouped['team_name'])
    
    # Show Chart
    st.plotly_chart(fig, use_container_width=True)

def display_overall_metrics(project_tree):
    """Display the overall project metrics."""
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
    """Create and display a pie chart of project contributors."""
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
    """Create and display a pie chart of source applications."""
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

def create_team_charts(project_tree, pie_height=300):
    """Create and display pie charts for team versions and models."""
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
        fig = px.pie(all_versions_by_team, names='Percentage Team', values='Count', hole=0.5)
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
        fig = px.pie(all_models_by_team, names='Percentage Team', values='Count', hole=0.5)
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
    """Find and display the most active team."""
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
    """Analyze and display team balance metrics."""
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
    """Display information about the most balanced team."""
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
    """Display the balance scores for all teams."""
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
    """Main function to display overall project statistics."""
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
    
    pie_height = 300
    contributer_col, source_application_col = st.columns([1, 1])
    
    with contributer_col:
        create_contributor_chart(project_tree, pie_height)
        
    with source_application_col:
        create_source_app_chart(project_tree, pie_height)
    
    all_versions_by_team, all_models_by_team = create_team_charts(project_tree, pie_height)
    team_data = find_most_active_team(all_versions_by_team, all_models_by_team)
    
    if detail_level == 'all':
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

