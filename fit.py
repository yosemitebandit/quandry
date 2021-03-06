"""Fitting puzzle piece images together.

Makes use of data generated by the 'analyze' script.
"""

import json

from quandry import util


# Load the data.
with open('piece-data.json') as piece_data_file:
  piece_data = json.loads(piece_data_file.read())


# Reorganize the data in terms of sides.  Each side is keyed by filepath and
# the side index.
sides = {}
for filepath in piece_data:
  for index, side in enumerate(piece_data[filepath]['sides']):
    key = '%s+%s' % (filepath, index)
    sides[key] = {
      'name': key,
      'type': piece_data[filepath]['side_types'][index],
      'length': piece_data[filepath]['side_lengths'][index],
      'outline': piece_data[filepath]['sides'][index],
    }
ins = [sides[k] for k in sides if sides[k]['type'] == 'in']
outs = [sides[k] for k in sides if sides[k]['type'] == 'out']


# Compare ins and outs.
for in_side in ins:
  print 'analyzing "%s"..' % in_side['name']
  side_length_ratios = []
  for out_side in outs:
    if in_side['name'].split('+')[0] == out_side['name'].split('+')[0]:
      continue
    diff = util.percent_diff(in_side['length'], out_side['length'])
    side_length_ratios.append((out_side['name'], diff))
  hausdorff_scores = []
  for name, ratio in sorted(side_length_ratios, key=lambda v: v[1]):
    if ratio > 10:
      continue
    h_score = util.hausdorff(in_side['outline'], sides[name]['outline'])
    hausdorff_scores.append((name, h_score))
  for h in sorted(hausdorff_scores, key=lambda v: v[1]):
    print '%10s -> %0.2f' % (h[0].split('/')[1], h[1])
