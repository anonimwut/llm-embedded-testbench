import pandas as pd
import numpy as np
from scipy import fftpack
from scipy.signal import butter, lfilter

def load_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    data = {
        'A_X': [],
        'A_Y': [],
        'A_Z': [],
    }

    temp_data = {
        'A_X': None,
        'A_Y': None,
        'A_Z': None,
    }

    # Iterate through lines and add values to the data dictionary
    for line in lines:
        try:
            key, value = line.strip().split(" = ")
            if key in temp_data:
                temp_data[key] = float(value)

                # If we have a full set of values, append them to the data dictionary
                if all(temp_data.values()):
                    for k in data:
                        data[k].append(temp_data[k])
                    # Reset temp_data for next set of values
                    temp_data = {
                        'A_X': None,
                        'A_Y': None,
                        'A_Z': None,
                    }
        except: 
            pass

    # Convert data dictionary to pandas DataFrame
    df = pd.DataFrame(data)

    return df

def compute_means(df):
    means = [
        df['A_X'].mean(),
        df['A_Y'].mean(),
        df['A_Z'].mean(),
    ]
    return means
