# This file is used to extract data from a specific model

import streamlit as st

from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

import pandas as pd

import plotly.graph_objects as go

import colour # For color conversion

def get_geometry_data(selected_version, client, project, verbose=True):
    objHash = selected_version.referencedObject
    if verbose:
        print(f'objHash: {objHash}')
        print(f'Starting to receive data...\n')
    transport = ServerTransport(client=client, stream_id=project.id)
    base = operations.receive(objHash, transport)
    return base

def get_all_attributes(base_data: Base, flattened=False, depth=0, all_attributes=set()) -> set:
    # print(f'{"-" * depth}Getting attributes of {base}...')
    
    for key in base_data.__dict__:
        if depth < 2:
            try:
                print(f'depth: {depth} - Key: {key} - Type: {type(base_data.__dict__[key])}')
            except Exception as e:
                # print(f'Error: {e}')
                pass
        # print(f'{"  " * depth}Key: {key} - Value: {base.__dict__[key]} - Type: {type(base.__dict__[key])}')
        all_attributes.add(key)

        if flattened: # If flattened is True, we need to recursively get all attributes of nested objects
            if base_data.__getitem__(key) is not None:
                try:
                    all_attributes = get_all_attributes(base_data.__getitem__(key)[0], flattened=True, depth=depth+1, all_attributes=all_attributes)
                except Exception as e:
                    # print(f'Error: {e}')
                    pass
                    

    return all_attributes

def search_for_attribute(base_data: Base, attribute: str, depth=0, single=True, found=False, output=[]): # single=True means we only want to find the first occurrence of the attribute, return all values of the attribute
    # print(f'{"  " * depth}Searching for attribute {attribute} in {base_data}...')

    for key in base_data.__dict__:
        # print(f'{"  " * depth}Key: {key} - Value: {base_data.__dict__[key]} - Type: {type(base_data.__dict__[key])}')
        if key == attribute:
            found = True
            output.append(base_data.__dict__[key])
            if single:
                break

        if base_data.__getitem__(key) is not None:
            try:
                found, output = search_for_attribute(base_data.__getitem__(key)[0], attribute, depth=depth+1, single=single, found=found, output=output)
            except Exception as e:
                # print(f'Error: {e}')
                pass

    return found, output

def extract(data, model_name, models, client, verbose=True):

    if verbose:
        print(f'Model name: {model_name}') # Debugging
        print(f'data: {data}') # Debugging

        print(f'data.keys(): {data.keys()}') # Debugging

    extracted_data = {}
    selected_model = None
    for model in models:
        if model.name == model_name:
            selected_model = model
            break

    if selected_model is None: # If model is not found
        if verbose:
            print(f'Model {model_name} not found.')

        extracted_data = {key: None for key in data.keys()} # Return None for all data if model is not found

    else: # If model is found
        if verbose:
            print(f'Model {model_name} found.')

        base_data = get_geometry_data(selected_model, client, verbose=verbose)

        if verbose:
            print(f'Base data received.')

        all_attributes = get_all_attributes(base_data, flattened=True)
        if verbose:
            print(f'All attributes: {all_attributes}')

        for data_name in data.keys():
            print(f'Data name: {data_name}') # Debugging
            data_names = [data_name, '@' + data_name]

            for name in data_names:
                if name in all_attributes:
                    found, output = search_for_attribute(base_data, name, single=True, found=False, output=[])
                    if found:
                        extracted_data[data_name] = output[0]
                        break
                else:
                    if verbose and name[0] == '@':
                        print(f'Attribute {name[1:]} not found.')
                        extracted_data[data_name] = None

    display_data(data, extracted_data, model_name, verbose=verbose)

    return extracted_data

# Display a markdown table with the extracted data
def display_data(data, extracted_data, model_name, verbose=True):

    # Display the model name
    st.markdown('### Model Name')
    if model_name is not None and model_name != "":
        st.markdown(model_name)
    else:
        st.markdown(f'Model: {model_name} not found.')

    st.markdown('---')

    if verbose:
        print(f'Extracted data: {extracted_data}')
    header = ['Attribute Name', 'Found', 'Value', 'Type', 'Unit']
    table = [header]

    for key in data:
        value = extracted_data[key]
        if value is None:
            value = "Not Found"
        type_expected = data[key][0]
        unit = data[key][1]
        type_extracted = type(value).__name__        

        if verbose:
            print(f'Key: {key} - Value: {value} - Type Expected: {type_expected} - Type Extracted: {type_extracted}')
        if extracted_data[key] is not None:
            if type_expected == type_extracted:
                table.append([key, 'Yes', value, type_extracted, unit])
            else:
                table.append([key, 'Yes', value, f'{type_extracted} (Expected: {type_expected})', unit])
        else:
            table.append([key, 'No', value, type_expected, unit])

    df = pd.DataFrame(table[1:], columns=table[0])

    st.markdown('### Extracted Data')
    st.table(df)
    st.markdown('---')

    # Display a percentage of the data found compared to the total data expected

    # Make two columns
    column1, column2 = st.columns(2)

    total_data = len(data)
    data_found = len([key for key in extracted_data if extracted_data[key] is not None])
    data_not_found = total_data - data_found
    percentage_found = (data_found / total_data)
    
    column1.markdown('### Data Found')
    column1.markdown(f'{data_found} / {total_data}') # Display the number of data found
    column1.progress(percentage_found) # Display the percentage of data found

    column2.markdown('### Data Not Found')
    column2.markdown(f'{data_not_found} / {total_data}') # Display the number of data not found
    column2.progress(1 - percentage_found) # Display the percentage of data not found

    # To debug make a slider to change the percentage found
    # Make a toggle to show the debug slider
    debug = st.checkbox("Debug")
    if debug:
        percentage_found = st.slider("Percentage Found", 0.0, 1.0, percentage_found)
    # Create a gauge chart using Plotly
    # Color should gradient from red to green based on the percentage found
    color = colour.Color("red").range_to(colour.Color("green"), 101)
    color = [c.hex for c in color]
    
    color = list(color)[int(percentage_found * 100)]

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentage_found * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
        },
        title = {'text': "Data Found (%)"},
    ))

    st.plotly_chart(fig)

    return extracted_data