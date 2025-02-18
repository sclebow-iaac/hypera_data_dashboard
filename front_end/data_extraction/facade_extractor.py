# This file is used to extract data from the facade model

import data_extraction.data_extractor as data_extractor

model_name = ""

data_names = [
    "ResidentialAreaWithDaylight",
    "TotalResidentialArea",
    "WorkAreaWithDaylight",
    "TotalWorkArea",
    "TotalFinalPanelArea",
    "TotalInitialPanelArea",
    "EnergyGeneration",
    "EnergyRequiredByIndustrialTeam"
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
    "Square Meters",
    "Square Meters",
    "Square Meters",
    "Square Meters",
    "Kilowatt Hours",
    "Kilowatt Hours"
]

data = dict(zip(data_names, zip(data_types, data_units)))

def extract(models, client, project_id):
    return data_extractor.extract(data, model_name, models, client, project_id)