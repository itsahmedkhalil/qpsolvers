#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2022 Stéphane Caron and the qpsolvers contributors.
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

"""Solver interface for CVXOPT."""

from typing import Dict, Optional, Union

import cvxopt
from cvxopt.solvers import options, qp
from numpy import array, ndarray
from scipy.sparse import csc_matrix

from .conversions import linear_from_box_inequalities

options["show_progress"] = False  # disable CVXOPT output by default


def to_cvxopt(
    M: Union[ndarray, csc_matrix]
) -> Union[cvxopt.matrix, cvxopt.spmatrix]:
    """
    Convert matrix to CVXOPT format.

    Parameters
    ----------
    M :
        Matrix in NumPy or CVXOPT format.

    Returns
    -------
    :
        Matrix in CVXOPT format.
    """
    if isinstance(M, ndarray):
        return cvxopt.matrix(M)
    coo = M.tocoo()
    return cvxopt.spmatrix(
        coo.data.tolist(), coo.row.tolist(), coo.col.tolist(), size=M.shape
    )


def cvxopt_solve_qp(
    P: Union[ndarray, csc_matrix],
    q: ndarray,
    G: Optional[Union[ndarray, csc_matrix]] = None,
    h: Optional[ndarray] = None,
    A: Optional[Union[ndarray, csc_matrix]] = None,
    b: Optional[ndarray] = None,
    lb: Optional[ndarray] = None,
    ub: Optional[ndarray] = None,
    solver: str = None,
    initvals: Optional[ndarray] = None,
    verbose: bool = False,
    maxiters: Optional[int] = None,
    abstol: Optional[float] = None,
    reltol: Optional[float] = None,
    feastol: Optional[float] = None,
    refinement: Optional[int] = None,
) -> Optional[ndarray]:
    """
    Solve a Quadratic Program defined as:

    .. math::

        \\begin{split}\\begin{array}{ll}
        \\mbox{minimize} &
            \\frac{1}{2} x^T P x + q^T x \\\\
        \\mbox{subject to}
            & G x \\leq h                \\\\
            & A x = b                    \\\\
            & lb \\leq x \\leq ub
        \\end{array}\\end{split}

    using `CVXOPT <http://cvxopt.org/>`_.

    Parameters
    ----------
    P :
        Symmetric quadratic-cost matrix. Together with :math:`A` and :math:`G`,
        it should satisfy :math:`\\mathrm{rank}([P\\ A^T\\ G^T]) = n`, see the
        rank assumptions below.
    q :
        Quadratic-cost vector.
    G :
        Linear inequality matrix. Together with :math:`P` and :math:`A`, it
        should satisfy :math:`\\mathrm{rank}([P\\ A^T\\ G^T]) = n`, see the
        rank assumptions below.
    h :
        Linear inequality vector.
    A :
        Linear equality constraint matrix. It needs to be full row rank, and
        together with :math:`P` and :math:`G` satisfy
        :math:`\\mathrm{rank}([P\\ A^T\\ G^T]) = n`. See the rank assumptions
        below.
    b :
        Linear equality constraint vector.
    lb :
        Lower bound constraint vector.
    ub :
        Upper bound constraint vector.
    solver :
        Set to 'mosek' to run MOSEK rather than CVXOPT.
    initvals :
        Warm-start guess vector.
    verbose :
        Set to `True` to print out extra information.
    maxiters :
        Maximum number of iterations (default: ``100``).
    abstol :
        Absolute accuracy (default: ``1e-7``).
    reltol :
        Relative accuracy (default: ``1e-6``).
    feastol :
        Tolerance for feasibility conditions (default: ``1e-7``).
    refinement :
        Number of iterative refinement steps when solving KKT equations
        (default: ``0`` if the problem has no second-order cone or matrix
        inequality constraints; ``1`` otherwise).

    Returns
    -------
    :
        Solution to the QP, if found, otherwise ``None``.

    Note
    ----
    .. _CVXOPT rank assumptions:

    **Rank assumptions:** CVXOPT requires the QP matrices to satisfy the

    .. math::

        \\begin{split}\\begin{array}{cc}
        \\mathrm{rank}(A) = p
        &
        \\mathrm{rank}([P\\ A^T\\ G^T]) = n
        \\end{array}\\end{split}

    where :math:`p` is the number of rows of :math:`A` and :math:`n` is the
    number of optimization variables. See the "Rank assumptions" paragraph in
    the report `The CVXOPT linear and quadratic cone program solvers
    <http://www.ee.ucla.edu/~vandenbe/publications/coneprog.pdf>`_ for details.

    Notes
    -----
    CVXOPT only considers the lower entries of `P`, therefore it will use a
    different cost than the one intended if a non-symmetric matrix is provided.

    See the `Algorithm Parameters
    <https://cvxopt.org/userguide/coneprog.html#algorithm-parameters>`_ section
    of the solver documentation for more details and default values of the
    solver parameters.
    """
    if lb is not None or ub is not None:
        G, h = linear_from_box_inequalities(G, h, lb, ub)

    # Update solver options if applicable
    options["show_progress"] = verbose
    if maxiters:
        options["maxiters"] = maxiters
    if abstol:
        options["abstol"] = abstol
    if reltol:
        options["reltol"] = reltol
    if feastol:
        options["feastol"] = feastol
    if refinement:
        options["refinement"] = refinement

    args = [to_cvxopt(P), to_cvxopt(q)]
    kwargs = {"G": None, "h": None, "A": None, "b": None}
    if G is not None and h is not None:
        kwargs["G"] = to_cvxopt(G)
        kwargs["h"] = to_cvxopt(h)
    if A is not None and b is not None:
        kwargs["A"] = to_cvxopt(A)
        kwargs["b"] = to_cvxopt(b)
    initvals_dict: Optional[Dict[str, cvxopt.matrix]] = None
    if initvals is not None:
        initvals_dict = {"x": to_cvxopt(initvals)}
    sol = qp(*args, solver=solver, initvals=initvals_dict, **kwargs)
    if "optimal" not in sol["status"]:
        return None
    return array(sol["x"]).reshape((q.shape[0],))
