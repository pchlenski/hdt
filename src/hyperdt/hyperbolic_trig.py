import numpy as np
from scipy.optimize import root_scalar


def _dist(x1, x2):
    """
    Closed form for distance between two unique rotational intersections where all other
    coordinates are 0

    A few observations and simplifications:
    - The distance is defined as arccosh(-a(theta1) * a(theta2) * cos(theta1 + theta2))
        - a(theta) = sqrt(-sec(2theta))
    - All angles are in (pi / 4, 3pi / 4). As such:
        - sec(theta) > 0, so we never take sqrt of a negative number
        - cos(theta1 + theta2) < 0, so we always take arccosh of a positive number
    - We can simplify the distance to a(theta1) * a(theta2) * cos(theta1 + theta2)
        - This is more stable than taking arccosh
    """
    a1 = np.sqrt(-1 / np.cos(2 * x1))
    a2 = np.sqrt(-1 / np.cos(2 * x2))
    dist = a1 * a2 * np.cos(x1 + x2)

    # Deal with really close values - numerical weirdness
    if np.abs(dist) < 1e-6 or np.abs(x1 - x2) < 1e-6:
        dist = 0
    return dist


def _dist_aberration(m, x1, x2):
    """This is 0 when d(theta1, m) = d(theta2, m) = d(theta1, theta2)/2"""
    return _dist(x1, m) - _dist(m, x2)


def get_midpoint(theta1, theta2, skip_checks=True):
    """Find hyperbolic midpoint of two angles"""
    theta_min = np.min([theta1, theta2])
    theta_max = np.max([theta1, theta2])
    root = root_scalar(_dist_aberration, args=(theta1, theta2), bracket=[theta_min, theta_max]).root
    if not skip_checks:
        assert np.abs(_dist_aberration(root, theta1, theta2)) < 1e-6
        assert root >= theta_min and root <= theta_max
    return root


def get_candidates_hyperbolic(X, dim, timelike_dim, dot_product="sparse"):
    """Get candidate split points for hyperbolic decision tree"""
    if dot_product == "sparse_minkowski":
        thetas = np.arctan2(-X[:, timelike_dim], X[:, dim])
    else:
        thetas = np.arctan2(X[:, timelike_dim], X[:, dim])
    thetas = np.unique(thetas)  # This also sorts

    # Get all pairs of angles
    candidates = np.array([get_midpoint(theta1, theta2) for theta1, theta2 in zip(thetas[:-1], thetas[1:])])
    if dot_product == "sparse_minkowski":
        pass
    else:
        assert (candidates >= np.pi / 4).all()
        assert (candidates <= 3 * np.pi / 4).all()
    return candidates
