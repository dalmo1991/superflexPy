"""
This code is copy-pasted from the original implementation in the superflexpy.
This copy is done to avoid that minor changes in the code (e.g. new lines)
are reflected in the documentation.

THE PRESENT CODE IS NOT SUPPOSED TO BE RUN: import are omitted it order to
make the code crash in case someone runs it
"""


class InterceptionFilter(BaseElement):
    _num_upstream = 1
    _num_downstream = 1

    def set_input(self, input):
        self.input = {}
        self.input["PET"] = input[0]
        self.input["P"] = input[1]

    def get_output(self, solve=True):
        remove = np.minimum(self.input["PET"], self.input["P"])

        return [self.input["PET"] - remove, self.input["P"] - remove]


class ProductionStore(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._flux_function_python]

        if approximation.architecture == "numba":
            self._fluxes = [self._flux_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._flux_function_python]

    def set_input(self, input):
        self.input = {}
        self.input["PET"] = input[0]
        self.input["P"] = input[1]

    def get_output(self, solve=True):
        if solve:
            # Solve the differential equation
            self._solver_states = [self._states[self._prefix_states + "S0"]]
            self._solve_differential_equation()

            # Update the states
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )

        Pn_minus_Ps = self.input["P"] - fluxes[0][0]
        Perc = -fluxes[0][2]
        return [Pn_minus_Ps + Perc]

    def get_aet(self):
        try:
            S = self.state_array
        except AttributeError:
            message = "{}get_aet method has to be run after running ".format(self._error_message)
            message += "the model using the method get_output"
            raise AttributeError(message)

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=S,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )

        return [-fluxes[0][1]]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):
        if ind is None:
            return (
                [
                    P * (1 - (S / x1) ** alpha),  # Ps
                    -PET * (2 * (S / x1) - (S / x1) ** alpha),  # Evaporation
                    -((x1 ** (1 - beta)) / ((beta - 1))) * (ni ** (beta - 1)) * (S**beta),  # Perc
                ],
                0.0,
                S0 + P * (1 - (S / x1) ** alpha) * dt,
            )
        else:
            return (
                [
                    P[ind] * (1 - (S / x1[ind]) ** alpha[ind]),  # Ps
                    -PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind]) ** alpha[ind]),  # Evaporation
                    -((x1[ind] ** (1 - beta[ind])) / ((beta[ind] - 1)))
                    * (ni[ind] ** (beta[ind] - 1))
                    * (S ** beta[ind]),  # Perc
                ],
                0.0,
                S0 + P[ind] * (1 - (S / x1[ind]) ** alpha[ind]) * dt[ind],
                [
                    -(P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind]) ** (alpha[ind] - 1)),
                    -(PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind]) ** (alpha[ind] - 1))),
                    -beta[ind]
                    * ((x1[ind] ** (1 - beta[ind])) / ((beta[ind] - 1) * dt[ind]))
                    * (ni[ind] ** (beta[ind] - 1))
                    * (S ** (beta[ind] - 1)),
                ],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])",
        nopython=True,
    )
    def _flux_function_numba(S, S0, ind, P, x1, alpha, beta, ni, PET, dt):
        return (
            (
                P[ind] * (1 - (S / x1[ind]) ** alpha[ind]),  # Ps
                -PET[ind] * (2 * (S / x1[ind]) - (S / x1[ind]) ** alpha[ind]),  # Evaporation
                -((x1[ind] ** (1 - beta[ind])) / ((beta[ind] - 1)))
                * (ni[ind] ** (beta[ind] - 1))
                * (S ** beta[ind]),  # Perc
            ),
            0.0,
            S0 + P[ind] * (1 - (S / x1[ind]) ** alpha[ind]) * dt[ind],
            (
                -(P[ind] * alpha[ind] / x1[ind]) * ((S / x1[ind]) ** (alpha[ind] - 1)),
                -(PET[ind] / x1[ind]) * (2 - alpha[ind] * ((S / x1[ind]) ** (alpha[ind] - 1))),
                -beta[ind]
                * ((x1[ind] ** (1 - beta[ind])) / ((beta[ind] - 1) * dt[ind]))
                * (ni[ind] ** (beta[ind] - 1))
                * (S ** (beta[ind] - 1)),
            ),
        )


