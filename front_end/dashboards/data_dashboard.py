import streamlit as st

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

# import dashboards from local files
import data_extraction.facade_extractor as facade_extractor
import data_extraction.residential_extractor as residential_extractor
import data_extraction.service_extractor as service_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor

from dashboards.dashboard import get_content_container_columns, content_container_width

def run(selected_team: str = "") -> None:
    left_margin, content_container, right_margin = get_content_container_columns()
    with content_container:
        st.title("Data Dashboard")
        st.markdown(
            "This dashboard is used to aggregate data from the metric models in the project")
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
            display_grid = st.checkbox("Display as Grid", value=True)

    if display_grid:
        l_0, facade_container, residential_container, r_0 = st.columns([1, content_container_width / 2, content_container_width / 2, 1], border=False)
        l_1, service_container, structure_container, r_1 = st.columns([1, content_container_width / 2, content_container_width / 2, 1], border=False)
        l_2, industrial_container, r_2 = st.columns([1, content_container_width, 1], border=False)
        for c in [facade_container, residential_container, service_container, structure_container, industrial_container]:
            c.border = True
    else:

        with content_container:

            facade_container = st.container()
            residential_container = st.container()
            service_container = st.container()
            structure_container = st.container()
            industrial_container = st.container()

    extractors = {
        "Facade": facade_extractor,
        "Residential": residential_extractor,
        "Service": service_extractor,
        "Structure": structure_extractor,
        "Industrial": industrial_extractor
    }

    containers = [
        facade_container,
        residential_container,
        service_container,
        structure_container,
        industrial_container
    ]
    for team_name, extractor, container in zip(extractors.keys(), extractors.values(), containers):
        with container:
            st.markdown(f"## {team_name} Team")
            verified, extracted_data, model_data = extractor.extract(attribute_display=False)
            extracted_data_container = st.container()
            extractor.display_data(extracted_data=extracted_data, header=header, show_table=table,
                                    gauge=gauge, simple_table=False, container=extracted_data_container)
            
            if not display_grid:
                st.markdown("------")
                st.markdown("------")
        

    # facade_container.markdown("## Facade Team")
    # facade_extractor.extract(header=header, table=table, gauge=gauge, attribute_display=False)
    # if not display_grid:
    #     facade_container.markdown("------")
    #     facade_container.markdown("------")

    # residential_container.markdown("## Residential Team")
    # residential_extractor.extract(header=header, table=table, gauge=gauge, attribute_display=False)
    # if not display_grid:
    #     residential_container.markdown("------")
    #     residential_container.markdown("------")

    # service_container.markdown("## Service Team")
    # service_extractor.extract(header=header, table=table, gauge=gauge, attribute_display=False)
    # if not display_grid:
    #     service_container.markdown("------")
    #     service_container.markdown("------")

    # structure_container.markdown("## Structure Team")
    # structure_extractor.extract(header=header, table=table, gauge=gauge, attribute_display=False)
    # if not display_grid:
    #     structure_container.markdown("------")
    #     structure_container.markdown("------")

    # industrial_container.markdown("## Industrial Team")
    # industrial_extractor.extract(header=header, table=table, gauge=gauge, attribute_display=False)

    return None
