#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# paulicollections.py: 
##
# © 2012 Christopher E. Granade (cgranade@gmail.com) and
#     Ben Criger (bcriger@gmail.com).
# This file is a part of the QuaEC project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

## IMPORTS ##

from PauliClass import *
from collections import Sequence
from singletons import Unspecified

import unitary_reps

## ALL ##

__all__ = [
    'PauliList'
    ]
        
## CLASSES ##

class PauliList(list):
    r"""
    Subclass of :obj:`list` offering useful methods for lists of
    :class:`qecc.Pauli` instances.
    
    :param paulis: Instances either of :obj:`str` or :class:`qecc.Pauli`, or
        the special object :obj:`qecc.Unspecified`.
        Strings are passed to the constructor of :class:`qecc.Pauli` for
        convinenence.
    """

    def __init__(self, *paulis):
        if len(paulis) == 1 and isinstance(paulis[0], Sequence) and not isinstance(paulis[0], str):
            paulis = map(ensure_pauli, paulis[0])
        else:
            paulis = map(ensure_pauli, paulis)
            
        # FIXME: figure out why super(list, self).__init__ doesn't work.
        list.__init__(self, paulis)
        
    def __getitem__(self, *args):
        item = super(PauliList, self).__getitem__(*args)
        if not isinstance(item, list):
            return item
        else:
            return PauliList(*item)
        
    def __getslice__(self, *args):
        # Note that this must be overrided due to an implementation detail of
        # CPython. See the note at
        #     http://docs.python.org/reference/datamodel.html#additional-methods-for-emulation-of-sequence-types
        return PauliList(*super(PauliList, self).__getslice__(*args))
        
    def __add__(self, other):
        return PauliList(*(super(PauliList, self).__add__(other)))
        
    def generated_group(self):
        """
        Yields an iterator onto the group generated by this list of Pauli
        operators. See also :obj:`qecc.from_generators`.
        """
        return from_generators(self)
    
    def stabilizer_subspace(self):
        r"""
        Returns a :class:`numpy.ndarray` of shape ``(n - k, 2 ** n)`` containing
        an orthonormal basis for the mutual +1 eigenspace of each fully
        specified Pauli in this list. Here, ``n`` is taken to be the number of
        qubits and ``k`` is taken to be the number of independent Pauli
        operators in this list.
        
        Raises a :obj:`RuntimeError` if NumPy cannot be imported.
        
        For example, to find the Bell basis vector :math:`\left|\beta_{00}\right\rangle`
        using the stabilizer formalism:
        
        >>> import qecc as q
        >>> q.PauliList('XX', q.Unspecified, q.Unspecified, 'ZZ').stabilizer_subspace()
        array([[ 0.70710678+0.j,  0.00000000+0.j,  0.00000000+0.j,  0.70710678+0.j]])
        
        Similarly, one can find the codewords of the phase-flip code :math:`S = \langle XXI, IXX \rangle`:
        
        >>> q.PauliList('XXI', 'IXX').stabilizer_subspace()
        array([[ 0.50000000-0.j, -0.00000000-0.j, -0.00000000-0.j,  0.50000000-0.j,
                -0.00000000-0.j,  0.50000000+0.j,  0.50000000-0.j, -0.00000000-0.j],
               [ 0.02229922+0.j,  0.49950250+0.j,  0.49950250+0.j,  0.02229922+0.j,
                 0.49950250+0.j,  0.02229922+0.j,  0.02229922+0.j,  0.49950250+0.j]])
                 
        Note that in this second case, some numerical errors have occured;
        this method does not guarantee that the returned basis
        vectors are exact.
        """
        return unitary_reps.mutual_eigenspace([P.as_unitary() for P in self if P is not Unspecified])
        
    def centralizer_gens(self, group_gens=None):
        r"""
        Returns the generators of the centralizer group
        :math:`\mathrm{C}(P_1, \dots, P_k)`, where :math:`P_i` is the :math:`i^{\text{th}}`
        element of this list. See :meth:`qecc.Pauli.centralizer_gens` for
        more information.
        """
        if group_gens is None:
            # NOTE: Assumes all Paulis contained by self have the same nq.
            Xs, Zs = elem_gens(len(self[0]))
            group_gens = Xs + Zs
            
        if len(self) == 0:
            # C({}) = G
            return PauliList(group_gens)
            
        centralizer_0 = self[0].centralizer_gens(group_gens=group_gens)
            
        if len(self) == 1:
            return centralizer_0
        else:
            return self[1:].centralizer_gens(group_gens=centralizer_0)
        
