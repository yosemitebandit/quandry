"""Puzzle piece image processing."""

import os

import matplotlib.pyplot as plt

from quandry import JigsawPiece


filepaths = ('a.jpg', 'b.jpg', 'c.jpg', 'd.jpg', 'e.jpg', 'f.jpg')
subplot_rows = len(filepaths)
plot_number = 0

for path in filepaths:
  # Calculate the piece data.
  print 'processing "%s"..' % path
  path = os.path.join('sample-pieces/', path)
  piece = JigsawPiece(path)
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
