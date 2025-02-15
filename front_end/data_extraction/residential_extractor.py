# This file is used to extract data from the residential model

import front_end.data_extraction.data_extractor as data_extractor

model_name = ""

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

def extract(models, client):
    return data_extractor.extract(data, model_name, models, client)