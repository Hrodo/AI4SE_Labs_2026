"""Check scoring conventions and execution behavior independently of run scores."""

import unittest

from metric import DEFAULT_DATA, balanced_f1, evaluate, execute_prediction, load_database, result_f1


class ResultF1Tests(unittest.TestCase):
    def test_empty_answer_conventions(self):
        self.assertEqual(result_f1([], []), 1)
        self.assertEqual(result_f1([], [(1, "a")]), 0)
        self.assertEqual(result_f1([(1, "a")], []), 0)

    def test_partial_retrieval_and_extra_rows(self):
        expected = [(1, "a"), (2, "b"), (3, "c")]
        self.assertAlmostEqual(result_f1(expected, expected[:2]), 0.8)
        self.assertAlmostEqual(result_f1(expected, expected[:2] + [(4, "d")]), 2 / 3)

    def test_multiset_and_column_order(self):
        rows = [(1, "a"), (2, "b")]
        self.assertEqual(result_f1(rows, rows[::-1]), 1)
        self.assertAlmostEqual(result_f1([(1, "a")], [(1, "a"), (1, "a")]), 2 / 3)
        self.assertEqual(result_f1([(1, "a")], [("a", 1)]), 0)

    def test_balancing_prevents_empty_majority_from_dominating(self):
        records = [{"expected_count": 0, "f1": 1.0}] * 9
        records += [{"expected_count": 1, "f1": 0.0}]
        self.assertEqual(balanced_f1(records), 0.5)
        self.assertEqual(balanced_f1(records[:9]), 1)
        with self.assertRaises(ValueError):
            balanced_f1([])


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.connection = load_database(DEFAULT_DATA)

    def tearDown(self):
        self.connection.close()

    def test_error_on_empty_reference_is_zero(self):
        labels = [{"question": "q", "result": "[]"}]
        predictions = [{"question": "q", "predicted_sql": "SELECT missing FROM RESTAURANT"}]
        row = evaluate(self.connection, labels, predictions)[0]
        self.assertEqual(row["f1"], 0)
        self.assertEqual(row["exact_match"], 0)
        self.assertTrue(row["execution_error"])

    def test_duplicate_questions_preserve_occurrence(self):
        labels = [{"question": "q", "result": "[[1, \"a\"]]"},
                  {"question": "q", "result": "[]"}]
        predictions = [{"question": "q", "predicted_sql": "SELECT 1, 'a'"},
                       {"question": "q", "predicted_sql": "SELECT 1, 'a' WHERE 0"}]
        rows = evaluate(self.connection, labels, predictions)
        self.assertEqual([row["f1"] for row in rows], [1, 1])
        with self.assertRaises(ValueError):
            evaluate(self.connection, labels, predictions[:1])
        with self.assertRaises(ValueError):
            evaluate(self.connection, labels[:1], [{"question": "other", "predicted_sql": "SELECT 1"}])

    def test_mutation_denied_and_subsequent_query_works(self):
        count = execute_prediction(self.connection, "SELECT COUNT(*) FROM RESTAURANT")
        row = evaluate(self.connection, [{"question": "q", "result": "[]"}],
                       [{"question": "q", "predicted_sql": "DELETE FROM RESTAURANT"}])[0]
        self.assertTrue(row["execution_error"])
        self.assertEqual(execute_prediction(self.connection, "SELECT COUNT(*) FROM RESTAURANT"), count)

    def test_instruction_budget_stops_infinite_query(self):
        row = evaluate(self.connection, [{"question": "q", "result": "[]"}],
                       [{"question": "q", "predicted_sql":
                         "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT SUM(x) FROM n"}])[0]
        self.assertTrue(row["execution_error"])
        self.assertEqual(row["f1"], 0)
        self.assertEqual(execute_prediction(self.connection, "SELECT 1"), [(1,)])


if __name__ == "__main__":
    unittest.main()
