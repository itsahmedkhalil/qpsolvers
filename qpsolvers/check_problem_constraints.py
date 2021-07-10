#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2021 Stéphane Caron <stephane.caron@normalesup.org>
#
# This file is part of qpsolvers.
#
# qpsolvers is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# qpsolvers is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with qpsolvers. If not, see <http://www.gnu.org/licenses/>.

"""
Utility function to check that a quadratic program is well-defined.
"""


def check_problem_constraints(G, h, A, b) -> None:
    """
    Check that problem constraint matrices and vectors are correctly defined.

    Parameters
    ----------
    G : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear inequality matrix.
    h : numpy.array
        Linear inequality vector.
    A : numpy.array, scipy.sparse.csc_matrix or cvxopt.spmatrix
        Linear equality matrix.
    b : numpy.array
        Linear equality vector.

    Raises
    ------
    ValueError
        If the constraints are not properly defined.
    """
    if G is None and h is not None:
        raise ValueError("incomplete inequality constraint (missing h)")
    if G is not None and h is None:
        raise ValueError("incomplete inequality constraint (missing G)")
    if A is None and b is not None:
        raise ValueError("incomplete equality constraint (missing b)")
    if A is not None and b is None:
        raise ValueError("incomplete equality constraint (missing A)")
