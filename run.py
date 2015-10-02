"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from quandry import JigsawPiece


filepaths = ('a.jpg',)
figure_grid = gridspec.GridSpec(len(filepaths), 2)
figure = plt.gcf()

for index, path in enumerate(filepaths):
  # Calculate the piece data.
  print 'processing "%s"..' % path
  path = os.path.join('sample-pieces/', path)
  piece = JigsawPiece(path)
  # Iteratively look for a reasonable number of corner candidates.
  harris_sensitivity = 0.05
  iterations = 0
  while True:
    piece.find_contours()
    piece.find_corners(harris_sensitivity=harris_sensitivity)
    print '  %s candidate corners' % len(piece.candidate_corners)
    if 100 <= len(piece.candidate_corners) <= 250:
      break
    if iterations > 100:
      break
    elif len(piece.candidate_corners) < 100:
      harris_sensitivity -= 0.01
    elif len(piece.candidate_corners) > 250:
      harris_sensitivity += 0.051
    iterations += 1
  # Find other piece data, including the "true corners."
  piece.find_center()
  piece.find_true_corners()
  # Plot the image.
  ax0 = plt.subplot(figure_grid[index, 0])
  ax0.imshow(piece.raw_image, aspect='equal')
  ax0.axis('off')
  # Plot the derived data in another subplot.
  ax1 = plt.subplot(figure_grid[index, 1])
  ax1.plot(piece.trace[:, 1], -piece.trace[:, 0], color='gray')
  ax1.plot(piece.center[1], -piece.center[0], '*b', markersize=8)
  for cc in piece.candidate_corners:
    ax1.plot(cc[1], -cc[0], '+r', markersize=8)
  corner_xs = [c[1] for c in piece.corners]
  corner_ys = [-c[0] for c in piece.corners]
  ax1.plot(corner_xs, corner_ys, 'og', markersize=8)
  ax1.set_aspect('equal')
  ax1.axis('off')
  # Set the raw image's axis limits to match the derived data's axis.
  ax0.axes.set_xlim(ax1.axes.get_xlim())
  ax0.axes.set_ylim([-1*limit for limit in ax1.axes.get_ylim()])

plt.show()
figure.savefig('out.png')
