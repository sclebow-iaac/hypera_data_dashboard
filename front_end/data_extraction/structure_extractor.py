# This file is used to extract data from the structure model

import front_end.data_extraction.data_extractor as data_extractor

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

def extract(models, client):
    return data_extractor.extract(data, model_name, models, client)