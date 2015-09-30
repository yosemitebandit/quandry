"""Puzzle piece image processing."""

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
from skimage import feature
from skimage import filters
from skimage import io


def distance(a, b):
  """Get the distance between points a and b."""
  dx = a[0] - b[0]
  dy = a[1] - b[1]
  return math.sqrt(dx**2 + dy**2)


# Load the image.
source = 'a.jpg'
piece = io.imread(source, as_grey=True)

# Find edges with the Canny filter.
low = 0.0
otsu = filters.threshold_otsu(piece, nbins=256)
sigma = 2
canny_edges = feature.canny(piece, sigma=sigma, low_threshold=low,
                            high_threshold=otsu)
canny_edges = np.logical_not(canny_edges)

# Get corners.
dist = 20
sensitivity = 0.05
window = 100
harris = feature.corner_harris(canny_edges, k=sensitivity)
coords = feature.corner_peaks(harris, min_distance=dist)

# Find approximate center.
center = [sum(coords[:, 0]) / len(coords[:, 0]),
          sum(coords[:, 1]) / len(coords[:, 1])]

# Find angle to each candidate corner, relative to this center.
angles = []
for coord in coords:
  x = coord[0] - center[0]
  y = coord[1] - center[1]
  angles.append(180 / math.pi * math.atan2(y, x))

# Find corner sets.
trig_threshold = 0.2
center_dist_threshold = 0.3
corner_sets = {}
for i, coord_one in enumerate(coords):
  corner_sets[i] = {
    90: [],
    180: [],
  }
  angle_one = math.pi / 180 * angles[i]
  center_dist_one = distance(coord_one, center)
  for k, coord_two in enumerate(coords):
    if i == k:
      continue
    center_dist_two = distance(coord_two, center)
    if (abs(center_dist_two - center_dist_one) / center_dist_one >
        center_dist_threshold):
      continue
    angle_two = math.pi / 180 * angles[k]
    cosine = math.cos(angle_one - angle_two)
    sine = math.sin(angle_one - angle_two)
    if abs(cosine) < trig_threshold:
      corner_sets[i][90].append(k)
    if abs(sine) < trig_threshold:
      corner_sets[i][180].append(k)

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

# Get area of each rect candidate with Bretschneider's Formula.
areas = []
for rect in rect_candidates:
  a = distance(coords[rect[0]], coords[rect[3]])
  b = distance(coords[rect[1]], coords[rect[0]])
  c = distance(coords[rect[2]], coords[rect[1]])
  d = distance(coords[rect[3]], coords[rect[2]])
  p = distance(coords[rect[0]], coords[rect[2]])
  q = distance(coords[rect[1]], coords[rect[3]])
  try:
    area = 0.25 * math.sqrt(4 * p**2 * q**2 - (b**2 + d**2 - a**2 - c**2)**2)
  except ValueError:
    area = 0
  areas.append([rect, area])

# Take a guess at the true corners by choosing the biggest area.
sorted_areas = sorted(areas, key=lambda a: a[1], reverse=True)
corner_coords = [[], []]
for index in sorted_areas[0][0]:
  corner_coords[0].append(coords[index][0])
  corner_coords[1].append(coords[index][1])

# Display results.
fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))

ax1.imshow(piece, cmap=plt.cm.gray)
ax1.axis('off')

ax2.imshow(canny_edges, cmap=plt.cm.gray)
ax2.axis('off')
ax2.set_title('Canny filter, $\sigma=%s$' % sigma, fontsize=20)

ax3.imshow(canny_edges, cmap=plt.cm.gray)
ax3.plot(center[1], center[0], '*b', markersize=8)
ax3.plot(corner_coords[1], corner_coords[0], 'og', markersize=12)
ax3.plot(coords[:, 1], coords[:, 0], '+r', markersize=12)
ax3.axis('off')
ax3.set_title('Harris corners', fontsize=20)

fig.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                    bottom=0.02, left=0.02, right=0.98)
plt.show()
fig.savefig('out.png')
