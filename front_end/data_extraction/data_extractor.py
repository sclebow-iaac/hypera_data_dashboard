# This file is used to extract data from a specific model

from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

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
    extracted_data = {}
    selected_model = None
    for model in models:
        if model.name == model_name:
            selected_model = model
            break

    if selected_model is None:
        if verbose:
            print(f'Model {model_name} not found.')

        return None
    
    if verbose:
        print(f'Model {model_name} found.')

    base_data = get_geometry_data(selected_model, client, verbose=verbose)

    if verbose:
        print(f'Base data received.')

    all_attributes = get_all_attributes(base_data, flattened=True)
    if verbose:
        print(f'All attributes: {all_attributes}')

    for data_name in data:
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

    return extracted_data