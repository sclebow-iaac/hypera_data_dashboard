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


def extract(attribute_display=True, container=None):
    return data_extractor.extract(data, model_name, attribute_display=attribute_display, container=container)


def display_data(extracted_data, model_data, verbose=True, header=True, show_table=True, gauge=True, simple_table=False, container=None):
    data_extractor.display_data(data, extracted_data, model_data=model_data, verbose=verbose, header=header,
                                show_table=show_table, gauge=gauge, simple_table=simple_table, container=container)
