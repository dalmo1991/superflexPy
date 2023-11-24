"""
File to create the results with Superflex
"""

import sys

# Add the path where the Superflex module is
sys.path.append("/home/dalmo/Documents/BitBucket/superflexPython/C_so/")
from os import chdir

import numpy as np
from superflex import Superflex_C

chdir("/home/dalmo/Documents/BitBucket/superflexpy_aug2019/test/reference_results/05_2HRUs/")

# Initialize the class
sup = Superflex_C()

# Load the model
dims = sup.load_model()

# Initialize the parameters
parameters = np.array([[]])

# Get the output
output = sup.run_model(parameters)

np.savetxt(
    "Results.csv",
    X=output,
    delimiter=",",
    header="Q_tot, Q_H1, E_FR_H1, S_FR_H1, Q_H2, E_UR_H2, S_UR_H2, S_FR_H2, S_SR_H2",
)
