import streamlit as st
import data_extraction.data_extractor as data_extractor

def run(selected_version, client, project):
    with st.spinner("Getting geometry data..."):
        
        # Add a toggle to show data extraction debug information
        show_extraction_debug = st.checkbox(
            label="Show data extraction debug information for the selected version",
            value=False,
            help="Toggle to show/hide data extraction debug information"
        )

        if show_extraction_debug:
        
            base = data_extractor.get_geometry_data(selected_version, client, project, verbose=True)
            print(f'base: {base}\n')

            # all_attributes_unflattened = get_all_attributes(base)
            # print(f'all_attributes_unflattened: {all_attributes_unflattened}\n')
            try: base_data = base["@Data"]
            except: base_data = base
            print(f'base_data: {base_data}\n')

            keys = [key for key in dir(base_data) if not key.startswith('__')]
            print(f'keys: {keys}\n')


            # while '@Data' in dir(base_data):
            #     print(f'base_data: {base_data}')
            #     base_data = base_data.__getitem__('@Data')

            all_attributes_flattened = data_extractor.get_all_attributes(base_data, flattened=True)
            print(f'all_attributes_flattened: {all_attributes_flattened}\n')

            # Add a dropdown to select the attribute to search for
            selected_attribute = st.selectbox(
                label="Select attribute to search for",
                options=sorted(list(all_attributes_flattened)),
                help="Select a specific attribute to search for in the base data"
            )

            # Add a toggle to search for a single or all occurrences of the attribute
            search_single = st.checkbox(
                label="Search for a single occurrence",
                value=True,
                help="Toggle to search for a single or all occurrences of the selected attribute"
            )

            # Check if a specific attribute exists in the base data
            attribute_to_search = selected_attribute
            attribute_found = data_extractor.search_for_attribute(base_data, attribute_to_search, single=search_single)
            print(f'Attribute {attribute_to_search} found: {attribute_found}\n')

            # Display the found attribute as a markdown table
            if attribute_found[0]:
                table_header = "| Attribute | Value |\n| --- | --- |\n"
                table_data = ""
                for i, value in enumerate(attribute_found[1]):
                    table_data += f"| {attribute_to_search} | {value} |\n"
                st.markdown(table_header + table_data)
            else:
                st.error(f"Attribute {attribute_to_search} not found in the base data")