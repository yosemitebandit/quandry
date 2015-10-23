"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from quandry import JigsawPiece


filepaths = ('take-two/0.jpg', 'take-two/1.jpg', 'take-two/2.jpg',
             'take-two/3.jpg')
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
    piece.segment()
    ax0.plot(piece.outline[:, 0], -piece.outline[:, 1], color='green')
    ax1.plot(piece.outline[:, 0], piece.outline[:, 1], color='gray')
  except:
    print 'could not find contours for "%s"' % filepath
    continue

  # Set the raw image's axis limits to match the derived data's axis.
  ax0.axes.set_xlim(ax1.axes.get_xlim())
  y_min, y_max = ax1.axes.get_ylim()
  ax0.axes.set_ylim((-y_min, -y_max))

  # Find the center.
  try:
    piece.find_center()
    ax1.plot(piece.center[0], piece.center[1], '*b', markersize=8)
  except:
    print 'could not find center for "%s"' % filepath
    continue

  # Find corner candidates with template matching.
  try:
    piece.template_corners()
    for cc in piece.candidate_corners:
      ax1.plot(cc[0], cc[1], '+r', markersize=8)
  except:
    print 'could not find corner candidates for "%s"' % filepath
    continue

  # Find the "true corners."
  try:
    piece.find_true_corners()
    corner_xs = [c[0] for c in piece.corners]
    corner_ys = [c[1] for c in piece.corners]
    ax1.plot(corner_xs, corner_ys, 'og', markersize=8)
  except:
    print 'could not find true corners for "%s"' % filepath
    continue

  # Determine the four sides: paths along the outline that connect corners.
  try:
    piece.find_sides()
    colors = ('r', 'g', 'b', 'cyan')
    for index, side in enumerate(piece.sides):
      x = [s[0] for s in side]
      y = [s[1] for s in side]
      ax1.plot(x, y, color=colors[index])
  except:
    print 'could not find sides for "%s"' % filepath

  # Get length of each side and label.
  try:
    piece.find_side_lengths()
  except:
    print 'could not find side lengths for "%s"' % filepath
    continue

  # Classify each side's type and label.
  try:
    piece.find_side_types()
    for index, side in enumerate(piece.sides):
      length = piece.side_lengths[index]
      side_type = piece.side_types[index]
      x, y = piece.mean_side_points[index]
      label = 'side %s: %0.0f (%s)' % (index, length, side_type)
      ax1.text(x, y, label, horizontalalignment='center',
               verticalalignment='center')
  except:
    print 'could not find side types for "%s"' % filepath
    continue

plt.show()
figure.savefig('out.png', dpi=200)
