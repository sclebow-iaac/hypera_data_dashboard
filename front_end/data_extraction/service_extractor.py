# This file is used to extract data from the service model

import data_extraction.data_extractor as data_extractor

model_name = "hypera/services/neighborhoods/data"

data_names = [
    "ListOfFunctionNames",
    "UtilizationRateOfFunction",
    "ActiveHoursOfFunctionPerDay",
    "FunctionExchangeFactor",
    "TotalAvailableHoursPerDay",
    "TotalArea",
    "AreaOfFunctions"
]

data_types = [
    "list",
    "list",
    "list",
    "list",
    "float",
    "float",
    "list"
]

data_units = [
    "None",
    "Percentage (0.0 - 1.0)",
    "Hours",
    "None",
    "Hours",
    "Square Meters",
    "Square Meters"
]

data = dict(zip(data_names, zip(data_types, data_units)))


def extract(header=True, table=True, gauge=True, attribute_display=True, container=None):
    return data_extractor.extract(data, model_name, header=header, table=table, gauge=gauge, attribute_display=attribute_display, container=container)


def display_data(extracted_data, verbose=True, header=True, show_table=True, gauge=True, simple_table=False, container=None):
    data_extractor.display_data(data, extracted_data, model_name, verbose=verbose, header=header,
                                show_table=show_table, gauge=gauge, simple_table=simple_table, container=container)
