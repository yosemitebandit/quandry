"""Puzzle pieces."""

import itertools
import math

import numpy as np
from skimage import feature
from skimage import filters
from skimage import io
from skimage import measure

from quandry import util


class JigsawPiece(object):
  """Representation of a puzzle piece."""

  def __init__(self, filepath):
    # Load the image.
    self.raw_image = io.imread(filepath)
    self.image = io.imread(filepath, as_grey=True)
    self.outline = []
    self.candidate_corners = []
    self.center = []
    self.angles = []
    self.corner_sets = []
    self.areas = []
    self.corners = []
    self.side_lengths = {}

  def find_edges(self, canny_sigma=2, canny_low_thresh=0):
    """Find edges with the Canny filter."""
    otsu_high_threshold = filters.threshold_otsu(self.image, nbins=256)
    self.outline = feature.canny(
      self.image, sigma=canny_sigma, low_threshold=canny_low_thresh,
      high_threshold=otsu_high_threshold)
    # Invert so we can plot a black line on a white background.
    self.outline = np.logical_not(self.outline)

  def find_contours(self, level=0.51):
    """Find contours with skimage."""
    contours = measure.find_contours(self.image, level)
    self.trace = sorted(contours, key=lambda c: len(c))[-1]
    # Need to save an array (an image), not just a list of coords.
    self.outline = np.zeros(self.image.shape)
    for coord in self.trace:
      self.outline[coord[0]][coord[1]] = 1

  def find_corners(self, harris_sensitivity=0.05, corner_peaks_dist=2):
    """Get candidate corners."""
    harris = feature.corner_harris(self.outline, k=harris_sensitivity)
    self.candidate_corners = feature.corner_peaks(
      harris, min_distance=corner_peaks_dist)

  def find_center(self):
    """Find approximate center."""
    self.center = [
      np.average(self.trace[:, 0]),
      np.average(self.trace[:, 1])]

  def find_angles(self):
    """Find angle to each candidate corner, relative to the center."""
    self.angles = []
    for coord in self.candidate_corners:
      x = coord[0] - self.center[0]
      y = coord[1] - self.center[1]
      self.angles.append(180 / math.pi * math.atan2(y, x))

  def find_corner_sets(self, center_dist_threshold=0.2, angle_threshold=0.2):
    """Find corner sets."""
    self.corner_sets = {}
    for i, coord_one in enumerate(self.candidate_corners):
      self.corner_sets[i] = {
        90: [],
        180: [],
      }
      angle_one = math.pi / 180 * self.angles[i]
      center_dist_one = util.distance(coord_one, self.center)
      for k, coord_two in enumerate(self.candidate_corners):
        if i == k:
          continue
        center_dist_two = util.distance(coord_two, self.center)
        if (abs(center_dist_two - center_dist_one) / center_dist_one >
            center_dist_threshold):
          continue
        if util.distance(coord_one, coord_two) < center_dist_one:
          continue
        angle_two = math.pi / 180 * self.angles[k]
        cosine = math.cos(angle_one - angle_two)
        sine = math.sin(angle_one - angle_two)
        if abs(cosine) < angle_threshold:
          self.corner_sets[i][90].append(k)
        if abs(sine) < angle_threshold:
          self.corner_sets[i][180].append(k)

  def find_rect_candidates(self):
    """Generate all possible collections of four corners."""
    rect_candidates = []
    for index in self.corner_sets:
      # Need at least two 90 neighbors and one 180 coord.
      if len(self.corner_sets[index][90]) < 2:
        continue
      if len(self.corner_sets[index][180]) < 1:
        continue
      # Choose the index, one 180 and two 90s to form a possible rectangle.
      for one_eighty in self.corner_sets[index][180]:
        for two_90s in itertools.combinations(self.corner_sets[index][90], 2):
          rect_candidates.append([index, two_90s[0], one_eighty, two_90s[1]])
    # Get area of each rect candidate with Bretschneider's Formula.
    self.areas = []
    for rect in rect_candidates:
      a = util.distance(
        self.candidate_corners[rect[0]], self.candidate_corners[rect[3]])
      b = util.distance(
        self.candidate_corners[rect[1]], self.candidate_corners[rect[0]])
      c = util.distance(
        self.candidate_corners[rect[2]], self.candidate_corners[rect[1]])
      d = util.distance(
        self.candidate_corners[rect[3]], self.candidate_corners[rect[2]])
      p = util.distance(
        self.candidate_corners[rect[0]], self.candidate_corners[rect[2]])
      q = util.distance(
        self.candidate_corners[rect[1]], self.candidate_corners[rect[3]])
      try:
        area = 0.25 * math.sqrt(
          4 * p**2 * q**2 - (b**2 + d**2 - a**2 - c**2)**2)
      except ValueError:
        area = 0
      self.areas.append([rect, area])

  def find_true_corners(self):
    """Take a guess at the true corners."""
    self.find_angles()
    self.find_corner_sets()
    self.find_rect_candidates()
    sorted_areas = sorted(self.areas, key=lambda a: a[1], reverse=True)
    self.corners = []
    for index in sorted_areas[0][0]:
      self.corners.append(self.candidate_corners[index])

  def find_side_lengths(self):
    """Finds lengths of the four sides.

    Our so-called true corners are not exactly on self.trace.  So we have to
    find the point on self.trace that is closest to each true corner.  Then
    we get the distance along self.trace between each corner.
    """
    for corner_index, corner_one in enumerate(self.corners):
      corner_one_distances = [util.distance(corner_one, p) for p in self.trace]
      index_one = corner_one_distances.index(min(corner_one_distances))
      corner_two = self.corners[(corner_index+1) % 4]
      corner_two_distances = [util.distance(corner_two, p) for p in self.trace]
      index_two = corner_two_distances.index(min(corner_two_distances))
      if corner_index < 3:
        path = self.trace[index_one:index_two]
      else:
        # Wrap around.
        path = np.concatenate(
          (self.trace[index_one:-1], self.trace[0:index_two]), axis=0)
      side_length = 0
      for path_index, point in enumerate(path):
        if path_index == 0:
          continue
        side_length += util.distance(point, path[path_index-1])
      key = '%s,%s' % (index_one, index_two)
      self.side_lengths[key] = side_length
