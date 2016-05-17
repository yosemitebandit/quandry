"""Tests for quandry.compare.shaped_like_a_side."""

import json
import os
import unittest

from quandry import compare


fixtures_path = 'quandry/tests/fixtures'


class GoodSidesTest(unittest.TestCase):
  """Testing paths that should be classified as sides."""

  @classmethod
  def setUpClass(cls):
    piece_four_path = os.path.join(
      fixtures_path, 'piece-four-questionable-E.json')
    with open(piece_four_path) as piece_four_file:
      cls.piece_four_data = json.loads(piece_four_file.read())

  def test_in_side(self):
    """'In' sides should pass."""
    in_side = self.piece_four_data['sides'][2]
    self.assertEqual(True, compare.shaped_like_a_side(in_side))

  def test_out_side(self):
    """'Out' sides should pass."""
    out_side = self.piece_four_data['sides'][3]
    self.assertEqual(True, compare.shaped_like_a_side(out_side))

  def test_flat_side(self):
    """Flat sides are sides too."""
    flat_side = self.piece_four_data['sides'][0]
    self.assertEqual(True, compare.shaped_like_a_side(flat_side))


class BadSidesTest(unittest.TestCase):
  """These various paths should not be classified as sides."""

  @classmethod
  def setUpClass(cls):
    piece_one_path = os.path.join(fixtures_path, 'piece-one-bad-N-W-S.json')
    piece_five_path = os.path.join(fixtures_path, 'piece-five-bad-N-W.json')
    with open(piece_one_path) as piece_one_file:
      cls.piece_one_data = json.loads(piece_one_file.read())
    with open(piece_five_path) as piece_five_file:
      cls.piece_five_data = json.loads(piece_five_file.read())

  def test_piece_one_north_side(self):
    north_side = self.piece_one_data['sides'][0]
    self.assertEqual(False, compare.shaped_like_a_side(north_side))

  def test_piece_one_west_side(self):
    west_side = self.piece_one_data['sides'][3]
    self.assertEqual(False, compare.shaped_like_a_side(west_side))

  def test_piece_one_south_side(self):
    south_side = self.piece_one_data['sides'][2]
    self.assertEqual(False, compare.shaped_like_a_side(south_side))

  def test_piece_five_north_side(self):
    north_side = self.piece_five_data['sides'][0]
    self.assertEqual(False, compare.shaped_like_a_side(north_side))

  def test_piece_five_west_side(self):
    west_side = self.piece_five_data['sides'][3]
    self.assertEqual(False, compare.shaped_like_a_side(west_side))
