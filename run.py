"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from quandry import compare
from quandry import JigsawPiece


initial_harris_sensitivity = 0.05
max_corner_iterations = 50
min_corner_candidates = 30
max_corner_candidates = 50


filepaths = ('g.jpg', 'h.jpg')
figure_grid = gridspec.GridSpec(len(filepaths), 2)
figure_grid.update(wspace=0.025, hspace=0.05)
figure = plt.gcf()


for index, filepath in enumerate(filepaths):
  # Setup each axis.
  ax0 = plt.subplot(figure_grid[index, 0])
  ax1 = plt.subplot(figure_grid[index, 1])
  ax0.axis('off')
  ax1.axis('off')
  ax0.set_aspect('equal')
  ax1.set_aspect('equal')

  # Start processing each image.
  print 'processing "%s"..' % filepath
  filepath = os.path.join('sample-pieces/', filepath)
  piece = JigsawPiece(filepath)
  # Plot the raw image.
  ax0.imshow(piece.raw_image, aspect='equal')

  # Get contours.
  try:
    if 'g.jpg' in filepath:
      piece.segment(low_threshold=50, high_threshold=150)
    elif 'h.jpg' in filepath:
      piece.segment(low_threshold=90, high_threshold=120)
    elif '0.jpg' in filepath:
      piece.segment(low_threshold=100, high_threshold=170)
    else:
      piece.segment()
    ax0.plot(piece.trace[:, 1], piece.trace[:, 0], color='green')
    ax1.plot(piece.trace[:, 1], -piece.trace[:, 0], color='gray')
  except AssertionError:
    print 'could not find contours for "%s"' % filepath
    continue

  # Set the raw image's axis limits to match the derived data's axis.
  ax0.axes.set_xlim(ax1.axes.get_xlim())
  ax0.axes.set_ylim([-1*limit for limit in ax1.axes.get_ylim()])

  # Find the center.
  try:
    piece.find_center()
    ax1.plot(piece.center[1], -piece.center[0], '*b', markersize=8)
  except:
    print 'could not find center for "%s"' % filepath
    continue

  # Iteratively look for a reasonable number of corner candidates.
  try:
    harris_sensitivity = initial_harris_sensitivity
    iterations = 0
    while True:
      piece.find_corners(harris_sensitivity=harris_sensitivity)
      print '  %s candidate corners' % len(piece.candidate_corners)
      if (min_corner_candidates <= len(piece.candidate_corners) and
          max_corner_candidates >= len(piece.candidate_corners)):
        break
      if iterations > max_corner_iterations:
        raise ValueError
      elif len(piece.candidate_corners) < min_corner_candidates:
        harris_sensitivity -= 0.01
      elif len(piece.candidate_corners) > max_corner_candidates:
        harris_sensitivity += 0.051
      iterations += 1
    for cc in piece.candidate_corners:
      ax1.plot(cc[1], -cc[0], '+r', markersize=8)
  except:
    print 'could not find corner candidates for "%s"' % filepath
    continue

  # Find the "true corners."
  try:
    piece.find_true_corners()
    corner_xs = [c[1] for c in piece.corners]
    corner_ys = [-c[0] for c in piece.corners]
    ax1.plot(corner_xs, corner_ys, 'og', markersize=8)
  except:
    print 'could not find true corners for "%s"' % filepath
    continue

  # Determine the four sides: paths along the outline that connect corners.
  try:
    piece.find_sides()
    for corner_path in piece.sides:
      x = [p[1] for p in corner_path]
      y = [-p[0] for p in corner_path]
      ax1.plot(x, y)
  except:
    print 'could not find sides for "%s"' % filepath

  # Get straight line distances between corners.
  try:
    piece.find_corner_distances()
    for index, length in enumerate(piece.corner_distances):
      corner_a = piece.corners[index]
      corner_b = piece.corners[(index+1) % 4]
      x = np.average([corner_a[1], corner_b[1]])
      y = -1 * np.average([corner_a[0], corner_b[0]])
      ax1.text(x, y, '%0.0f' % length)
  except:
    print 'could not find side lengths for "%s"' % filepath
    continue


plt.show()
figure.savefig('out.png', dpi=100)
