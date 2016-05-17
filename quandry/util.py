"""Util grab-bag."""

import math

import matplotlib.pyplot as plt
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


def percent_diff(a, b):
  """Get the percent difference between two values."""
  return 100. * abs(a - b) / a


def translate_line(line, p):
  """Translate a line such that the first point lies at point p.

  The line should be a list of (x, y) pairs.
  """
  xs, ys = zip(*line)
  translated_x = [x - p[0] for x in xs]
  translated_y = [y - p[1] for y in ys]
  return zip(*[translated_x, translated_y])


def reflect_point(p, line):
  """Reflect a point, p, over a line defined by two endpoints."""
  # Create a vector that runs through the origin.
  l1, l2 = line
  v = np.array((float(l2[0] - l1[0]), l2[1] - l1[1]))
  # Translate the to-be-reflected point as well, then do some vector math..
  #print p, l1
  p = np.array(p) - np.array(l1)
  k = np.dot(p, v) / np.dot(v, v) * v
  # Translate everything back.
  return 2 * k - p + np.array(l1)


def hausdorff(a, b):
  """Compute Hausdorff distance between two lines.

  Each line, a and b, should be lists of (x, y) points.  The first line will
  be translated such that its first point lies at the origin.  Then the angle
  to the endpoint of line a will be measured -- we'll call this angle theta.
  The vector connecting line a's endpoints we'll call V.

  Then, as with line a, points along line b will be translated such that the
  first point lies on the origin.  The points will then be rotated through
  theta.  A reflected line b will be constructed by flipping this rotated line
  over V.

  Finally we'll apply the Hausdorff routine to the reflected and non-reflected
  forms of b and return the minimum score between the two.
  """
  translated_a = translate_line(a, a[0])
  theta = angle(translated_a[0], translated_a[-1])
  v = [translated_a[0], translated_a[-1]]
  translated_b = translate_line(b, b[0])
  # The rotation method has some weird return values at the moment..
  rotated_b = []
  for point in translated_b:
    rotated_point = rotate(point, theta)
    rotated_b.append([rotated_point[0][0], rotated_point[1][0]])
  reflected_b = [reflect_point(p, v) for p in rotated_b]
  # Run the Hausdorff routine between (translated_a, rotated_b) and
  # (translated_a, reflected_b).
  results = []
  for b_line in (reflected_b, rotated_b):
    min_distances = []
    for point in translated_a:
      distances = [distance(point, b) for b in b_line]
      min_distances.append(min(distances))
    results.append(np.mean(min_distances))

  # let's plot some stuff..
  ax = plt.subplot('111')
  x = [p[0] for p in translated_a]
  y = [p[1] for p in translated_a]
  ax.plot(x, y)
  x = [p[0] for p in reflected_b]
  y = [p[1] for p in reflected_b]
  ax.plot(x, y)
  x = [p[0] for p in rotated_b]
  y = [p[1] for p in rotated_b]
  ax.plot(x, y)
  ax.set_aspect('equal')
  figure = plt.gcf()
  figure.savefig('/tmp/hout.png', dpi=200)

  return min(results)
