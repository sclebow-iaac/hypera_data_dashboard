# This file is used to extract data from a specific model

import streamlit as st

from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

import pandas as pd

import plotly.graph_objects as go

import colour  # For color conversion

import attribute_extraction

def get_geometry_data(selected_version, client, project, verbose=True):
    objHash = selected_version.referencedObject
    if verbose:
        print(f'objHash: {objHash}')
        print(f'Starting to receive data...\n')
    transport = ServerTransport(client=client, stream_id=project.id)
    base = operations.receive(objHash, transport)
    if verbose:
        print(f'Data received.\n')
    return base


def get_all_attributes(base_data, flattened=True, depth=0, all_attributes=set(), verbose=True) -> set:
    if depth == 0:  # If depth is 0, we are starting the search
        all_attributes = set()

    if verbose:
        print()  # Debugging
        print(f'{"-" * depth}Getting attributes of {base_data}...')
        print(f'{"-" * depth}Attributes: {base_data.__dict__}')

    for key in base_data.__dict__:
        if verbose:
            print(
                f'{"-" * depth}Key: {key} - Value: {base_data.__dict__[key]} - Type: {type(base_data.__dict__[key])}')

        all_attributes.add(key)

        if flattened:  # If flattened is True, we need to recursively get all attributes of nested objects

            value = base_data.__dict__[key]

            # If the value is not a list, we need to make it a list to iterate over it
            if type(value) != list:
                value = [value]

            for item in value:
                if item is not None:
                    if verbose:
                        print(f'{"-" * depth}Item: {item}')

                    if type(item) == Base:
                        if verbose:
                            print(f'{"-" * depth}Item is a Base object.')

                        all_attributes = get_all_attributes(
                            item, flattened=True, depth=depth+1, all_attributes=all_attributes, verbose=verbose)

    return all_attributes


# single=True means we only want to find the first occurrence of the attribute, return all values of the attribute
def search_for_attribute(base_data: Base, attribute: str, depth=0, single=True, found=False, output=[], verbose=True):
    if depth == 0:  # If depth is 0, we are starting the search
        output = []
        found = False

    if verbose:
        print(f'{"  " * depth}Searching for attribute {attribute} in {base_data}...')
        print(f'{"  " * depth}Attributes: {base_data.__dict__}')

    for key in base_data.__dict__:
        if key == attribute:  # If the key is the attribute we are looking for
            found = True  # Set found to True
            # Append the value of the attribute to the output list
            output.append(base_data.__dict__[key])
            if single:  # If we only want to find the first occurrence of the attribute, break the loop
                break

        if verbose:  # Debugging
            print(
                f'{"-" * depth}Key: {key} - Value: {base_data.__dict__[key]} - Type: {type(base_data.__dict__[key])}')

        value = base_data.__dict__[key]  # Get the value of the key

        if type(value) != list:  # If the value is not a list, we need to make it a list to iterate over it
            value = [value]  # Make the value a list

        for item in value:  # Iterate over the value
            if item is not None:  # If the item is not None
                if verbose:  # Debugging
                    print(f'{"-" * depth}Item: {item}')  # Debugging

                # If the item is a Base object, we need to recursively search for the attribute
                if type(item) == Base:
                    if verbose:  # Debugging
                        # Debugging
                        print(f'{"-" * depth}Item is a Base object.')

                    # Recursively search for the attribute in the item object
                    found, output = search_for_attribute(
                        item, attribute, depth=depth+1, single=single, found=found, output=output, verbose=verbose)

    return found, output


