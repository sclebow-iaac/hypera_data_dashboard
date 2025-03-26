import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
from streamlit_plotly_events import plotly_events

import attribute_extraction
from dashboards.dashboard import *

from project_statistics_components.network import create_network_graph

default_speckle_viewer_height = 600

def run(project_tree, project_id):
    st.write('This tab allows you to explore the project tree and select models for analysis.')

    # Create the network diagram
    selected_model_name, selected_node_children = create_network_graph(project_tree)

    # Sort the children by their long name
    selected_node_children.sort()

    # print()
    # # Debug print
    # print(f"Selected Model Name: {selected_model_name}")
    # print(f"Selected Node Children: {selected_node_children}")

    if selected_model_name is None:
        st.write("No model selected.")
    else:
        if len(selected_node_children) == 0:
            st.write("No child models available for this node.")
            single_tab = st.container()
            combined_tab = None
        else:
            st.write(f'The selected node has {len(selected_node_children)} child model(s)')
            combined_tab, single_tab = st.tabs([
                "Analyze all Child Models Combined", 
                "Analyze a Single Child Model"
            ])


        with single_tab:
            if len(selected_node_children) != 0:
                # Create a dropdown to select a model from the children
                selected_child_name = st.selectbox(f'**Select a child model to analyze, there is/are {len(selected_node_children)}**', selected_node_children)
                selected_model_name = selected_child_name

            # Get the model ID from the selected model name
            # Check the long name of the model
            selected_model_id = None
            version_data = None
            for key, value in project_tree.items():
                if value["long_name"] == selected_model_name:
                    selected_model_id = value["id"]
                    version_data = value["version_data"]
                    print(f'version_data: {version_data}')
                    break

            selected_version_id = st.selectbox(f"Select a version, there is/are {len(version_data)}", list(version_data.keys()), format_func=lambda x: version_data[x]["createdAt"])
            
            
            attribute_extraction.run_from_version_id(version_id=selected_version_id, model_id=selected_model_id)

            # Create two columns for the speckle viewer and the version data
            viewer_col, version_data_col = st.columns([1, 1])
            with viewer_col:
                # Create a Speckle Viewer
                st.subheader("Speckle Viewer")
                speckle_model_id = selected_model_id + '@' + selected_version_id
                display_speckle_viewer(container=viewer_col, project_id=project_id, model_id=speckle_model_id, header_text='Selected Model', height=default_speckle_viewer_height)

            with version_data_col:
                # Display the version data
                st.subheader("Version Data")

                creator = version_data[selected_version_id]["authorUser"]
                created_at = version_data[selected_version_id]["createdAt"]
                source_application = version_data[selected_version_id]["sourceApplication"]
                st.markdown(f"**Created By:** {creator.name}")
                st.markdown(f"**Created At:** {created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                st.markdown(f"**Source Application:** {source_application}")

            st.header("Selected Model Data:")
            # Create a dataframe from the version data
            version_data_df = pd.DataFrame.from_dict(version_data, orient='index')
            # Convert the createdAt column to datetime
            version_data_df['createdAt'] = pd.to_datetime(version_data_df['createdAt'])
            # Sort the dataframe by createdAt
            version_data_df = version_data_df.sort_values(by='createdAt')

            # Add timeline for single model versions
            st.subheader(f'Timeline for {len(version_data)} version(s)')
            
            # Prepare data for timeline
            timeline_df = version_data_df.copy()
            timeline_df['author_name'] = timeline_df['authorUser'].apply(lambda x: x.name)
            
            # Calculate appropriate height based on number of versions
            height = max(30 * len(version_data), 200)
            
            # Create a timeline showing version commits
            fig = px.scatter(timeline_df, 
                            x='createdAt', 
                            y=[selected_model_name.split('/')[-1]] * len(timeline_df),
                            color='sourceApplication',
                            hover_data=['sourceApplication', 'author_name'],
                            labels={'createdAt': 'Date', 'y': 'Model', 'author_name': 'Author'},
                            height=height)
            
            # Add connecting lines to visualize sequence
            fig.add_trace(go.Scatter(
                x=timeline_df['createdAt'],
                y=[selected_model_name.split('/')[-1]] * len(timeline_df),
                mode='lines',
                line=dict(width=1.5, dash='dot'),
                showlegend=False,
                opacity=0.7,
                hoverinfo='skip'
            ))
            
            # Improve visualization
            fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='black')))
            fig.update_layout(
                xaxis_title="Version Creation Date",
                yaxis_title="Model",
                legend_title="Source Applications",
                font_family="Roboto Mono",
                font_color="#2c3e50",
                plot_bgcolor='rgba(240,240,240,0.2)',
                hovermode='closest',
                showlegend=False,
            )
            
            # Show the chart
            st.plotly_chart(fig, use_container_width=True)

            # Create a pie chart of the contributors in a column
            # Create a pie chart of the Source Applications in a column
            contributor_col, source_application_col = st.columns([1, 1])
            with contributor_col:
                st.subheader("Model Contributors")
                # Get the contributors from the version data
                contributors = version_data_df['authorUser'].apply(lambda x: x.name).value_counts().reset_index()
                contributors.columns = ['Contributor', 'Count']
                # Create a pie chart of the contributors
                fig = px.pie(contributors, names='Contributor', values='Count', hole=0.5)
                fig.update_layout(
                    showlegend=True,
                    margin=dict(l=1, r=1, t=1, b=1),
                    height=200,
                    font_family="Roboto Mono",
                    font_color="#2c3e50"
                )
                fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                # Show the chart
                contributor_col.plotly_chart(fig, use_container_width=True)
            with source_application_col:
                st.subheader("Model Source Applications")
                # Get the source applications from the version data
                source_applications = version_data_df['sourceApplication'].value_counts().reset_index()
                source_applications.columns = ['Source Application', 'Count']
                # Create a pie chart of the source applications
                fig = px.pie(source_applications, names='Source Application', values='Count', hole=0.5)
                fig.update_layout(
                    showlegend=True,
                    margin=dict(l=1, r=1, t=1, b=1),
                    height=200,
                    font_family="Roboto Mono",
                    font_color="#2c3e50"
                )
                fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                # Show the chart
                source_application_col.plotly_chart(fig, use_container_width=True)

            # Add information about version frequency
            st.markdown("### Version Frequency Analysis")
            versions_per_day = version_data_df.set_index('createdAt').groupby(pd.Grouper(freq='D')).size()
            versions_per_day = versions_per_day[versions_per_day > 0]  # Only days with versions

            active_days = len(versions_per_day)
            total_days = (version_data_df['createdAt'].max() - version_data_df['createdAt'].min()).days + 1
            avg_versions_per_active_day = versions_per_day.mean()

            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            metrics_col1.metric("Active Days", f"{active_days}/{total_days} days")
            metrics_col2.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
            if not versions_per_day.empty:
                metrics_col3.metric("Most Active Day", f"{versions_per_day.idxmax().strftime('%Y-%m-%d')} ({versions_per_day.max()} versions)")
            else:
                metrics_col3.metric("Most Active Day", "No data")

        if combined_tab is not None:
            with combined_tab:
                viewer_col, version_data_col = st.columns([1, 1])
                # Combine all child model ids for the speckle viewer
                child_model_ids = []
                latest_version_data_per_model = {}
                all_version_data_per_model = {}
                for child in selected_node_children:
                    # Get the model ID from the selected model name
                    # Check the long name of the model
                    for key, value in project_tree.items():
                        if value["long_name"] == child:
                            child_model_ids.append(value["id"])
                            # Get the latest version data
                            latest_version_data = None
                            soonest_date = None
                            for version_id, version_info in value["version_data"].items():
                                if latest_version_data is None or version_info["createdAt"] < soonest_date:
                                    latest_version_data = version_info
                                    soonest_date = version_info["createdAt"]
                            latest_version_data_per_model[child] = latest_version_data
                            all_version_data_per_model[child] = value["version_data"]
                            break

                combined_model_id = ','.join(child_model_ids)

                with viewer_col:
                    # Create a Speckle Viewer
                    st.subheader("Speckle Viewer")
                    speckle_model_id = combined_model_id
                    height = min(max(50 * len(child_model_ids), default_speckle_viewer_height), 1000)
                    display_speckle_viewer(
                                            container=viewer_col, 
                                            project_id=project_id, 
                                            model_id=speckle_model_id, 
                                            is_transparent=False,
                                            hide_controls=False,
                                            hide_selection_info=False,
                                            no_scroll=False,
                                            height=height,
                                            header_text='Combined Model',
                                        )


                with version_data_col:
                    # Display the version data
                    st.subheader("Latest Version Data")

                    for child, version_info in latest_version_data_per_model.items():
                        with st.expander(f"**Latest Version for {child}:**"):
                            st.markdown(f"**Created By:** {version_info['authorUser'].name}")
                            st.markdown(f"**Created At:** {version_info['createdAt'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
                            st.markdown(f"**Source Application:** {version_info['sourceApplication']}")

                st.header("Combined Model Data:")
                
                # Create a timeline of all version data with a different color for each model
                total_version_count = sum(len(value) for value in all_version_data_per_model.values())
                st.subheader(f'Timeline for {total_version_count} version(s) across {len(all_version_data_per_model)} models')

                # Create a dataframe to store all version data
                all_versions_df = pd.DataFrame()

                # Process each model's versions and add them to the dataframe
                for child_model, version_data in all_version_data_per_model.items():
                    # Create a dataframe for this model's versions
                    model_df = pd.DataFrame.from_dict(version_data, orient='index')
                    # Add model name column
                    model_df['model_name'] = child_model
                    # Convert timestamps to datetime
                    model_df['createdAt'] = pd.to_datetime(model_df['createdAt'])
                    # Extract author name from authorUser object
                    model_df['author_name'] = model_df['authorUser'].apply(lambda x: x.name)
                    # Add to the combined dataframe
                    all_versions_df = pd.concat([all_versions_df, model_df])

                # Sort by creation date
                all_versions_df = all_versions_df.sort_values(by='createdAt')

                height = min(800, max(150 + 7 * total_version_count, 200))

                # Create a timeline showing version commits by model
                fig = px.scatter(all_versions_df, 
                                x='createdAt', 
                                y='model_name',
                                color='model_name',
                                hover_data=['sourceApplication', 'author_name'],  # Use author_name instead of authorUser
                                labels={'createdAt': 'Date', 'model_name': 'Model Name', 'author_name': 'Author'},
                                height=height)

                # Improve the visualization
                fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='black')))
                fig.update_layout(
                    xaxis_title="Version Creation Date",
                    yaxis_title="Model",
                    legend_title="Models",
                    font_family="Roboto Mono",
                    font_color="#2c3e50",
                    plot_bgcolor='rgba(240,240,240,0.2)',
                    hovermode='closest',
                    showlegend=False,
                )

                # Add connecting lines for each model to better visualize the sequence
                for model_name in all_versions_df['model_name'].unique():
                    model_data = all_versions_df[all_versions_df['model_name'] == model_name].sort_values('createdAt')
                    
                    fig.add_trace(go.Scatter(
                        x=model_data['createdAt'],
                        y=[model_name] * len(model_data),
                        mode='lines',
                        line=dict(width=1.5, dash='dot'),
                        showlegend=False,
                        opacity=0.7,
                        hoverinfo='skip'
                    ))

                # Show the chart
                st.plotly_chart(fig, use_container_width=True)

                # Create a pie chart of the contributors in a column
                # Create a pie chart of the Source Applications in a column
                contributor_col, source_application_col = st.columns([1, 1])
                with contributor_col:
                    st.subheader("Model Contributors")
                    # Get the contributors from the version data
                    contributors = all_versions_df['authorUser'].apply(lambda x: x.name).value_counts().reset_index()
                    contributors.columns = ['Contributor', 'Count']
                    # Create a pie chart of the contributors
                    fig = px.pie(contributors, names='Contributor', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=200,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    contributor_col.plotly_chart(fig, use_container_width=True)
                with source_application_col:
                    st.subheader("Model Source Applications")
                    # Get the source applications from the version data
                    source_applications = all_versions_df['sourceApplication'].value_counts().reset_index()
                    source_applications.columns = ['Source Application', 'Count']
                    # Create a pie chart of the source applications
                    fig = px.pie(source_applications, names='Source Application', values='Count', hole=0.5)
                    fig.update_layout(
                        showlegend=True,
                        margin=dict(l=1, r=1, t=1, b=1),
                        height=200,
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    # Show the chart
                    source_application_col.plotly_chart(fig, use_container_width=True)

                # Add information about version frequency
                st.markdown("### Version Frequency Analysis")
                versions_per_day = all_versions_df.set_index('createdAt').groupby(pd.Grouper(freq='D')).size()
                versions_per_day = versions_per_day[versions_per_day > 0]  # Only days with versions

                active_days = len(versions_per_day)
                total_days = (all_versions_df['createdAt'].max() - all_versions_df['createdAt'].min()).days + 1
                avg_versions_per_active_day = versions_per_day.mean()

                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                metrics_col1.metric("Active Days", f"{active_days}/{total_days} days")
                metrics_col2.metric("Average Versions per Active Day", f"{avg_versions_per_active_day:.2f}")
                metrics_col3.metric("Most Active Day", f"{versions_per_day.idxmax().strftime('%Y-%m-%d')} ({versions_per_day.max()} versions)")

