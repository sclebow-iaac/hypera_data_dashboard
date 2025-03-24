import streamlit as st
import data_extraction.data_extractor as data_extractor

from specklepy.objects.base import Base

from dashboards.dashboard import setup_speckle_connection

def run_from_version_id(version_id, model_id):
    models, client, project_id = setup_speckle_connection()
    # Get the version object from the model
    version = client.version.get(version_id, project_id)

    # Get the project object from the model
    project = client.project.get(project_id)

    # Run the extraction function with the selected version
    run(version, client, project)

def run(selected_version, client, project):
    with st.spinner("Getting geometry data..."):
        # Create a container for the attribute extraction section
        attribute_container = st.container()

        # Add a toggle to show data extraction debug information
        show_extraction_debug = attribute_container.checkbox(
            label="Show data extraction debug information for the selected version (Slow Process)",
            value=False,
            help="Toggle to show/hide data extraction debug information"
        )

        if show_extraction_debug:

            base = data_extractor.get_geometry_data(
                selected_version, client, project, verbose=True)
            print(f'base: {base}\n')

            base_data = base
            while '@Data' in dir(base_data):
                base_data = base_data.__getitem__('@Data')

            keys = [key for key in dir(base_data) if not key.startswith('__')]
            print(f'keys: {keys}\n')

            all_attributes_flattened = data_extractor.get_all_attributes(
                base_data, flattened=True, verbose=False)
            print(f'all_attributes_flattened: {all_attributes_flattened}\n')

            # Add a dropdown to select the attribute to search for
            selected_attribute = attribute_container.selectbox(
                label="Select attribute to search for",
                options=sorted(list(all_attributes_flattened)),
                help="Select a specific attribute to search for in the base data"
            )

            # Add a toggle to search for a single or all occurrences of the attribute
            search_single = attribute_container.checkbox(
                label="Search for a single occurrence",
                value=True,
                help="Toggle to search for a single or all occurrences of the selected attribute"
            )

            # Check if a specific attribute exists in the base data
            attribute_to_search = selected_attribute
            attribute_found = data_extractor.search_for_attribute(
                base_data, attribute_to_search, single=search_single, verbose=False)
            print(
                f'Attribute {attribute_to_search} found: {attribute_found}\n')

            # Display the found attribute as a markdown table
            if attribute_found[0]:
                table_header = "| Attribute | Value |\n| --- | --- |\n"
                table_data = ""
                for i, value in enumerate(attribute_found[1]):
                    table_data += f"| {attribute_to_search} | {value} |\n"
                attribute_container.markdown(table_header + table_data)
            else:
                attribute_container.error(
                    f"Attribute {attribute_to_search} not found in the base data")

            # If value is type Base, get all attributes
            for i, value in enumerate(attribute_found[1]):
                if type(value) == Base:
                    table_header = "| Attribute | Value |\n| --- | --- |\n"
                    table_data = ""
                    attribute_container.write(
                        f'Attribute {attribute_to_search} is of type BaseData')
                    all_attributes_flattened = list(data_extractor.get_all_attributes(
                        value, flattened=True, verbose=False))
                    attribute_container.write(
                        f'all_attributes_flattened: {all_attributes_flattened}\n')

                    for key in all_attributes_flattened:
                        sub_found, sub_value = data_extractor.search_for_attribute(
                            value, key, single=True, verbose=False)
                        table_data += f"| {key} | {sub_value[0]} |\n"
                    attribute_container.markdown(table_header + table_data)
                    break
