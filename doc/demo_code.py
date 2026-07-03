# Import other libraries
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from superflexpy.framework.network import Network
from superflexpy.framework.node import Node
from superflexpy.framework.unit import Unit
from superflexpy.implementation.elements.gr4j import UnitHydrograph1

# Import SuperflexPy
from superflexpy.implementation.elements.hbv import PowerReservoir
from superflexpy.implementation.numerical_approximators.implicit_euler import (
    ImplicitEulerPython,
)
from superflexpy.implementation.root_finders.pegasus import PegasusPython

# Set the wd to the one of the file, to avoid absolute paths
os.chdir(sys.path[0])

# Initialize solver (default settings)
solver_python = PegasusPython()
approximator = ImplicitEulerPython(root_finder=solver_python)
# %% Run element
# Initialize the reservoir
reservoir = PowerReservoir(
    parameters={"k": 0.01, "alpha": 2.0}, states={"S0": 10.0}, approximation=approximator, id="R"
)

reservoir.set_timestep(1.0)

# Create input
precipitation = np.array(
    [6.5, 3.0, 0.0, 0.0, 0.0, 2.0, 4.0, 8.0, 2.0, 0.0, 0.0, 2.5, 1.0, 0.0, 4.0, 0.0, 1.0, 0.0, 0.0, 0.0]
)

# Set input
reservoir.set_input([precipitation])

# Run the element
output = reservoir.get_output()[0]
reservoir_state = reservoir.state_array[:, 0]

# Plotting
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
ax[0].bar(x=range(len(precipitation)), height=precipitation, color="blue")

ax[1].plot(range(len(precipitation)), output, color="blue", lw=2, label="Outflow")

ax_bis = ax[1].twinx()
ax_bis.plot(range(len(precipitation)), reservoir_state, color="red", lw=2, ls="--", label="Reservoir state")

ax[0].set_ylabel("Precipitation [mm/day]")
ax[1].set_ylabel("Flow [mm/day]")
ax_bis.set_ylabel("State [mm]")
ax[1].set_xlabel("Time [day]")

lines = [
    Line2D([0], [0], color="blue", lw=2, label="Outflow"),
    Line2D([0], [0], color="red", lw=2, ls="--", label="Reservoir state"),
]
ax[1].legend(lines, [l.get_label() for l in lines])

fig.savefig("pics/demo/SingleReservoir.png", res=600)

# %% Run Unit
# Reset the fast reservoir (we use it again)
reservoir.reset_states()

# Initialize the lag function
lag_function = UnitHydrograph1(parameters={"lag-time": 2.3}, states={"lag": None}, id="lag-fun")

# Create unit
unit_1 = Unit(layers=[[reservoir], [lag_function]], id="unit-1")

unit_1.set_timestep(1.0)

unit_1.set_input([precipitation])

# Run the unit
output = unit_1.get_output()[0]

# Fast reservoir
r_state = unit_1.get_internal(id="R", attribute="state_array")[:, 0]
r_output = unit_1.call_internal(id="R", method="get_output", solve=False)[0]

# The output of lag is the same of the unit

# Plotting
fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 9))

ax[0].bar(x=range(len(precipitation)), height=precipitation, color="blue")

ax[1].plot(range(len(precipitation)), r_output, color="blue", lw=2, label="Outflow")
ax_bis = ax[1].twinx()
ax_bis.plot(range(len(precipitation)), r_state, color="red", lw=2, ls="--", label="Reservoir state")

ax[2].plot(range(len(precipitation)), output, color="blue", lw=2, label="Outflow")

ax[0].set_ylabel("Precipitation [mm/day]")
ax[1].set_ylabel("Outflow [mm/day]")
ax_bis.set_ylabel("State [mm]")
ax[2].set_ylabel("Outflow [mm/day]")
ax[2].set_xlabel("Time [day]")
ax[1].set_title("Reservoir")
ax[2].set_title("Lag function")

lines = [
    Line2D([0], [0], color="blue", lw=2, label="Outflow"),
    Line2D([0], [0], color="red", lw=2, ls="--", label="Reservoir state"),
]
ax[1].legend(lines, [l.get_label() for l in lines])
ax[2].legend(lines[:1], [l.get_label() for l in lines[:1]])

fig.savefig("pics/demo/SingleUnit.png", res=600)

# %% Run Node

# Reset states of Unit1
unit_1.reset_states()
unit_1.set_states({"unit-1_lag-fun_lag": None})  # Remove after new build

# Create second unit
unit_2 = Unit(layers=[[reservoir]], id="unit-2")

# Put units together in a node
node_1 = Node(units=[unit_1, unit_2], weights=[0.7, 0.3], area=10.0, id="node-1")

node_1.set_timestep(1.0)
node_1.set_input([precipitation])

# Solve the node
output = node_1.get_output()[0]

output_unit_1 = node_1.call_internal(id="unit-1", method="get_output", solve=False)[0]
output_unit_2 = node_1.call_internal(id="unit-2", method="get_output", solve=False)[0]

# Plotting
fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 9))

ax[0].bar(x=range(len(precipitation)), height=precipitation, color="blue")

ax[1].plot(range(len(precipitation)), output_unit_1, color="blue", lw=2, label="Unit 1")
ax[1].plot(range(len(precipitation)), output_unit_2, color="red", lw=2, ls="--", label="Unit 2")

ax[2].plot(range(len(precipitation)), output, color="blue", lw=2, label="Outflow")

ax[0].set_ylabel("Precipitation [mm/day]")
ax[1].set_ylabel("Outflow [mm/day]")
ax[2].set_ylabel("Outflow [mm/day]")
ax[2].set_xlabel("Time [day]")
ax[1].set_title("Units")
ax[2].set_title("Node")

ax[1].legend()
ax[2].legend()

fig.savefig("pics/demo/SingleNode.png", res=600)

# %% Network
node_1.reset_states()
node_1.set_states({"node-1_unit-1_lag-fun_lag": None})  # Remove after new build

# Create other nodes
node_2 = Node(units=[unit_1, unit_2], weights=[0.3, 0.7], area=5.0, id="node-2")

node_3 = Node(units=[unit_2], weights=[1.0], area=3.0, id="node-3")

# Create the network
net = Network(nodes=[node_1, node_2, node_3], topology={"node-1": "node-3", "node-2": "node-3", "node-3": None})

node_1.set_input([precipitation])
node_2.set_input([precipitation * 0.5])
node_3.set_input([precipitation + 1.0])

net.set_timestep(1.0)

output = net.get_output()

output_unit_1_node_1 = net.call_internal(id="node-1_unit-1", method="get_output", solve=False)[0]

# Plotting
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

ax[0].bar(x=range(len(precipitation)), height=precipitation, color="blue")

ax[1].plot(range(len(precipitation)), output["node-1"][0], color="blue", lw=2, label="node-1")
ax[1].plot(range(len(precipitation)), output["node-2"][0], color="red", lw=2, label="node-2")
ax[1].plot(range(len(precipitation)), output["node-3"][0], color="orange", lw=2, label="node-3")

ax[0].set_ylabel("Precipitation [mm/day]")
ax[1].set_ylabel("Outflow [mm/day]")
ax[1].set_xlabel("Time [day]")

ax[1].legend()

fig.savefig("pics/demo/Network.png", res=600)
