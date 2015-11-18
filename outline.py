"""Generates outline for a piece.

Saves output data in a json file, and optionally saves a plot of the analyzed
data.  Low and high segmentation thresholds may also be set.

Usage:
  outline.py <filepath> [--low=<low>] [--high=<high>] [--plot]

Arguments:
  filepath  the path to an image file

Options:
  --plot  shows the output plot
  --low=<low>  the low segmentation threshold [default: 50]
  --high=<high>  the high segmentation threshold [default: 110]
"""

import json
import os

from docopt import docopt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from quandry import JigsawPiece


if __name__ == '__main__':
  args = docopt(__doc__)
  filepath = args['<filepath>']
  low_threshold = int(args['--low'])
  high_threshold = int(args['--high'])
  piece_data = {}

  # Setup each axis.
  if args['--plot']:
    figure_grid = gridspec.GridSpec(1, 2)
    figure_grid.update(wspace=0.025, hspace=0.05)
    ax0 = plt.subplot(figure_grid[0, 0])
    ax1 = plt.subplot(figure_grid[0, 1])
    ax0.axis('off')
    ax1.axis('off')
    ax0.set_aspect('equal')
    ax1.set_aspect('equal')

  # Start processing the image.
  print 'processing "%s"..' % filepath
  piece = JigsawPiece(filepath)
  if args['--plot']:
    ax0.imshow(piece.raw_image, aspect='equal')
  piece_data[filepath] = {}
  piece_data[filepath]['raw_image'] = piece.raw_image.tolist()

  # Get contours.
  try:
    piece.segment(low_threshold=low_threshold, high_threshold=high_threshold)
    if args['--plot']:
      ax0.plot(piece.outline[:, 0], -piece.outline[:, 1], color='green')
      ax1.plot(piece.outline[:, 0], piece.outline[:, 1], color='gray')
    piece_data[filepath]['outline'] = piece.outline.tolist()
  except:
    print 'could not find contours for "%s"' % filepath

  # Set the raw image's axis limits to match the derived data's axis.
  if args['--plot']:
    ax0.axes.set_xlim(ax1.axes.get_xlim())
    y_min, y_max = ax1.axes.get_ylim()
    ax0.axes.set_ylim((-y_min, -y_max))

  # Save the figure.
  filename = os.path.basename(filepath)
  extensionless_filename = filename.split('.')[0]
  directory = os.path.dirname(filepath)
  if args['--plot']:
    output_figure_path = os.path.join(
      directory, '%s-outline.png' % extensionless_filename)
    figure = plt.gcf()
    figure.savefig(output_figure_path, dpi=200)

  # Save the output data.
  output_data_path = os.path.join(
    directory, '%s-outline.json' % extensionless_filename)
  with open(output_data_path, 'w') as piece_data_file:
    piece_data_file.write(json.dumps(piece_data))
