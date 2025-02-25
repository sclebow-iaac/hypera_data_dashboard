# This file is used to extract data from the residential model

import data_extraction.data_extractor as data_extractor

model_name = "hypera/residential/programming/residential/data"

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

def extract(models, client, project_id, header=True, table=True, gauge=True, attribute_display=True):
    return data_extractor.extract(data, model_name, models, client, project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)