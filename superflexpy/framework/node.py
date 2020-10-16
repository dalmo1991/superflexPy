"""
Copyright 2020 Marco Dal Molin et al.

This file is part of SuperflexPy.

SuperflexPy is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SuperflexPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with SuperflexPy. If not, see <https://www.gnu.org/licenses/>.

This file is part of the SuperflexPy modelling framework. For details about it,
visit the page https://superflexpy.readthedocs.io

CODED BY: Marco Dal Molin
DESIGNED BY: Marco Dal Molin, Fabrizio Fenicia, Dmitri Kavetski

This file contains the implementation of the Node class.
"""

from copy import copy, deepcopy
from ..utils.generic_component import GenericComponent
from .unit import Unit


class Node(GenericComponent):
    """
    This class defines a Node. A node can be part of a network and it is a
    collection of Units. It's task is to sum the outputs of the Units,
    applying, if present, a routing.
    """

    def __init__(self, units, weights, area, id, parameters=None, states=None, shared_parameters=True):
        """
        This is the initializer of the class Node.

        Parameters
        ----------
        units : list(superflexpy.framework.unit.Unit)
            List of Units contained in the Node.
        weights : list
            List of weights to be applied to the Units when putting together
            their outputs. The order must be the same used in the units list.
            If a weight is a list, then different fluxes coming from the same
            unit have a different weight.
        area : float
            Influence area of the node. It is the net value: if a node has
            other nodes upstream, their area is not counted.
        id : str
            Identifier of the node. All the nodes of the framework must have an
            identifier.
        shared_parameters : bool
            True if the parameters of the Units are shared among the different
            Nodes.
        """

        self.id = id

        self._error_message = 'module : superflexPy, Node : {},'.format(id)
        self._error_message += ' Error message : '

        # Handle local parameters and states
        if parameters is not None:
            self._local_parameters = parameters

        if states is not None:
            self._local_states = states
            self._init_local_states = deepcopy(states)

        self._content = []
        for h in units:
            if not isinstance(h, Unit):
                message = '{}units must be instance of the Unit class'.format(self._error_message)
                raise TypeError(message)
            if shared_parameters:
                self._content.append(copy(h))
            else:
                self._content.append(deepcopy(h))

        self.area = area
        self._content_pointer = {hru.id: i
                                 for i, hru in enumerate(self._content)}
        self._weights = deepcopy(weights)
        self.add_prefix_parameters(id, shared_parameters)
        self.add_prefix_states(id)

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        This method sets the inputs to the node.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of input fluxes.
        """

        self.input = input

    def get_output(self, solve=True):
        """
        This method solves the Node, solving each Unit and putting together
        their outputs according to the weight.

        Parameters
        ----------
        solve : bool
            True if the elements have to be solved (i.e. calculate the states).

        Returns
        -------
        list(numpy.ndarray)
            List containig the output fluxes of the node.
        """

        # Set the inputs
        for h in self._content:
            h.set_input(deepcopy(self.input))

        # Calculate output
        if isinstance(self._weights[0], float):
            for i, (h, w) in enumerate(zip(self._content, self._weights)):
                loc_out = h.get_output(solve)

                if i == 0:
                    output = [o * w for o in loc_out]
                else:
                    for j in range(len(output)):
                        output[j] += loc_out[j] * w
        else:
            for i, (h, w) in enumerate(zip(self._content, self._weights)):
                loc_out = h.get_output(solve)
                out_count = 0

                if i == 0:
                    output = []
                    for j in range(len(w)):
                        if w[j] is None:
                            output.append(0)
                        else:
                            output.append(loc_out[out_count] * w[j])
                            out_count += 1
                else:
                    for j in range(len(w)):
                        if w[j] is None:
                            continue
                        else:
                            output[j] += loc_out[out_count] * w[j]
                            out_count += 1

        return self._internal_routing(output)

    def get_internal(self, id, attribute):
        """
        This method allows to inspect attributes of the objects that belong to
        the node.

        Parameters
        ----------
        id : str
            Id of the object. If it is not a unit, it must contain the ids of
            the object containing it. If, for example it is an element, the id
            will be idUnit_idElement.
        attribute : str
            Name of the attribute to expose.

        Returns
        -------
        Unknown
            Attribute exposed
        """

        hru_num, ele = self._find_attribute_from_name(id)

        if ele:
            ele_id = id.split('_')[-1]
            return self._content[hru_num].get_internal(ele_id, attribute)
        else:
            try:
                method = getattr(self._content[hru_num], attribute)
                return method
            except AttributeError:
                message = '{}the attribute {} does not exist.'.format(self._error_message, attribute)
                raise AttributeError(message)

    def call_internal(self, id, method, **kwargs):
        """
        This method allows to call methods of the objects that belong to the
        node.

        Parameters
        ----------
        id : str
            Id of the object. If it is not a unit, it must contain the ids of
            the object containing it. If, for example it is an element, the id
            will be idUnit_idElement.
        method : str
            Name of the method to call.

        Returns
        -------
        Unknown
            Output of the called method.
        """
        hru_num, ele = self._find_attribute_from_name(id)

        if ele:
            ele_id = id.split('_')[-1]
            return self._content[hru_num].call_internal(ele_id, method, **kwargs)
        else:
            try:
                method = getattr(self._content[hru_num], method)
                return method(**kwargs)
            except AttributeError:
                message = '{}the method {} does not exist.'.format(self._error_message, method)
                raise AttributeError(message)

    # METHODS USED BY THE FRAMEWORK

    def add_prefix_parameters(self, id, shared_parameters):
        """
        This method adds the prefix to the parameters of the elements that are
        contained in the node.

        Parameters
        ----------
        id : str
            Prefix to add.
        """

        # Add prefix to local parameters
        if '_' in id:
            message = '{}The prefix cannot contain \'_\''.format(self._error_message)
            raise ValueError(message)

        if self._local_parameters:  # the following block runs only if the dictionary is not empty
            # Extract the prefixes in the parameters name
            splitted = list(self._local_parameters.keys())[0].split('_')

            if id not in splitted:
                # Apply the prefix
                for k in list(self._local_parameters.keys()):
                    value = self._local_parameters.pop(k)
                    self._local_parameters['{}_{}'.format(id, k)] = value

                # Save the prefix for furure uses
                self._prefix_local_parameters = '{}_{}'.format(id, self._prefix_local_parameters)

        if not shared_parameters:
            for h in self._content:
                h.add_prefix_parameters(id)

    def add_prefix_states(self, id):
        """
        This method adds the prefix to the states of the elements that are
        contained in the node.

        Parameters
        ----------
        id : str
            Prefix to add.
        """

        # Add prefix to local states
        if '_' in id:
            message = '{}The prefix cannot contain \'_\''.format(self._error_message)
            raise ValueError(message)

        if self._local_states:  # the following block runs only if the dictionary is not empty
            # Extract the prefixes in the parameters name
            splitted = list(self._local_states.keys())[0].split('_')

            if id not in splitted:
                # Apply the prefix
                for k in list(self._local_states.keys()):
                    value = self._local_states.pop(k)
                    self._local_states['{}_{}'.format(id, k)] = value
                    value = self._init_local_states.pop(k)
                    self._init_local_states['{}_{}'.format(id, k)] = value

                # Save the prefix for furure uses
                self._prefix_local_states = '{}_{}'.format(id, self._prefix_local_states)

        for h in self._content:
            h.add_prefix_states(id)

    def external_routing(self, flux):
        """
        This methods applies the external routing to the fluxes. External
        routing is the one that affects the fluxes moving from the outflow of
        this node to the outflow of the one downstream. This function is used
        by the Network.

        Parameters
        ----------
        flux : list(numpy.ndarray)
            List of fluxes on which the routing has to be applied.
        """

        # No routing
        return flux

    # PROTECTED METHODS

    def _find_attribute_from_name(self, id):
        """
        This method is used to find the attributes or methods of the components
        contained for post-run inspection.

        Parameters
        ----------
        id : str
            Identifier of the component

        Returns
        -------
        int, bool
            Index of the component to look for and indication if it is an
            element (True) or not.
        """

        splitted = id.split('_')

        hru_num = self._find_content_from_name(id)

        if len(splitted) == 2:
            return (hru_num, True)  # We are looking for an element
        elif len(splitted) == 1:
            return (hru_num, False)  # We are looking for a unit
        else:
            raise ValueError('Tmp for debug in node')

    def _internal_routing(self, flux):
        """
        Internal routing is the one that affects the flux coming to the Units
        and reaching the outflow of the node. This function is internally
        used by the node.
        """

        # No routing
        return flux

    # MAGIC METHODS

    def __copy__(self):
        message = '{}A Node cannot be copied'.format(self._error_message)
        raise AttributeError(message)

    def __deepcopy__(self, memo):
        message = '{}A Node cannot be copied'.format(self._error_message)
        raise AttributeError(message)

    def __repr__(self):
        str = 'Module: superflexPy\nNode: {}\n'.format(self.id)
        str += 'Units:\n'
        str += '\t{}\n'.format([h.id for h in self._content])
        str += 'Weights:\n'
        str += '\t{}\n'.format(self._weights)

        for h in self._content:
            str += '********************\n'
            str += '********************\n'
            str += h.__repr__()
            str += '\n'

        return str
