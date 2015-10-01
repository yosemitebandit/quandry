"""Util grab-bag."""

import math


def distance(a, b):
  """Get the distance between points a and b."""
  dx = a[0] - b[0]
  dy = a[1] - b[1]
  return math.sqrt(dx**2 + dy**2)
