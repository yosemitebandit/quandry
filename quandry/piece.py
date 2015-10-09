"""Puzzle pieces."""

import itertools
import math

import numpy as np
from scipy import ndimage
from skimage import feature
from skimage import filters
from skimage import io
from skimage import measure
from skimage import morphology

from quandry import util


class JigsawPiece(object):
  """Representation of a puzzle piece."""

  def __init__(self, filepath):
    # Load the image and denoise.
    self.raw_image = io.imread(filepath)
    self.grey_image = io.imread(filepath, as_grey=True)
    # Setup other to-be-determined attributes.
    self.segmentation = []
    self.outline = []
    self.candidate_corners = []
    self.center = []
    self.angles = []
    self.corner_sets = []
    self.areas = []
    self.corners = []
    self.sides = []
    self.corner_distances = []

  def segment(self, low_threshold=50, high_threshold=110, contour_level=0.5):
    """Finds the piece's outline via region-based segmentation.

    http://scikit-image.org/docs/dev/user_guide/tutorial_segmentation.html
    http://scikit-image.org/docs/dev/auto_examples/plot_contours.html
    """
    elevation_map = filters.sobel(self.grey_image)
    markers = np.zeros_like(self.grey_image)
    low_threshold = low_threshold / 255.
    high_threshold = high_threshold / 255.
    markers[self.grey_image < low_threshold] = 2
    markers[self.grey_image > high_threshold] = 1
    self.segmentation = morphology.watershed(elevation_map, markers)
    self.segmentation = ndimage.binary_fill_holes((self.segmentation - 1))
    contours = measure.find_contours(self.segmentation, contour_level)
    largest_contour = sorted(contours, key=lambda c: len(c))[-1]
    # We have to flip these coordinates over y=x to fix some issues with the
    # plots.
    self.outline = np.array([[p[1], p[0]] for p in largest_contour])

  def find_center(self):
    """Find approximate center."""
    self.center = [
      np.average(self.outline[:, 0]),
      np.average(self.outline[:, 1])]

  def find_corners(self, harris_sensitivity=0.05, corner_peaks_dist=2):
    """Get candidate corners."""
    harris = feature.corner_harris(self.segmentation, k=harris_sensitivity)
    # Again note the flip over y=x to fix plotting issues..
    corners = [[p[1], p[0]] for p in
               feature.corner_peaks(harris, min_distance=corner_peaks_dist)]
    # Try to remove outliers -- probably edges of the image.
    distances = [util.distance(c, self.center) for c in corners]
    average = np.average(distances)
    stdev = np.std(distances)
    self.candidate_corners = []
    for index, corner in enumerate(corners):
      if average + 1.5 * stdev > distances[index]:
        self.candidate_corners.append(corner)

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
    corners = []
    for index in sorted_areas[0][0]:
      corners.append(self.candidate_corners[index])
    # Sort them such that the top left corner is first and then they proceed in
    # clockwise order.
    angles = [(c, util.angle(c, self.center)) for c in corners]
    corners = [c[0] for c in sorted(angles, key=lambda a: a[1])]
    self.corners = [corners[1], corners[0], corners[3], corners[2]]

  def find_sides(self):
    """Find the piece's four sides."""
    print 'outline elements:', len(self.outline)
    for corner_index, corner_one in enumerate(self.corners):
      # The corners may not lie directly on the piece's outline.  So we find the
      # points closest to the corners that do lie on the outline.
      corner_one_distances = [
        util.distance(corner_one, p) for p in self.outline]
      index_one = corner_one_distances.index(min(corner_one_distances))
      corner_two = self.corners[(corner_index + 1) % 4]
      corner_two_distances = [
        util.distance(corner_two, p) for p in self.outline]
      index_two = corner_two_distances.index(min(corner_two_distances))
      # The array of coordinates defining the outline may wrap around as we
      # trace a specific side..
      larger_index = max((index_one, index_two))
      smaller_index = min((index_one, index_two))
      if float(larger_index - smaller_index) / len(self.outline) > 0.4:
        side = np.concatenate(
          (self.outline[larger_index:-1], self.outline[0:smaller_index]),
          axis=0)
      else:
        side = self.outline[smaller_index:larger_index]
      self.sides.append(side)

  def find_corner_distances(self):
    """Find straight line distances between corners."""
    for corner_index, corner_a in enumerate(self.corners):
      corner_b = self.corners[(corner_index + 1) % 4]
      distance = util.distance(corner_a, corner_b)
      self.corner_distances.append(distance)
