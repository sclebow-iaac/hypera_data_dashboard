import streamlit as st
import pandas as pd
import plotly.express as px

def show(container, client, project, models, versions, verbose=False):
    with container:
        st.subheader("Statistics")

        # Columns for Cards
        modelCol, versionCol, connectorCol, contributorCol = st.columns(4)

        #DEFINITIONS
        #create a definition to convert your list to markdown
        def listToMarkdown(list, column):
            list = ["- " + i +  "\n" for i in list]
            list = "".join(list)
            return column.markdown(list)

        #Model Card 💳
        modelCol.metric(label = "Number of Models in Project", value= len(models))
        #branch names as markdown list
        modelNames = [m.name for m in models]
        # listToMarkdown(modelNames, modelCol)

        #Version Card 💳
        versionCol.metric(label = "Number of Versions in Selected Model", value= len(versions))

        def get_all_versions_in_project(project):
            all_versions = []
            for model in project.models.items:
                versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
                all_versions.extend(versions)
            return all_versions

        #Connector Card 💳
        #connector list
        all_versions_in_project = get_all_versions_in_project(project)
        connectorList = [v.sourceApplication for v in all_versions_in_project]
        #number of connectors
        connectorCol.metric(label="Number of Connectors in Project", value= len(dict.fromkeys(connectorList)))
        #get connector names
        connectorNames = list(dict.fromkeys(connectorList))
        #convert it to markdown list
        listToMarkdown(connectorNames, connectorCol)

        def get_all_coillaborators_in_project(project):
            all_collaborators = []
            for model in project.models.items:
                versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
                for version in versions:
                    all_collaborators.append(version.authorUser)
            return all_collaborators

        #Contributor Card 💳
        all_collaborators = get_all_coillaborators_in_project(project)
        #unique contributor names
        contributorNames = list(dict.fromkeys([col.name for col in all_collaborators]))
        contributorCol.metric(label = "Number of Contributors to Project", value= len(contributorNames))
        #convert it to markdown list
        listToMarkdown(contributorNames,contributorCol)

        #COLUMNS FOR CHARTS
        connector_graph_col, collaborator_graph_col = st.columns([1,1])

        #model GRAPH 📊
        #model count dataframe
        model_names = []
        version_counts = []
        for model in models:
            model_names.append(model.name)
            version_count = len(client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items)
            # print(f'Model: {model.name} - Version count: {version_count}\n')
            version_counts.append(version_count)

        model_counts = pd.DataFrame([[model_name, version_count] for model_name, version_count in zip(model_names, version_counts)])

        # #rename dataframe columns
        # model_counts.columns = ["modelName", "totalCommits"]
        # #create graph
        # model_count_graph = px.bar(model_counts, x=model_counts.modelName, y=model_counts.totalCommits, color=model_counts.modelName, labels={"modelName":"","totalCommits":""})
        # #update layout
        # model_count_graph.update_layout(
        #     showlegend = False,
        #     margin = dict(l=1,r=1,t=1,b=1),
        #     height=220,
        #     paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        #     plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
        #     font_family="Arial",
        #     font_color="black"
        # )
        # #show graph
        # model_graph_col.plotly_chart(model_count_graph, use_container_width=True)

        # Create a new row for the pie charts
        pie_col1, pie_col2 = st.columns(2)

        # CONNECTOR CHART 🍩
        with pie_col1:
            st.subheader("Connector Chart")
            version_frame = pd.DataFrame.from_dict([c.dict() for c in all_versions_in_project])
            #get apps from commits
            apps = version_frame["sourceApplication"]
            #reset index
            apps = apps.value_counts().reset_index()
            #rename columns
            apps.columns=["app","count"]
            #donut chart
            fig = px.pie(apps, names=apps["app"],values=apps["count"], hole=0.5)
            #set dimensions of the chart
            fig.update_layout(
                showlegend=False,
                margin=dict(l=1, r=1, t=1, b=1),
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Roboto Mono",
                font_color="#2c3e50"
            )
            #set width of the chart so it uses column width
            connector_graph_col.plotly_chart(fig, use_container_width=True)

        # COLLABORATOR CHART 🍩
        with pie_col2:
            st.subheader("Collaborator Chart")
            #get authors from commits
            version_user_names = []
            for user in version_frame["authorUser"]:
                # # print(f'type: {type(user)}')
                # # print(f'user: {user.get('name')}\n')
                version_user_names.append(user.get('name'))

            authors = pd.DataFrame(version_user_names).value_counts().reset_index()
            #rename columns
            authors.columns=["author","count"]
            #create our chart
            authorFig = px.pie(authors, names=authors["author"], values=authors["count"],hole=0.5)
            authorFig.update_layout(
                showlegend=False,
                margin=dict(l=1,r=1,t=1,b=1),
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',  # Add transparent background
                plot_bgcolor='rgba(0,0,0,0)',   # Add transparent plot background
                font_family="Roboto Mono",
                font_color="#2c3e50",
                yaxis_scaleanchor="x",
            )
            collaborator_graph_col.plotly_chart(authorFig, use_container_width=True)

        st.markdown("---")

        #COMMIT PANDAS TABLE 🔲
        st.subheader("Commit Activity Timeline 🕒")
        #created at parameter to dataframe with counts
        # # print("VALUE")
        # # print(pd.to_datetime(commits["createdAt"]).dt.date.value_counts().reset_index())

        timestamps = [version.createdAt.date() for version in all_versions_in_project]
        # print(f'timestamps: {timestamps}\n')

        #convert to pandas dataframe and
        # rename the column of the timestamps frame to createdAt
        timestamps_frame = pd.DataFrame(timestamps, columns=["createdAt"]).value_counts().reset_index().sort_values("createdAt")

        # print(f'timestamps_frame: {timestamps_frame}\n')

        cdate = timestamps_frame
        #rename columns
        cdate.columns = ["date", "count"]
        #redate indexed dates
        cdate["date"] = pd.to_datetime(cdate["date"]).dt.date

        # print(f'cdate: {cdate}\n')

        #COMMIT ACTIVITY LINE CHART📈
        #line chart
        fig = px.line(cdate, x=cdate["date"], y=cdate["count"], markers =True)
        #recolor line
        fig.update_layout(
            showlegend=False,
            margin=dict(l=1,r=1,t=1,b=1),
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',  # Add transparent background
            plot_bgcolor='rgba(0,0,0,0)',   # Add transparent plot background
            font_family="Roboto Mono",
            font_color="#2c3e50"
        )
        fig.update_traces(line_color="red")

        #Show Chart
        st.plotly_chart(fig, use_container_width=True)

        #--------------------------