class RoutingStore(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._flux_function_python]

        if approximation.architecture == "numba":
            self._fluxes = [self._flux_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._flux_function_python]

    def set_input(self, input):
        self.input = {}
        self.input["P"] = input[0]

    def get_output(self, solve=True):
        if solve:
            # Solve the differential equation
            self._solver_states = [self._states[self._prefix_states + "S0"]]
            self._solve_differential_equation()

            # Update the states
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )

        Qr = -fluxes[0][1]
        F = -fluxes[0][2]

        return [Qr, F]

    @staticmethod
    def _flux_function_python(S, S0, ind, P, x2, x3, gamma, omega, dt):
        if ind is None:
            return (
                [
                    P,  # P
                    -((x3 ** (1 - gamma)) / ((gamma - 1))) * (S**gamma),  # Qr
                    -(x2 * (S / x3) ** omega),  # F
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],  # P
                    -((x3[ind] ** (1 - gamma[ind])) / ((gamma[ind] - 1))) * (S ** gamma[ind]),  # Qr
                    -(x2[ind] * (S / x3[ind]) ** omega[ind]),  # F
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [
                    0.0,
                    -((x3[ind] ** (1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind]))
                    * (S ** (gamma[ind] - 1))
                    * gamma[ind],
                    -(omega[ind] * x2[ind] * ((S / x3[ind]) ** (omega[ind] - 1))),
                ],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])",
        nopython=True,
    )
    def _flux_function_numba(S, S0, ind, P, x2, x3, gamma, omega, dt):
        return (
            (
                P[ind],  # P
                -((x3[ind] ** (1 - gamma[ind])) / ((gamma[ind] - 1))) * (S ** gamma[ind]),  # Qr
                -(x2[ind] * (S / x3[ind]) ** omega[ind]),  # F
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (
                0.0,
                -((x3[ind] ** (1 - gamma[ind])) / ((gamma[ind] - 1) * dt[ind])) * (S ** (gamma[ind] - 1)) * gamma[ind],
                -(omega[ind] * x2[ind] * ((S / x3[ind]) ** (omega[ind] - 1))),
            ),
        )


class FluxAggregator(BaseElement):
    _num_downstream = 1
    _num_upstream = 1

    def set_input(self, input):
        self.input = {}
        self.input["Qr"] = input[0]
        self.input["F"] = input[1]
        self.input["Q2_out"] = input[2]

    def get_output(self, solve=True):
        return [self.input["Qr"] + np.maximum(0, self.input["Q2_out"] - self.input["F"])]


class UnitHydrograph1(LagElement):
    def __init__(self, parameters, states, id):
        LagElement.__init__(self, parameters, states, id)

    def _build_weight(self, lag_time):
        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []
            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t) - self._calculate_lag_area(i, t))
            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        if bin <= 0:
            value = 0
        elif bin < len:
            value = (bin / len) ** 2.5
        else:
            value = 1
        return value


class UnitHydrograph2(LagElement):
    def __init__(self, parameters, states, id):
        LagElement.__init__(self, parameters, states, id)

    def _build_weight(self, lag_time):
        weight = []

        for t in lag_time:
            array_length = np.ceil(t)
            w_i = []
            for i in range(int(array_length)):
                w_i.append(self._calculate_lag_area(i + 1, t) - self._calculate_lag_area(i, t))
            weight.append(np.array(w_i))

        return weight

    @staticmethod
    def _calculate_lag_area(bin, len):
        half_len = len / 2
        if bin <= 0:
            value = 0
        elif bin < half_len:
            value = 0.5 * (bin / half_len) ** 2.5
        elif bin < len:
            value = 1 - 0.5 * (2 - bin / half_len) ** 2.5
        else:
            value = 1
        return value


