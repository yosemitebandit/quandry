"""Util grab-bag."""

import math


def distance(a, b):
  """Get the distance between points a and b."""
  dx = a[0] - b[0]
  dy = a[1] - b[1]
  return math.sqrt(dx**2 + dy**2)


def angle(a, b):
  """Measure the angle formed by the vector between points a and b."""
  dy = b[1] - a[1]
  dx = b[0] - a[0]
  return math.atan2(dy , dx)
