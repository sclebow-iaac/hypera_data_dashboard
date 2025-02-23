# This file is used to extract data from the residential model

import data_extraction.data_extractor as data_extractor

model_name = "hypera/residential/building form/residential"

data_names = [
    "ListOfUnitFunctions",
    "NumberOfUnitsOfASingleFunction"
]

data_types = [
    "list",
    "list"
]

data_units = [
    "None",
    "Count"
]

data = dict(zip(data_names, zip(data_types, data_units)))

metric_data = {data_names[0]: data_types[0], data_names[1]: data_types[1]}

def get_data():
    return data

def extract(models, client, project_id):
    return data_extractor.extract(data, model_name, models, client, project_id)