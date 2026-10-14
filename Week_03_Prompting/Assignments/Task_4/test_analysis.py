"""Check inferential calculations against small, hand-verifiable examples."""

import unittest

import numpy as np

from analyze import holm, mcnemar, paired_ci, permutation_p


class StatisticalTests(unittest.TestCase):
    def test_exact_mcnemar(self):
        self.assertEqual(mcnemar(0, 0), 1)
        self.assertEqual(mcnemar(4, 0), 0.125)
        self.assertEqual(mcnemar(2, 2), 1)
        self.assertAlmostEqual(mcnemar(14, 6), 0.11531829833984375)
        self.assertEqual(mcnemar(14, 6), mcnemar(6, 14))

    def test_exact_permutation(self):
        # Four positive differences: only all-plus/all-minus are as extreme.
        self.assertEqual(permutation_p([1, 1, 1, 1]), 2 / 16)
        self.assertEqual(permutation_p([0, 0, 0]), 1)
        self.assertEqual(permutation_p([1, -1]), 1)
        # Sums are +/-3 and +/-1; the observed sum is 1, so every flip qualifies.
        self.assertEqual(permutation_p([2, -1]), 1)
        self.assertEqual(permutation_p([2, 1]), .5)
        self.assertEqual(permutation_p([0, .2, .1]), .5)
        self.assertEqual(permutation_p([-.2, -.1]), .5)

    def test_holm_in_original_order(self):
        np.testing.assert_allclose(holm([.04, .001, .03]), [.06, .003, .06])
        self.assertEqual(holm([1, 1]), [1, 1])

    def test_paired_bootstrap_and_stratum_weights(self):
        mask = np.array([True, False, False, False])
        # Constant within each stratum: every balanced resample must be 0.5.
        low, high = paired_ci([0, 1, 1, 1], mask, True, 2026, 1000)
        self.assertEqual((low, high), (.5, .5))
        self.assertEqual(paired_ci([0] * 4, mask, False, 2026, 1000), (0, 0))
        self.assertEqual(paired_ci([0, 1, 0, -1], mask, False, 2026, 1000),
                         paired_ci([0, 1, 0, -1], mask, False, 2026, 1000))


if __name__ == "__main__":
    unittest.main()
