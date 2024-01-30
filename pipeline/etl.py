import pandas as pd
import numpy as np

def etl():
    url1 = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_facility.csv"
    url2 = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv"
    url3 = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_facility.csv"
    url4 = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_state.csv"

    donate_fac = pd.read_csv(url1).to_json(orient="records")
    donate_state = pd.read_csv(url2).to_json(orient="records")
    new_donors_fac = pd.read_csv(url3).to_json(orient="records")
    new_donors_state = pd.read_csv(url4).to_json(orient="records")

    return donate_fac, donate_state, new_donors_fac, new_donors_state