def extract(data, model_name, models, client, project_id, verbose=True, header=True, table=True, gauge=True, attribute_display=True):

    if verbose:
        print(f'Model name: {model_name}')  # Debugging
        print(f'data: {data}')  # Debugging

        print(f'data.keys(): {data.keys()}')  # Debugging

    extracted_data = {}
    selected_model = None
    for model in models:
        if model.name == model_name:
            selected_model = model
            break

    if selected_model is None:  # If model is not found
        if verbose:
            print(f'Model {model_name} not found.')

        # Return None for all data if model is not found
        extracted_data = {key: None for key in data.keys()}

    else:  # If model is found
        if verbose:
            print(f'Model {model_name} found.')

        # Get projects
        selected_project = client.project.get(project_id=project_id)

        # Get the project with models
        project = client.project.get_with_models(
            project_id=selected_project.id, models_limit=100)
        print(f'Project: {project.name}')

        versions = client.version.get_versions(
            model_id=selected_model.id, project_id=project.id, limit=100).items
        latest_version = versions[0]
        print(
            f'latest_version, createdAt: {latest_version.createdAt.strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'latest_version, authorUser: {latest_version.authorUser.name}')

        with st.spinner(f'Receiving data from {model_name}'):
            base_data = get_geometry_data(
                latest_version, client, project, verbose=verbose)

        nested_index = 0
        while '@Data' in dir(base_data):
            base_data = base_data.__getitem__('@Data')
            nested_index += 1
            print(f'Nested index: {nested_index}')

        if verbose:
            print(f'Base data received.')

        all_attributes = get_all_attributes(base_data, flattened=True)
        if verbose:
            print(f'All attributes: {all_attributes}')

        for data_name in data.keys():
            print()  # Debugging
            print(f'Data name: {data_name}')  # Debugging
            data_names = [data_name, '@' + data_name]

            for name in data_names:
                print(f'Searching for attribute {name}...')  # Debugging
                if name not in all_attributes:
                    if verbose:
                        print(f'Attribute {name} not in all_attributes.')
                    extracted_data[data_name] = None
                else:
                    if verbose:
                        print(f'Attribute {name} is in all_attributes.')

                    found, output = search_for_attribute(
                        base_data, name, single=False, verbose=False)
                    if verbose:
                        print(f'Found: {found} - Output: {output}')
                    if found:  # If the attribute is found
                        # Set the extracted data to the output
                        extracted_data[data_name] = output[0]
                        # Iterate over the output to get the first non-None value or non-Base object
                        # Check if the output is a list
                        if type(output) != list:
                            output = [output]
                        for item in output:
                            if item is not None and type(item) != Base:
                                extracted_data[data_name] = item
                                break
                        # extracted_data[data_name] = output[0] # Set the extracted data to the output
                        # print(f'Attribute {name} found: {output[0]}') # Debugging
                        break  # Break the loop if the attribute is found
                #     else:
                #         print(f'Attribute {name} not found.')

                # else:
                #     if verbose:
                #         print(f'Attribute {name} not found.')
                #         extracted_data[data_name] = None

    display_data(data, extracted_data, model_name, verbose=False, header=header, show_table=table, gauge=gauge)
    
    if attribute_display:
        # Add a separator
        st.markdown("---")
        # Add attribute extraction for debugging
        attribute_extraction.run(latest_version, client, project)

    return extracted_data

# Display a markdown table with the extracted data


def display_data(data, extracted_data, model_name, verbose=True, header=True, show_table=True, gauge=True):
    if header:
        # Display the model name
        st.markdown('### Model Name')
        if model_name is not None and model_name != "":
            st.markdown(f'#### {model_name}')
        else:
            st.markdown(f'Model: {model_name} not found.')

        st.markdown('---')

    if verbose:
        print(f'Extracted data: {extracted_data}')
    header = ['Attribute Name', 'Found', 'Value', 'Type', 'Unit']
    table = [header]

    print()

    type_matched_bools = []

    for key in data:
        value = extracted_data[key]
        if value is None:
            value = "Not Found"

        # If the value is a list with one element, get the first element
        if type(value) == list and len(value) == 1:
            value = value[0]

        type_expected = data[key][0]
        unit = data[key][1]

        if type_expected == 'float':
            try:
                value = float(value)
                print(f'{key} converted to float')
            except:
                print('Error converting value to float')
        
        if type_expected == 'int':
            try:
                value = int(value)
                print(f'{key} converted to int')
            except:
                print('Error converting value to int')

        type_extracted = type(value).__name__

        print(f'Key: {key} - Value: {value}')
        print(f'Type: {type(value).__name__}')
        print(f'Type expected: {type_expected}')
        print()
        
        type_matched_bools.append(type_expected == type_extracted)
        if verbose:
            print(
                f'Key: {key} - Value: {value} - Type Expected: {type_expected} - Type Extracted: {type_extracted}')
        if extracted_data[key] is not None:
            if type_expected == type_extracted:
                table.append([key, 'Yes', str(value), f'{type_extracted} (As Expected)', unit])
            else:
                table.append(
                    [key, 'Yes', value, f'{type_extracted} (Expected: {type_expected})', unit])
        else:
            table.append([key, 'No', value, type_expected, unit])

    if show_table:
        df = pd.DataFrame(table[1:], columns=table[0])

        st.markdown('### Extracted Data')
        st.table(df)
        st.markdown('---')

    if gauge:
        # Display a percentage of the data found compared to the total data expected

        # Make two columns
        column1, column2 = st.columns(2)

        total_data = len(data)
        data_found = len(
            [key for key in extracted_data if extracted_data[key] is not None])
        data_not_found = total_data - data_found
        percentage_found = (data_found / total_data)

        percentage_type_matched = sum(type_matched_bools) / len(type_matched_bools)

        column1.markdown('### Data Found')
        # Display the number of data found
        column1.markdown(f'{data_found} / {total_data}')
        column1.progress(percentage_found)  # Display the percentage of data found
        column1.markdown(f'### Data Type Verified')
        # Display the percentage of data type matched
        column1.markdown(f'{sum(type_matched_bools)} / {len(type_matched_bools)}')
        column1.progress(percentage_type_matched)

        column2.markdown('### Data Not Found')
        # Display the number of data not found
        column2.markdown(f'{data_not_found} / {total_data}')
        # Display the percentage of data not found
        column2.progress(1 - percentage_found)
        column2.markdown(f'### Data Type Not Verified')
        # Display the percentage of data type not matched
        column2.markdown(f'{len(type_matched_bools) - sum(type_matched_bools)} / {len(type_matched_bools)}')
        column2.progress(1 - percentage_type_matched)

        # To debug make a slider to change the percentage found
        # Make a toggle to show the debug slider
        # debug = st.checkbox(f'Debug Slider {model_name}', key=f'Debug Slider {model_name}')
        # if debug:
        #     percentage_type_matched = st.slider(
        #         "Percentage Found", 0.0, 1.0, percentage_type_matched)

        # Create a gauge chart using Plotly
        # Color should gradient from red to green based on the percentage found
        color = colour.Color("red").range_to(colour.Color("green"), 101)
        color = [c.hex for c in color]

        color = list(color)[int(percentage_type_matched * 100)]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percentage_type_matched * 100,
            number={'suffix': "%"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
            },
            title={'text': "Data Verified (%)"},
        ))

        fig.update_layout(
            height=300
        )

        st.plotly_chart(fig, use_container_width=True, key=f'Gauge {model_name}')
        # # Create Three Columns
        # col1, col2, col3 = st.columns(3, vertical_alignment="top")
        
        # col2.plotly_chart(fig, use_container_width=True)


    return extracted_data
