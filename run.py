"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from quandry import JigsawPiece


filepaths = ('a.jpg', 'b.jpg',)#'c.jpg', 'd.jpg', 'e.jpg', 'f.jpg')
figure_grid = gridspec.GridSpec(len(filepaths), 3)
figure = plt.gcf()

for index, path in enumerate(filepaths):
  # Calculate the piece data.
  print 'processing "%s"..' % path
  path = os.path.join('sample-pieces/', path)
  piece = JigsawPiece(path, denoise_weight=3)
  piece.find_contours()
  # Iteratively look for a reasonable number of corner candidates.
  harris_sensitivity = 0.05
  iterations = 0
  while True:
    piece.find_corners(harris_sensitivity=harris_sensitivity)
    print '  %s candidate corners' % len(piece.candidate_corners)
    if 150 <= len(piece.candidate_corners) <= 250:
      break
    if iterations > 100:
      break
    elif len(piece.candidate_corners) < 150:
      harris_sensitivity -= 0.01
    elif len(piece.candidate_corners) > 250:
      harris_sensitivity += 0.051
    iterations += 1
  # Find other piece data, including the "true corners."
  piece.find_center()
  piece.find_true_corners()
  piece.find_side_lengths()

  # Plot the image.
  ax0 = plt.subplot(figure_grid[index, 0])
  ax0.imshow(piece.raw_image, aspect='equal')
  ax11 = plt.subplot(figure_grid[index, 1])
  ax11.imshow(piece.image, aspect='equal', cmap=plt.cm.gray)
  ax11.axis('off')
  # Plot the derived outline in another subplot.
  ax1 = plt.subplot(figure_grid[index, 2])
  ax1.plot(piece.trace[:, 1], -piece.trace[:, 0], color='gray')
  # Show the derived centroid and candidate corners.
  ax1.plot(piece.center[1], -piece.center[0], '*b', markersize=8)
  for cc in piece.candidate_corners:
    ax1.plot(cc[1], -cc[0], '+r', markersize=8)
  # Show our best guess at the "true corners."
  corner_xs = [c[1] for c in piece.corners]
  corner_ys = [-c[0] for c in piece.corners]
  ax1.plot(corner_xs, corner_ys, 'og', markersize=8)
  # Label the computed side path lengths.
  for key in piece.side_lengths:
    index_one, index_two = [int(v) for v in key.split(',')]
    point_one = piece.trace[index_one]
    point_two = piece.trace[index_two]
    x = np.average([point_one[1], point_two[1]])
    y = -1 * np.average([point_one[0], point_two[0]])
    ax1.text(x, y, '%0.0f' % piece.side_lengths[key])
  # Set the raw image's axis limits to match the derived data's axis.
  ax0.axes.set_xlim(ax1.axes.get_xlim())
  ax0.axes.set_ylim([-1*limit for limit in ax1.axes.get_ylim()])
  ax11.axes.set_xlim(ax1.axes.get_xlim())
  ax11.axes.set_ylim([-1*limit for limit in ax1.axes.get_ylim()])
  # Set other axis properties.
  ax0.axis('off')
  ax1.axis('off')
  ax1.set_aspect('equal')

plt.show()
figure.savefig('out.png')
