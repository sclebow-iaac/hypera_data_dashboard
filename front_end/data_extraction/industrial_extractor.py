# This file is used to extract data from the industrial model

import data_extraction.data_extractor as data_extractor

model_name = "hypera/industrial/data"

data_names = [
    "EnergyGeneration",
    "EnergyDemand",
    "FoodProduction",
    "FoodDemand",
    "RecycledWater",
    "WasteWaterProduction",
    "RecycledSolidWaste",
    "SolidWasteProduction"
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
    "Kilowatt Hours",
    "Kilowatt Hours",
    "Kilograms",
    "Kilograms",
    "Cubic Meters",
    "Cubic Meters",
    "Kilograms",
    "Kilograms"
]

data = dict(zip(data_names, zip(data_types, data_units)))

def get_data():
    return data

def extract(models, client, project_id):
    return data_extractor.extract(data, model_name, models, client, project_id)