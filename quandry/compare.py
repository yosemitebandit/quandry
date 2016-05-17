"""Comparisons."""

import json
import os

from quandry import util


def shaped_like_a_side(side_data):
  """Determines if the given side data is actually shaped like a side.

  Sides may be flat, out-shaped or in-shaped (the latter two being
  indistinguishable when looking at just a single shape).

  Arguments:
    side_data: a list of (x, y) tuples

  Returns a boolean.
  """
  fixtures_path = 'quandry/fixtures/'
  piece_six_path = os.path.join(fixtures_path, 'piece-six.json')
  with open(piece_six_path) as piece_six_file:
    canonical_out_side = json.loads(piece_six_file.read())['sides'][1]
  out_score = util.hausdorff(side_data, canonical_out_side)
  print 'out score: %s' % out_score
  if out_score < 10:
    #return True
    pass

  piece_three_path = os.path.join(fixtures_path, 'piece-three.json')
  with open(piece_three_path) as piece_three_file:
    canonical_flat_side = json.loads(piece_three_file.read())['sides'][0]
  flat_score = util.hausdorff(side_data, canonical_flat_side)
  print 'flat score: %s' % flat_score
  if flat_score < 10:
    #return True
    pass
  # Both "out" and "flat" tests failed, so we'll call this not a side.
  #return False