x1, x2, x3, x4 = (50.0, 0.1, 20.0, 3.5)

root_finder = PegasusPython()  # Use the default parameters
numerical_approximation = ImplicitEulerPython(root_finder)

interception_filter = InterceptionFilter(id="ir")

production_store = ProductionStore(
    parameters={"x1": x1, "alpha": 2.0, "beta": 5.0, "ni": 4 / 9},
    states={"S0": 10.0},
    approximation=numerical_approximation,
    id="ps",
)

splitter = Splitter(weight=[[0.9], [0.1]], direction=[[0], [0]], id="spl")

unit_hydrograph_1 = UnitHydrograph1(parameters={"lag-time": x4}, states={"lag": None}, id="uh1")

unit_hydrograph_2 = UnitHydrograph2(parameters={"lag-time": 2 * x4}, states={"lag": None}, id="uh2")

routing_store = RoutingStore(
    parameters={"x2": x2, "x3": x3, "gamma": 5.0, "omega": 3.5},
    states={"S0": 10.0},
    approximation=numerical_approximation,
    id="rs",
)

transparent = Transparent(id="tr")

junction = Junction(
    direction=[[0, None], [1, None], [None, 0]], id="jun"  # First output  # Second output  # Third output
)

flux_aggregator = FluxAggregator(id="fa")

model = Unit(
    layers=[
        [interception_filter],
        [production_store],
        [splitter],
        [unit_hydrograph_1, unit_hydrograph_2],
        [routing_store, transparent],
        [junction],
        [flux_aggregator],
    ],
    id="model",
)


## HyMod


