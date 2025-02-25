import streamlit as st

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

# import dashboards from local files
import data_extraction.facade_extractor as facade_extractor
import data_extraction.residential_extractor as residential_extractor
import data_extraction.service_extractor as service_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor

def run(selected_team: str = "") -> None:
    speckleServer = "macad.speckle.xyz"
    speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckleServer)
    account = get_account_from_token(speckleToken, speckleServer)
    client.authenticate_with_account(account)
    
    project_id = '31f8cca4e0'
    selected_project = client.project.get(project_id=project_id)
    project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
    models = project.models.items
    
    st.title("Data Dashboard")
    st.markdown("This dashboard is used to aggregate data from the metric models in the project")
    st.markdown("------")
    
    st.markdown('Visibility toggles')
    # Add columns for the visibility toggles
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        header = st.checkbox("Header", value=True)
    with col2:
        table = st.checkbox("Table", value=False)
    with col3:
        gauge = st.checkbox("Gauge", value=True)
    with col4:
        attribute_display = st.checkbox("Attribute Display", value=False)

    st.markdown("## Facade Team")
    facade_extractor.extract(models=models, client=client, project_id=project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)
    st.markdown("------")
    st.markdown("------")

    st.markdown("## Residential Team")
    residential_extractor.extract(models=models, client=client, project_id=project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)
    st.markdown("------")
    st.markdown("------")

    st.markdown("## Service Team")
    service_extractor.extract(models=models, client=client, project_id=project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)
    st.markdown("------")
    st.markdown("------")

    st.markdown("## Structure Team")
    structure_extractor.extract(models=models, client=client, project_id=project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)
    st.markdown("------")
    st.markdown("------")

    st.markdown("## Industrial Team")
    industrial_extractor.extract(models=models, client=client, project_id=project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)

    return None