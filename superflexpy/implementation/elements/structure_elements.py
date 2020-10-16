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

This file contains the implementation of some elements that are used to
complete the structure of the model.
"""

from copy import copy, deepcopy
from ...framework.element import BaseElement


class Splitter(BaseElement):
    """
    This class implements a Splitter. A Splitter is used to connect one element
    to multiple elements downstream.
    """

    _num_upstream = 1

    def __init__(self, weight, direction, id):
        """
        This is the initializer of the class Splitter.

        Parameters
        ----------
        weight : list(list(float))
            The weight defines the part (between 0 and 1) of a flux that goes
            into a down stream element. It is represented by a 2D array (list
            of lists) where the columns define the input flux and the rows the
            output element. Assuming there are 2 fluxes and 3 output elements,
            the weight can be [[a, b], [c, d], [e, f]] that means, for example,
            that the second input flux goes to the third element with weight f.
        direction : list(list(int))
            The direction defines where each input flux goes in the output
            elements. It is represented by a 2D array (list of lists) where the
            columns contain the index of the input flux to be taken for the
            output and the rows the output element. If one element is None it
            means that the input flux is not transfered to the output element.
            Assuming there are 2 fluxes and 3 output elements, the direction
            can be [[a, b], [c, d], [e, f]] that means, for example, that the
            second flux of the third output element is the one with index f in
            the input fluxes.
        id : str
            Itentifier of the element. All the elements of the framework must
            have an id.
        """

        BaseElement.__init__(self, id)
        self._direction = direction
        self._weight = weight
        self._num_downstream = len(weight)

    # METHODS FOR THE USER

    def set_weight(self, weight):
        """
        This method sets the weight of the element. See the documentation
        of the __init__ method for details.

        Parameters
        ----------
        weight : list
            Weight list.
        """
        self._weight = deepcopy(weight)

    def get_weight(self):
        """
        This method returns the weight of the element. See the documentation
        of the __init__ method for details.

        Returns
        -------
        list
            Weight list.
        """
        return deepcopy(self._weight)

    def set_input(self, input):
        """
        The method sets the input fluxes of the element.

        Parameters
        ----------
        input : list
            List of inputs of the element. The dimensionality depends on the
            element.
        """
        self.input = input

    def get_direction(self):
        """
        This method returns the direction of the element. See the documentation
        of the __init__ method for details.

        Returns
        -------
        list
            Direction list
        """
        return deepcopy(self._direction)

    def set_direction(self, direction):
        """
        This method sets the direction of the element. See the documentation
        of the __init__ method for details.

        Parameters
        ----------
        direction : list
            Define how to mix/split the fluxes
        """
        self._direction = deepcopy(direction)

    def get_output(self, solve=True):
        """
        This method returns the output of the splitter to the downstream
        elements.

        Returns
        -------
        list(list(numpy.ndarray))
            List of output fluxes. Each element of the external list goes to
            an element downstream
        """

        output = []

        for i in range(len(self._weight)):
            output.append([])
            for j in range(len(self._weight[i])):
                if self._direction[i][j] is None:
                    continue
                output[-1].append(self.input[self._direction[i][j]]
                                  * self._weight[i][self._direction[i][j]])

        return output

    # MAGIC METHODS

    def __copy__(self):
        w = deepcopy(self._weight)  # It is a 2D list -> I need to go deep
        d = deepcopy(self._direction)
        return self.__class__(weight=w,
                              direction=d,
                              id=self.id)

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'Weight:\n'
        str += '\t{}\n'.format(self._weight)
        str += 'Direction:\n'
        str += '\t{}\n'.format(self._direction)

        return str


class Junction(BaseElement):
    """
    This class implements a Junction. A Junction is used to connect multiple
    element to a single element downstream.
    """

    _num_downstream = 1

    def __init__(self, direction, id):
        """
        This is the initializer of the class Junction.

        Parameters
        ----------
        direction : list(list(int))
            The direction defines where each input flux goes in the output
            element. It is represented by a 2D array (list of lists) where the
            columns contain the index of the input flux to be taken for the
            output and the rows the output flux. If the flux is not present in
            the input element, its value in the direction is None. Assuming
            there are 2 fluxes and 3 input, the direction can be
            [[a, b, c], [d, e, f]] that means, for example, that the second
            output flux is the one with index f in the third input element.
        id : str
            id of the element
        """

        BaseElement.__init__(self, id)
        self._direction = direction
        self._num_upstream = len(direction[0])

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        The method sets the input fluxes of the element.

        Parameters
        ----------
        input : list
            List of inputs of the element. The dimensionality depends on the
            element.
        """
        self.input = input

    def get_direction(self):
        """
        This method returns the direction of the element. See the documentation
        of the __init__ method for details.

        Returns
        -------
        list
            Direction list
        """
        return deepcopy(self._direction)

    def set_direction(self, direction):
        """
        This method sets the direction of the element. See the documentation
        of the __init__ method for details.

        Parameters
        ----------
        direction : list
            Define how to mix/split the fluxes
        """
        self._direction = deepcopy(direction)

    def get_output(self, solve=True):
        """
        This method returns the output of the junction to the downstream
        element.

        Returns
        -------
        list(numpy.ndarray)
            List of output fluxes.
        """

        output = [0] * len(self._direction)

        for i in range(len(self._direction)):
            for j in range(len(self._direction[i])):
                if self._direction[i][j] is None:
                    continue

                output[i] += self.input[j][self._direction[i][j]]

        return output

    # MAGIC METHODS

    def __copy__(self):
        d = deepcopy(self._direction)
        return self.__class__(direction=d,
                              id=self.id)

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'Direction:\n'
        str += '\t{}\n'.format(self._direction)

        return str


