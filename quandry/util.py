"""Util grab-bag."""

import math

import numpy as np


def distance(a, b):
  """Get the distance between points a and b."""
  dx = a[0] - b[0]
  dy = a[1] - b[1]
  return math.sqrt(dx**2 + dy**2)


def angle(a, b):
  """Measure the angle formed by the vector between points a and b."""
  dy = b[1] - a[1]
  dx = b[0] - a[0]
  return math.atan2(dy, dx)


def rotate(point, angle):
  """Rotate a point about the origin by some angle (given in radians)."""
  rotation_matrix = np.array([
    [math.cos(angle), -math.sin(angle)],
    [math.sin(angle), math.cos(angle)]])
  point = np.array([
    [point[0]],
    [point[1]]])
  result = np.dot(rotation_matrix, point)
  return (result[0], result[1])


def distance_to_line(line_endpoints, c):
  """Finds the distance from point c to a line defined by two endpoints."""
  a = line_endpoints[0]
  b = line_endpoints[1]
  result = (abs((b[0] - a[0])*(a[1] - c[1]) - (a[0] - c[0])*(b[1] - a[1])) /
            distance(a, b))
  # It's an ndarray..
  return result[0]
