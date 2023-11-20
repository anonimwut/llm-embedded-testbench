import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

def load_data_1D(file_name):
    # Initialize lists for each data type
    data = []

    with open(file_name, 'r') as file:
        for line in file:
            # Skip empty lines
            line = line.strip()
            if line:
                try:
                    # Attempt to convert to float and append to data
                    data.append([float(line)])
                except ValueError:
                    # If conversion fails, print a warning and continue
                    print(f"Warning: could not convert '{line}' to float. Skipping line.")

    # Convert lists to numpy arrays
    data = np.array(data)

    return data


def truncate_arrays(array1, array2):
    if len(array1) > len(array2):
        diff = len(array1) - len(array2)
        array1 = array1[diff:]
    elif len(array2) > len(array1):
        diff = len(array2) - len(array1)
        array2 = array2[diff:]
    
    return array1, array2

def euclidian_distance(data1, data2):
    # Load data from two files
    data1 = np.array(data1).flatten()
    data2 = np.array(data2).flatten()
    #data1, data2 = truncate_arrays(data1, data2)
    # Check that the inputs are 1-D
    assert data1.ndim == 1, f"Expected data1 to be 1-D, but it has shape {data1.shape}"
    assert data2.ndim == 1, f"Expected data2 to be 1-D, but it has shape {data2.shape}"
  

    # Use dynamic time warping to compute the distance between the two sequences
    distance, path = fastdtw(data1, data2)

    return distance