class Linker(BaseElement):
    """
    This class implements a Linker. A Linker is used to connect multiple
    element in the cases where the paths cross. The Linker operates only on all
    the fluxes list and does not mix fluxes inside and element.
    """

    def __init__(self, direction, id):
        """
        This is the initializer of the class Linker.

        Parameters
        ----------
        direction : list(int)
            The direction defines the connections between upstream and
            downstream elements. It is represented by a list on integers where
            each value represent the index of the input element to output.
            Assuming that the linker connects 3 elements, if the direction is
            [a, b, c] it means that the second output element takes the fluxes
             coming from the input element in position b.
        id : str
            id of the element
        """

        BaseElement.__init__(self, id)
        self._direction = direction
        self._num_upstream = len(direction)
        self._num_downstream = len(direction)

    # METHODS FOR THE USER

    def get_direction(self):
        """
        This method returns the direction of the element. See the documentation
        of the __init__ method for details.

        Returns
        -------
        list
            Direction list
        """
        return deepcopy(self._direction)

    def set_direction(self, direction):
        """
        This method sets the direction of the element. See the documentation
        of the __init__ method for details.

        Parameters
        ----------
        direction : list
            Define how to mix/split the fluxes
        """
        self._direction = deepcopy(direction)

    def set_input(self, input):
        """
        The method sets the input fluxes of the element.

        Parameters
        ----------
        input : list
            List of inputs of the element. The dimensionality depends on the
            element.
        """
        self.input = input

    def get_output(self, solve=True):
        """
        This method returns the output of the linker to the downstream
        elements.

        Returns
        -------
        list(list(numpy.ndarray))
            List of output fluxes. Each element of the external list goes to
            an element downstream
        """

        output = []
        for i in range(len(self.input)):
            output.append(self.input[self._direction[i]])

        return output

    # MAGIC METHODS

    def __copy__(self):
        d = deepcopy(self._direction)
        return self.__class__(direction=d,
                              id=self.id)

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __repr__(self):
        str = 'Module: superflexPy\nElement: {}\n'.format(self.id)
        str += 'Direction:\n'
        str += '\t{}\n'.format(self._direction)

        return str


class Transparent(BaseElement):
    """
    This class implements a Transparent element. A Transparent element is used
    to fill gaps in the HRU structure. It just transfer the incoming fluxes to
    the output.
    """

    _num_upstream = 1
    _num_downstream = 1

    # METHODS FOR THE USER

    def set_input(self, input):
        """
        The method sets the input fluxes of the element.

        Parameters
        ----------
        input : list(numpy.ndarray)
            List of inputs of the element.
        """

        self.input = input

    def get_output(self, solve=True):
        """
        The method returns the output fluxes of the element.

        Returns
        ----------
        list(numpy.ndarray)
            List of outputs of the element.
        """
        return self.input
