"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from quandry import JigsawPiece


denoise_weight = 0.8
contour_level = 0.4
initial_harris_sensitivity = 0.05
max_corner_iterations = 50
min_corner_candidates = 100
max_corner_candidates = 250


filepaths = ('g.jpg', 'h.jpg')
figure_grid = gridspec.GridSpec(len(filepaths), 4)
figure_grid.update(wspace=0.025, hspace=0.05)
figure = plt.gcf()


for index, path in enumerate(filepaths):
  # Setup each axis.
  ax0 = plt.subplot(figure_grid[index, 0])
  ax1 = plt.subplot(figure_grid[index, 1])
  ax2 = plt.subplot(figure_grid[index, 2])
  ax3 = plt.subplot(figure_grid[index, 3])
  ax0.axis('off')
  ax1.axis('off')
  ax2.axis('off')
  ax3.axis('off')
  ax3.set_aspect('equal')

  # Start processing each image.
  print 'processing "%s"..' % path
  path = os.path.join('sample-pieces/', path)
  piece = JigsawPiece(path, denoise_weight=denoise_weight)
  # Plot the image and the denoised image.
  ax0.imshow(piece.raw_image, aspect='equal')
  ax1.imshow(piece.image, aspect='equal', cmap=plt.cm.gray)

  # Get contours.
  try:
    piece.find_contours(contour_level=contour_level)
    ax2.imshow(piece.raw_image, aspect='equal')
    ax2.plot(piece.trace[:, 1], piece.trace[:, 0], color='green')
    ax3.plot(piece.trace[:, 1], -piece.trace[:, 0], color='gray')
  except:
    print 'could not find contours for "%s"' % path
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
      ax3.plot(cc[1], -cc[0], '+r', markersize=8)
  except:
    print 'could not find corner candidates for "%s"' % path
    continue

  # Find the center.
  try:
    piece.find_center()
    ax3.plot(piece.center[1], -piece.center[0], '*b', markersize=8)
  except:
    print 'could not find center for "%s"' % path
    continue

  # Find the "true corners."
  try:
    piece.find_true_corners()
    corner_xs = [c[1] for c in piece.corners]
    corner_ys = [-c[0] for c in piece.corners]
    ax3.plot(corner_xs, corner_ys, 'og', markersize=8)
  except:
    print 'could not find true corners for "%s"' % path
    continue

  # Get the side lengths.
  try:
    piece.find_side_lengths()
    for key in piece.side_lengths:
      index_one, index_two = [int(v) for v in key.split(',')]
      point_one = piece.trace[index_one]
      point_two = piece.trace[index_two]
      x = np.average([point_one[1], point_two[1]])
      y = -1 * np.average([point_one[0], point_two[0]])
      ax3.text(x, y, '%0.0f' % piece.side_lengths[key])
  except:
    print 'could not find true corners for "%s"' % path
    continue

  # Set the raw image's axis limits to match the derived data's axis.
  ax0.axes.set_xlim(ax3.axes.get_xlim())
  ax0.axes.set_ylim([-1*limit for limit in ax3.axes.get_ylim()])
  ax1.axes.set_xlim(ax3.axes.get_xlim())
  ax1.axes.set_ylim([-1*limit for limit in ax3.axes.get_ylim()])
  ax2.axes.set_xlim(ax3.axes.get_xlim())
  ax2.axes.set_ylim([-1*limit for limit in ax3.axes.get_ylim()])


plt.show()
figure.savefig('out.png', dpi=100)
