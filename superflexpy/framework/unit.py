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

This file contains the implementation of the Unit class.
"""

from copy import copy, deepcopy
from ..utils.generic_component import GenericComponent


class Unit(GenericComponent):
    """
    This class defines a Unit. A unit can be part of a node and it is a
    collection of elements. It's task is to build the basic structure,
    connecting different elements. Mathematically, it is a directed acyclic
    graph.
    """

    def __init__(self, layers, id, parameters=None, states=None, copy_pars=True):
        """
        This is the initializer of the class Unit.

        Parameters
        ----------
        layers : list(list(superflexpy.framework.element.BaseElement))
            This list defines the structure of the unit. The elements are
            arranged in layers (upstream to downstream) and each layer can
            contain multiple elements.
        id : str
            Identifier of the unit. All the units of the framework must have an
            identifier.
        copy_pars : bool
            True if the parameters of the elements are copied instead of being
            shared among the different Units.
        """

        self._error_message = 'module : superflexPy, Unit : {},'.format(id)
        self._error_message += ' Error message : '

        # Handle local parameters and states
        if parameters is not None:
            self._local_parameters = parameters

        if states is not None:
            self._local_states = states
            self._init_local_states = deepcopy(states)

        if copy_pars:
            # Deep-copy the elements
            self._layers = []
            for l in layers:
                self._layers.append([])
                for el in l:
                    self._layers[-1].append(deepcopy(el))
        else:
            self._layers = layers

        self.id = id

        self._check_layers()
        self.add_prefix_parameters(id)
        self.add_prefix_states(id)
        self._construct_dictionary()

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        This method sets the inputs to the unit.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of input fluxes.
        """

        self.input = input

    def get_output(self, solve=True):
        """
        This method solves the Unit, solving each Element and putting together
        their outputs according to the structure.

        Parameters
        ----------
        solve : bool
            True if the elements have to be solved (i.e. calculate the states).

        Returns
        -------
        list(numpy.ndarray)
            List containing the output fluxes of the unit.
        """

        # Set the first layer (it must have 1 element)
        self._layers[0][0].set_input(self.input)

        for i in range(1, len(self._layers)):
            # Collect the outputs
            outputs = []
            for el in self._layers[i - 1]:
                if el.num_downstream == 1:
                    outputs.append(el.get_output(solve))
                else:
                    loc_out = el.get_output(solve)
                    for o in loc_out:
                        outputs.append(o)

            # Fill the inputs
            ind = 0
            for el in self._layers[i]:
                if el.num_upstream == 1:
                    el.set_input(outputs[ind])
                    ind += 1
                else:
                    loc_in = []
                    for _ in range(el.num_upstream):
                        loc_in.append(outputs[ind])
                        ind += 1
                    el.set_input(loc_in)

        # Return the output of the last element
        return self._layers[-1][0].get_output(solve)

    def append_layer(self, layer):
        """
        This method appends a layer to the structure.

        Parameters
        ----------
        layer : list(superflexpy.framework.elements.BaseElement)
            Layer to be appended.
        """

        self.insert_layer(layer, position=len(self._layers))

    def insert_layer(self, layer, position):
        """
        This method inserts a layer in the unit structure.

        Parameters
        ----------
        layer : list(superflexpy.framework.elements.BaseElement)
            Layer to be inserted.
        position : int
            Position where the layer is inserted.
        """

        layer_loc = []
        for el in layer:
            layer_loc.append(deepcopy(el))

        self._layers.insert(position, layer_loc)
        self._construct_dictionary()
        self._check_layers()

    # def parse_structure(self, structure):
    #     raise NotImplementedError('Functionality in the TODO list')

    def get_internal(self, id, attribute):
        """
        This method allows to inspect attributes of the objects that belong to
        the unit.

        Parameters
        ----------
        id : str
            Id of the object.
        attribute : str
            Name of the attribute to expose.

        Returns
        -------
        Unknown
            Attribute exposed
        """

        return self._find_attribute_from_name(id, attribute)

    def call_internal(self, id, method, **kwargs):
        """
        This method allows to call methods of the objects that belong to the
        unit.

        Parameters
        ----------
        id : str
            Id of the object.
        method : str
            Name of the method to call.

        Returns
        -------
        Unknown
            Output of the called method.
        """

        method = self._find_attribute_from_name(id, method)
        return method(**kwargs)

    # METHODS USED BY THE FRAMEWORK

    def add_prefix_parameters(self, id):
        """
        This method adds the prefix to the parameters of the elements that are
        contained in the unit.

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

        for l in self._layers:
            for el in l:
                try:
                    el.add_prefix_parameters(id)
                except AttributeError:
                    continue

    def add_prefix_states(self, id):
        """
        This method adds the prefix to the states of the elements that are
        contained in the unit.

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

        # add the Prefix to the elements
        for l in self._layers:
            for el in l:
                try:
                    el.add_prefix_states(id)
                except AttributeError:
                    continue

    # PROTECTED METHODS

    def _construct_dictionary(self):
        """
        This method populates the self._content_pointer dictionary.
        """

        self._content_pointer = {}

        for i in range(len(self._layers)):
            for j in range(len(self._layers[i])):
                if self._layers[i][j].id in self._content_pointer:
                    message = '{}The element {} already exist.'.format(self._error_message, self._layers[i][j].id)
                    raise KeyError(message)
                self._content_pointer[self._layers[i][j].id] = (i, j)

        self._content = {}
        for k in self._content_pointer.keys():
            l, el = self._content_pointer[k]
            self._content[(l, el)] = self._layers[l][el]

    def _find_attribute_from_name(self, id, function):
        """
        This method is used to find the attributes or methods of the components
        contained for post-run inspection.

        Parameters
        ----------
        id : str
            Identifier of the component
        function : str
            Name of the attribute or method

        Returns
        -------
        Unknown
            Attribute or method to inspect
        """

        # Search the element
        (l, el) = self._find_content_from_name(id)
        element = self._layers[l][el]

        # Call the function on the element
        try:
            method = getattr(element, function)
        except AttributeError:
            message = '{}the method {} does not exist.'.format(self._error_message, function)
            raise AttributeError(message)

        return method

    def _check_layers(self):
        """
        This method controls if the layers respect all the rules in terms of
        number of upstream/downstream elements.
        """

        # Check layer 0
        if len(self._layers[0]) != 1:
            message = '{}layer 0 has {} elements.'.format(self._error_message, len(self._layers[0]))
            raise ValueError(message)

        if self._layers[0][0].num_upstream != 1:
            message = '{}The element in layer 0 has {} upstream elements.'.format(self._error_message, len(self._layers[0][0].num_upstream))
            raise ValueError(message)

        # Check the other layers
        for i in range(1, len(self._layers)):
            num_upstream = 0
            num_downstream = 0
            for el in self._layers[i - 1]:
                num_downstream += el.num_downstream
            for el in self._layers[i]:
                num_upstream += el.num_upstream

            if num_downstream != num_upstream:
                message = '{}Downstream : {}, Upstream : {}'.format(self._error_message, num_downstream, num_upstream)
                raise ValueError(message)

        # Check last layer
        if len(self._layers[-1]) != 1:
            message = '{}last layer has {} elements.'.format(self._error_message, len(self._layers[-1]))
            raise ValueError(message)

        if self._layers[-1][0].num_downstream != 1:
            message = '{}The element in the last layer has {} downstream elements.'.format(self._error_message, len(self._layers[-1][0].num_downstream))
            raise ValueError(message)

    # MAGIC METHODS

    def __copy__(self):
        layers = []
        for l in self._layers:
            layers.append([])
            for el in l:
                layers[-1].append(copy(el))

        p = self._local_parameters
        s = deepcopy(self._local_states)

        unit = self.__class__(layers=layers,
                              id=self.id,
                              parameters=p,
                              states=s,
                              copy_pars=False)  # False because the copy is customized here
        unit._prefix_local_parameters = self._prefix_local_parameters
        unit._prefix_local_states = self._prefix_local_states

        return unit

    def __deepcopy__(self, memo):

        p = deepcopy(self._local_parameters)
        s = deepcopy(self._local_states)

        unit = self.__class__(layers=self._layers,
                              id=self.id,
                              parameters=p,
                              states=s,
                              copy_pars=True)  # init already implements deepcopy
        unit._prefix_local_parameters = self._prefix_local_parameters
        unit._prefix_local_states = self._prefix_local_states

        return unit

    def __repr__(self):
        str = 'Module: superflexPy\nUnit: {}\n'.format(self.id)
        str += 'Layers:\n'
        id_layer = []
        for l in self._layers:
            id_layer.append([])
            for el in l:
                id_layer[-1].append(el.id)

        str += '\t{}\n'.format(id_layer)

        for l in self._layers:
            for el in l:
                str += '********************\n'
                str += el.__repr__()
                str += '\n'

        return str
