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

This file contains the implementation of a class that implements methods that
are useful for Unit, Node, and Network.
"""


class GenericComponent(object):
    """
    This is the abstract class for the creation of the components Unit, Node,
    and Network. It defines a series of methods that are common among the
    components.
    """

    _content_pointer = {}
    """
    Dictionary that maps the id of the components to their location
    """

    _content = []  # Note that it can also be a dictionary
    """
    List (or dictionary) of the component contained
    """

    _local_parameters = {}
    """
    Dictionary that contains the parameters that are specific to the component
    """

    _local_states = {}
    """
    Dictionary that contains the states that are specific to the component
    """

    _init_local_states = {}
    """
    Dictionary that contains the value of the states, which that are specific
    to the component, at initialization.
    """

    _prefix_local_parameters = ''
    """
    Prefix applied to local parameters
    """

    _prefix_local_states = ''
    """
    Prefix applied to local states
    """

    def get_parameters(self, names=None):
        """
        This method returns the parameters of the component and of the ones
        contained.

        Parameters
        ----------
        names : list(str)
            Names of the parameters to return. The names must be the ones
            returned by the method get_parameters_name. If None, all the
            parameters are returned.

        Returns
        -------
        dict:
            Parameters of the element.
        """

        parameters = {}

        if names is None:
            # Add local parameters
            for k in self._local_parameters.keys():
                parameters[k] = self._local_parameters[k]

            for c in self._content_pointer.keys():
                position = self._content_pointer[c]
                try:
                    cont_pars = self._content[position].get_parameters()
                except AttributeError:
                    continue
                for k in cont_pars:
                    if k not in parameters:
                        parameters[k] = cont_pars[k]
        else:
            for n in names:
                position = self._find_content_from_name(n)
                if position is None:
                    for c in self._content_pointer.keys():
                        position = self._content_pointer[c]
                        try:
                            cont_pars = self._content[position].get_parameters([n])
                            break
                        except (AttributeError, KeyError):  # Attribute error because the content may not have the method, Key error because the parameter may not belong to the content
                            continue
                elif position == -1:  # it means local
                    cont_pars = {n: self._local_parameters[n]}
                else:
                    cont_pars = self._content[position].get_parameters([n])

                parameters = {**parameters, **cont_pars}

        return parameters

    def get_parameters_name(self):
        """
        This method returns the names of the parameters of the component and of
        the ones contained.

        Returns
        -------
        list(str):
            List with the names of the parameters.
        """

        return list(self.get_parameters().keys())

    def _find_content_from_name(self, name):
        """
        This method finds a component using the name of the parameter or the
        state.

        Parameters
        ----------
        name : str
            Name to use for the search

        Returns
        -------
        int or tuple
            Index of the component in self._content
        """

        splitted_name = name.split('_')

        try:
            class_id = self.id
        except AttributeError:  # We are in a Model
            class_id = None

        if class_id is not None:
            if class_id in splitted_name:
                if (len(splitted_name) - splitted_name.index(class_id)) == 2:  # It is a local parameter
                    position = -1
                else:
                    # HRU or Catchment
                    ind = splitted_name.index(class_id)
                    position = self._content_pointer[splitted_name[ind + 1]]
            else:
                position = self._content_pointer[splitted_name[0]]
        else:
            # Network. The network doesn't have local parameters
            for c in self._content_pointer.keys():
                if c in splitted_name:
                    position = self._content_pointer[c]
                    break
                else:
                    position = None

        return position

    def set_parameters(self, parameters):
        """
        This method sets the values of the parameters.

        Parameters
        ----------
        parameters : dict
            Contains the parameters of the element to be set. The keys must be
            the ones returned by the method get_parameters_name. Only the
            parameters that have to be changed should be passed.
        """

        for p in parameters.keys():
            position = self._find_content_from_name(p)

            if position is None:
                for c in self._content_pointer.keys():
                    try:
                        position = self._content_pointer[c]
                        self._content[position].set_parameters({p: parameters[p]})
                        break
                    except (KeyError, ValueError):
                        continue
            elif position == -1:
                self._local_parameters[p] = parameters[p]
            else:
                self._content[position].set_parameters({p: parameters[p]})

    def get_states(self, names=None):
        """
        This method returns the states of the component and of the ones
        contained.

        Parameters
        ----------
        names : list(str)
            Names of the states to return. The names must be the ones
            returned by the method get_states_name. If None, all the
            states are returned.

        Returns
        -------
        dict:
            States of the element.
        """

        states = {}

        if names is None:
            # Add local states
            for k in self._local_states.keys():
                states[k] = self._local_states[k]
            for c in self._content_pointer.keys():
                position = self._content_pointer[c]
                try:
                    cont_st = self._content[position].get_states()
                except AttributeError:
                    continue
                for k in cont_st:
                    if k not in states:
                        states[k] = cont_st[k]
        else:
            for n in names:
                position = self._find_content_from_name(n)
                if position is None:
                    for c in self._content_pointer.keys():
                        position = self._content_pointer[c]
                        try:
                            cont_st = self._content[position].get_states([n])
                            break
                        except (AttributeError, KeyError):  # Attribute error because the content may not have the method, Key error because the parameter may not belong to the content
                            continue
                elif position == -1:
                    cont_st = {n: self._local_states[n]}
                else:
                    cont_st = self._content[position].get_states([n])

                states = {**states, **cont_st}

        return states

    def get_states_name(self):
        """
        This method returns the names of the states of the component and of the
        ones contained.

        Returns
        -------
        list(str):
            List with the names of the states.
        """

        return list(self.get_states().keys())

    def set_states(self, states):
        """
        This method sets the values of the states.

        Parameters
        ----------
        states : dict
            Contains the states of the element to be set. The keys must be
            the ones returned by the method get_states_name. Only the
            states that have to be changed should be passed.
        """

        for s in states.keys():
            position = self._find_content_from_name(s)

            if position is None:
                for c in self._content_pointer.keys():
                    try:
                        position = self._content_pointer[c]
                        self._content[position].set_states({s: states[s]})
                        break
                    except (KeyError, ValueError):
                        continue
            elif position == -1:
                self._local_states[s] = states[s]
            else:
                self._content[position].set_states({s: states[s]})

    def reset_states(self, id=None):
        """
        This method sets the states to the values provided to the __init__
        method. If a state was initialized as None, it will not be reset.

        Parameters
        ----------
        id : list(str)
            List of element's id where the method is applied.
        """

        try:
            local_id = self.id
        except AttributeError:
            local_id = None

        if id is None:
            for c in self._content_pointer.keys():
                position = self._content_pointer[c]
                try:
                    self._content[position].reset_states()
                except AttributeError:
                    continue

                if self._init_local_states:
                    self.set_states(states=self._init_local_states)
        else:
            if isinstance(id, str):
                id = [id]
            for i in id:
                if i == local_id and self._init_local_states:
                    self.set_states(states=self._init_local_states)
                elif i != local_id:
                    i += '_X'  # Needed to work with find_content_from_name
                    position = self._find_content_from_name(i)

                    self._content[position].reset_states()

    def get_timestep(self):
        """
        This method returns the timestep used by the element.

        Returns
        -------
        float
            Timestep
        """
        return self._dt

    def set_timestep(self, dt):
        """
        This method sets the timestep used by the element.

        Parameters
        ----------
        dt : float
            Timestep
        """

        self._dt = dt

        for c in self._content_pointer.keys():
            position = self._content_pointer[c]

            try:
                self._content[position].set_timestep(dt)
            except AttributeError:
                continue

    def define_solver(self, solver):
        """
        This method define the solver to use for the differential equation.

        Parameters
        ----------
        solver : superflexpy.utils.root_finder.RootFinder
            Solver used to find the root(s) of the differential equation(s).
            Child classes may implement their own solver, therefore the tipe
            of the solver is not enforced.
        """

        for c in self._content_pointer.keys():
            position = self._content_pointer[c]

            try:
                self._content[position].define_solver(solver)
            except AttributeError:
                continue
