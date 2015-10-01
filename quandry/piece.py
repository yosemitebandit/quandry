"""Representation of a puzzle piece."""

import itertools
import math

import numpy as np
from skimage import feature
from skimage import filters
from skimage import io

from quandry import util


class JigsawPiece(object):
  def __init__(self, filepath, canny_low_thresh=0, canny_sigma=2,
               harris_sensitivity=0.05, corner_peaks_dist=2,
               angle_threshold=0.2, center_dist_ratio_threshold=0.2):
    # Load the image.
    self.image = io.imread(filepath, as_grey=True)
    # Find edges with the Canny filter.
    otsu_high_threshold = filters.threshold_otsu(self.image, nbins=256)
    self.outline = feature.canny(
      self.image, sigma=canny_sigma, low_threshold=canny_low_thresh,
      high_threshold=otsu_high_threshold)
    print 'outline'
    # Invert so we can plot a black line on a white background.
    self.outline = np.logical_not(self.outline)
    # Get candidate corners.
    harris = feature.corner_harris(self.outline, k=harris_sensitivity)
    print 'harris'
    corners = feature.corner_peaks(harris, min_distance=corner_peaks_dist)
    print 'corner peaks'
    # Find approximate center by computing average of these corners.
    self.center = [sum(corners[:, 0]) / len(corners[:, 0]),
                   sum(corners[:, 1]) / len(corners[:, 1])]
    # Find angle to each candidate corner, relative to the center.
    angles = []
    for coord in corners:
      x = coord[0] - self.center[0]
      y = coord[1] - self.center[1]
      angles.append(180 / math.pi * math.atan2(y, x))
    # Find corner sets.
    corner_sets = {}
    for i, coord_one in enumerate(corners):
      corner_sets[i] = {
        90: [],
        180: [],
      }
      angle_one = math.pi / 180 * angles[i]
      center_dist_one = util.distance(coord_one, self.center)
      for k, coord_two in enumerate(corners):
        if i == k:
          continue
        center_dist_two = util.distance(coord_two, self.center)
        if (abs(center_dist_two - center_dist_one) / center_dist_one >
            center_dist_ratio_threshold):
          continue
        angle_two = math.pi / 180 * angles[k]
        cosine = math.cos(angle_one - angle_two)
        sine = math.sin(angle_one - angle_two)
        if abs(cosine) < angle_threshold:
          corner_sets[i][90].append(k)
        if abs(sine) < angle_threshold:
          corner_sets[i][180].append(k)
    print 'corner sets', len(corner_sets)
    # Generate all possible rectangle candidates (collections of four corners).
    rect_candidates = []
    for index in corner_sets:
      # Need at least two 90 neighbors and one 180 coord.
      if len(corner_sets[index][90]) < 2:
        continue
      if len(corner_sets[index][180]) < 1:
        continue
      # Choose the index, one 180 and two 90s to form a possible rectangle.
      for one_eighty in corner_sets[index][180]:
        for two_90s in itertools.combinations(corner_sets[index][90], 2):
          rect_candidates.append([index, two_90s[0], one_eighty, two_90s[1]])
    print 'rect candidates'
    # Get area of each rect candidate with Bretschneider's Formula.
    areas = []
    for rect in rect_candidates:
      a = util.distance(corners[rect[0]], corners[rect[3]])
      b = util.distance(corners[rect[1]], corners[rect[0]])
      c = util.distance(corners[rect[2]], corners[rect[1]])
      d = util.distance(corners[rect[3]], corners[rect[2]])
      p = util.distance(corners[rect[0]], corners[rect[2]])
      q = util.distance(corners[rect[1]], corners[rect[3]])
      try:
        area = 0.25 * math.sqrt(
          4 * p**2 * q**2 - (b**2 + d**2 - a**2 - c**2)**2)
      except ValueError:
        area = 0
      areas.append([rect, area])
    print 'areas'
    # Take a guess at the true corners by choosing the biggest area.
    sorted_areas = sorted(areas, key=lambda a: a[1], reverse=True)
    self.corners = [[], []]
    for index in sorted_areas[0][0]:
      self.corners[0].append(corners[index][0])
      self.corners[1].append(corners[index][1])
