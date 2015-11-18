"""Enhancing raw images.

Usage:
  enhance.py <filepath> [--outdir=<outdir>]

Arguments:
  filepath  the path to an image file

Options:
  --outdir=<outdir>  where to save enhanced images
"""

import os

from docopt import docopt
from PIL import Image
from PIL import ImageOps


if __name__ == '__main__':
  args = docopt(__doc__)
  filepath = args['<filepath>']
  image = Image.open(filepath)
  enhanced = ImageOps.autocontrast(image)
  extensionless_filename = filepath.split('.')[0]
  outpath = '%s-enhanced.png' % extensionless_filename
  if args['--outdir']:
    outpath = os.path.join(args['--outdir'], outpath)
    savedir = os.path.dirname(outpath)
    if not os.path.exists(savedir):
      os.makedirs(savedir)
  enhanced.save(outpath)
