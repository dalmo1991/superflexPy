"""
File to create the results with Superflex
"""

import sys

# Add the path where the Superflex module is
sys.path.append("/home/dalmo/Documents/BitBucket/superflexPython/C_so/")
from os import chdir

import numpy as np
from superflex import Superflex_C

chdir("/home/dalmo/Documents/BitBucket/superflexpy_aug2019/test/reference_results/06_3Cats_2HRUs/")

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
    header="Q_c1, Q_c2, Q_c3, Q_c1_h1, S_c1_h1_FR, Q_c2_h1, S_c2_h1_FR, Q_c3_h1, S_c3_h1_FR, Q_c1_h2, E_c1_h2_UR, S_c1_h2_UR, S_c1_h2_FR, S_c1_h2_SR, Q_c2_h2, E_c2_h2_UR, S_c2_h2_UR, S_c2_h2_FR, S_c2_h2_SR, Q_c3_h2, E_c3_h2_UR, S_c3_h2_UR, S_c3_h2_FR, S_c3_h2_SR",
)
