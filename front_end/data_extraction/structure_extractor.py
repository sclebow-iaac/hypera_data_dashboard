# This file is used to extract data from the structure model

import data_extraction.data_extractor as data_extractor

model_name = ""

data_names = [
    "TotalColumnFreeFloorArea",
    "TotalFloorArea",
    "TotalEmbodiedCarbonEmissions",
    "UsableFloorArea",
    "LoadCapacity",
    "SelfWeightOfStructure",
    "TheoreticalMinimumMaterialUsage",
    "ActualMaterialUsage"
]

data_types = [
    "float",
    "float",
    "float",
    "float",
    "float",
    "float",
    "float",
    "float"
]

data_units = [
    "Square Meters",
    "Square Meters",
    "Kilograms",
    "Square Meters",
    "Kilograms",
    "Kilograms",
    "Kilograms",
    "Kilograms"
]

data = dict(zip(data_names, zip(data_types, data_units)))

def extract(models, client, project_id, header=True, table=True, gauge=True, attribute_display=True):
    return data_extractor.extract(data, model_name, models, client, project_id, header=header, table=table, gauge=gauge, attribute_display=attribute_display)