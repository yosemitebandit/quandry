"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt

from quandry import JigsawPiece


#filepaths = ('a.jpg', 'b.jpg')#, 'c.jpg', 'd.jpg', 'e.jpg', 'f.jpg')
filepaths = ('a.jpg',)
subplot_rows = len(filepaths)
plot_number = 0

for path in filepaths:
  # Calculate the piece data.
  print 'processing "%s"..' % path
  path = os.path.join('sample-pieces/', path)
  piece = JigsawPiece(path)

  canny_sigma = 2
  harris_sensitivity = 0.05
  while True:
    piece.find_edges(canny_sigma=canny_sigma)
    piece.find_corners(harris_sensitivity=harris_sensitivity)
    print '  %s candidate corners' % len(piece.candidate_corners)
    if len(piece.candidate_corners) < 400:
      break
    canny_sigma += 0.1
    harris_sensitivity += 0.01

  piece.find_center()
  piece.find_angles()
  piece.find_corner_sets()
  piece.find_rect_candidates()
  piece.find_true_corners()
  # Plot the image.
  plot_number += 1
  plt.subplot(subplot_rows, 2, plot_number)
  plt.imshow(piece.image, cmap=plt.cm.jet)
  plt.axis('off')
  # Plot the derived data
  plot_number += 1
  plt.subplot(subplot_rows, 2, plot_number)
  plt.imshow(piece.outline, cmap=plt.cm.gray)
  plt.plot(piece.center[1], piece.center[0], '*b', markersize=8)
  plt.plot(piece.corners[1], piece.corners[0], 'og', markersize=8)
  plt.axis('off')

plt.show()
#fig.savefig('out.png')
