# This file is used to extract data from the service model

import data_extraction.data_extractor as data_extractor

model_name = "hypera/services/neighborhoods/massing"

data_names = [
    "ListOfFunctionNames",
    "UtilizationRateOfFunction",
    "ActiveHoursOfFunctionPerDay",
    "FunctionExchangeFactor",
    "TotalAvailableHoursPerDay",
    "TotalSpacesAvailable"
]

data_types = [
    "list",
    "list",
    "list",
    "list",
    "float",
    "int"
]

data_units = [
    "None",
    "Percentage (0.0 - 1.0)",
    "Hours",
    "None",
    "Hours",
    "Count"
]

data = dict(zip(data_names, zip(data_types, data_units)))

def extract(models, client, project_id, header=True, table=True, gauge=True, attribute_display=True):
    return data_extractor.extract(data, model_name, models, client, project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)