class UpperZone(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._fluxes_function_python]

        if approximation.architecture == "numba":
            self._fluxes = [self._fluxes_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._fluxes_function_python]

    def set_input(self, input):
        self.input = {"P": input[0], "PET": input[1]}

    def get_output(self, solve=True):
        if solve:
            self._solver_states = [self._states[self._prefix_states + "S0"]]

            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][2]]

    def get_AET(self):
        try:
            S = self.state_array
        except AttributeError:
            message = "{}get_aet method has to be run after running ".format(self._error_message)
            message += "the model using the method get_output"
            raise AttributeError(message)

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=S,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][1]]

    # PROTECTED METHODS

    @staticmethod
    def _fluxes_function_python(S, S0, ind, P, Smax, m, beta, PET, dt):
        if ind is None:
            return (
                [
                    P,
                    -PET * ((S / Smax) * (1 + m)) / ((S / Smax) + m),
                    -P * (1 - (1 - (S / Smax)) ** beta),
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],
                    -PET[ind] * ((S / Smax[ind]) * (1 + m[ind])) / ((S / Smax[ind]) + m[ind]),
                    -P[ind] * (1 - (1 - (S / Smax[ind])) ** beta[ind]),
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [
                    0.0,
                    -PET[ind] * m[ind] * Smax[ind] * (1 + m[ind]) / ((S + Smax[ind] * m[ind]) ** 2),
                    -P[ind] * beta[ind] * ((1 - (S / Smax[ind])) ** (beta[ind] - 1)) / Smax[ind],
                ],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])",
        nopython=True,
    )
    def _fluxes_function_numba(S, S0, ind, P, Smax, m, beta, PET, dt):
        return (
            (
                P[ind],
                -PET[ind] * ((S / Smax[ind]) * (1 + m[ind])) / ((S / Smax[ind]) + m[ind]),
                -P[ind] * (1 - (1 - (S / Smax[ind])) ** beta[ind]),
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (
                0.0,
                -PET[ind] * m[ind] * Smax[ind] * (1 + m[ind]) / ((S + Smax[ind] * m[ind]) ** 2),
                -P[ind] * beta[ind] * ((1 - (S / Smax[ind])) ** (beta[ind] - 1)) / Smax[ind],
            ),
        )


class LinearReservoir(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._fluxes_function_python]  # Used by get fluxes, regardless of the architecture

        if approximation.architecture == "numba":
            self._fluxes = [self._fluxes_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._fluxes_function_python]

    # METHODS FOR THE USER

    def set_input(self, input):
        self.input = {"P": input[0]}

    def get_output(self, solve=True):
        if solve:
            self._solver_states = [self._states[self._prefix_states + "S0"]]
            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,  # I can use the python method since it is fast
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][1]]

    # PROTECTED METHODS

    @staticmethod
    def _fluxes_function_python(S, S0, ind, P, k, dt):
        if ind is None:
            return (
                [
                    P,
                    -k * S,
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],
                    -k[ind] * S,
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [0.0, -k[ind]],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 2), f8, f8, UniTuple(f8, 2)))(optional(f8), f8, i4, f8[:], f8[:], f8[:])", nopython=True
    )
    def _fluxes_function_numba(S, S0, ind, P, k, dt):
        return (
            (
                P[ind],
                -k[ind] * S,
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (0.0, -k[ind]),
        )


root_finder = PegasusPython()  # Use the default parameters
numerical_approximation = ImplicitEulerPython(root_finder)

upper_zone = UpperZone(
    parameters={"Smax": 50.0, "m": 0.01, "beta": 2.0},
    states={"S0": 10.0},
    approximation=numerical_approximation,
    id="uz",
)

splitter = Splitter(weight=[[0.6], [0.4]], direction=[[0], [0]], id="spl")

channel_routing_1 = LinearReservoir(
    parameters={"k": 0.1}, states={"S0": 10.0}, approximation=numerical_approximation, id="cr1"
)

channel_routing_2 = LinearReservoir(
    parameters={"k": 0.1}, states={"S0": 10.0}, approximation=numerical_approximation, id="cr2"
)

channel_routing_3 = LinearReservoir(
    parameters={"k": 0.1}, states={"S0": 10.0}, approximation=numerical_approximation, id="cr3"
)

lower_zone = LinearReservoir(parameters={"k": 0.1}, states={"S0": 10.0}, approximation=numerical_approximation, id="lz")

transparent_1 = Transparent(id="tr1")

transparent_2 = Transparent(id="tr2")

junction = Junction(direction=[[0, 0]], id="jun")  # First output

model = Unit(
    layers=[
        [upper_zone],
        [splitter],
        [channel_routing_1, lower_zone],
        [channel_routing_2, transparent_1],
        [channel_routing_3, transparent_2],
        [junction],
    ],
    id="model",
)


# M4
class UnsaturatedReservoir(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._fluxes_function_python]

        if approximation.architecture == "numba":
            self._fluxes = [self._fluxes_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._fluxes_function_python]

    def set_input(self, input):
        self.input = {"P": input[0], "PET": input[1]}

    def get_output(self, solve=True):
        if solve:
            self._solver_states = [self._states[self._prefix_states + "S0"]]

            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][2]]

    def get_AET(self):
        try:
            S = self.state_array
        except AttributeError:
            message = "{}get_aet method has to be run after running ".format(self._error_message)
            message += "the model using the method get_output"
            raise AttributeError(message)

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,
            S=S,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )
        return [-fluxes[0][1]]

    # PROTECTED METHODS

    @staticmethod
    def _fluxes_function_python(S, S0, ind, P, Smax, m, beta, PET, dt):
        if ind is None:
            return (
                [
                    P,
                    -PET * ((S / Smax) * (1 + m)) / ((S / Smax) + m),
                    -P * (S / Smax) ** beta,
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],
                    -PET[ind] * ((S / Smax[ind]) * (1 + m[ind])) / ((S / Smax[ind]) + m[ind]),
                    -P[ind] * (S / Smax[ind]) ** beta[ind],
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [
                    0.0,
                    -(Ce[ind] * PET[ind] * m[ind] * (m[ind] + 1) * Smax[ind]) / ((S + m[ind] * Smax[ind]) ** 2),
                    -(P[ind] * beta[ind] / Smax[ind]) * (S / Smax[ind]) ** (beta[ind] - 1),
                ],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 3), f8, f8, UniTuple(f8, 3)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:], f8[:], f8[:])",
        nopython=True,
    )
    def _fluxes_function_numba(S, S0, ind, P, Smax, m, beta, PET, dt):
        return (
            (
                P[ind],
                PET[ind] * ((S / Smax[ind]) * (1 + m[ind])) / ((S / Smax[ind]) + m[ind]),
                -P[ind] * (S / Smax[ind]) ** beta[ind],
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (
                0.0,
                -(Ce[ind] * PET[ind] * m[ind] * (m[ind] + 1) * Smax[ind]) / ((S + m[ind] * Smax[ind]) ** 2),
                -(P[ind] * beta[ind] / Smax[ind]) * (S / Smax[ind]) ** (beta[ind] - 1),
            ),
        )


class PowerReservoir(ODEsElement):
    def __init__(self, parameters, states, approximation, id):
        ODEsElement.__init__(self, parameters=parameters, states=states, approximation=approximation, id=id)

        self._fluxes_python = [self._fluxes_function_python]  # Used by get fluxes, regardless of the architecture

        if approximation.architecture == "numba":
            self._fluxes = [self._fluxes_function_numba]
        elif approximation.architecture == "python":
            self._fluxes = [self._fluxes_function_python]

    # METHODS FOR THE USER

    def set_input(self, input):
        self.input = {"P": input[0]}

    def get_output(self, solve=True):
        if solve:
            self._solver_states = [self._states[self._prefix_states + "S0"]]
            self._solve_differential_equation()

            # Update the state
            self.set_states({self._prefix_states + "S0": self.state_array[-1, 0]})

        fluxes = self._num_app.get_fluxes(
            fluxes=self._fluxes_python,  # I can use the python method since it is fast
            S=self.state_array,
            S0=self._solver_states,
            dt=self._dt,
            **self.input,
            **{k[len(self._prefix_parameters) :]: self._parameters[k] for k in self._parameters},
        )

        return [-fluxes[0][1]]

    # PROTECTED METHODS

    @staticmethod
    def _fluxes_function_python(S, S0, ind, P, k, alpha, dt):
        if ind is None:
            return (
                [
                    P,
                    -k * S**alpha,
                ],
                0.0,
                S0 + P * dt,
            )
        else:
            return (
                [
                    P[ind],
                    -k[ind] * S ** alpha[ind],
                ],
                0.0,
                S0 + P[ind] * dt[ind],
                [0.0, -k[ind] * alpha[ind] * S ** (alpha[ind] - 1)],
            )

    @staticmethod
    @nb.jit(
        "Tuple((UniTuple(f8, 2), f8, f8, UniTuple(f8, 2)))(optional(f8), f8, i4, f8[:], f8[:], f8[:], f8[:])",
        nopython=True,
    )
    def _fluxes_function_numba(S, S0, ind, P, k, alpha, dt):
        return (
            (
                P[ind],
                -k[ind] * S ** alpha[ind],
            ),
            0.0,
            S0 + P[ind] * dt[ind],
            (0.0, -k[ind] * alpha[ind] * S ** (alpha[ind] - 1)),
        )


root_finder = PegasusPython()
numeric_approximator = ImplicitEulerPython(root_finder=root_finder)

ur = UnsaturatedReservoir(
    parameters={"Smax": 50.0, "Ce": 1.0, "m": 0.01, "beta": 2.0},
    states={"S0": 25.0},
    approximation=numeric_approximator,
    id="UR",
)

fr = PowerReservoir(
    parameters={"k": 0.1, "alpha": 1.0}, states={"S0": 10.0}, approximation=numeric_approximator, id="FR"
)

model = Unit(layers=[[ur], [fr]], id="M4")
