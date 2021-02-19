import unittest

import numpy as np

from Orange.classification import CatGBClassifier
from Orange.data import Table
from Orange.evaluation import CrossValidation, CA
from Orange.preprocess.score import Scorer


class TestCatGBClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.iris = Table("iris")

    def test_GBTrees(self):
        booster = CatGBClassifier()
        cv = CrossValidation(k=3)
        results = cv(self.iris, [booster])
        ca = CA(results)
        self.assertGreater(ca, 0.9)
        self.assertLess(ca, 0.99)

    def test_predict_single_instance(self):
        booster = CatGBClassifier()
        model = booster(self.iris)
        for ins in self.iris:
            model(ins)
            prob = model(ins, model.Probs)
            self.assertGreaterEqual(prob.all(), 0)
            self.assertLessEqual(prob.all(), 1)
            self.assertAlmostEqual(prob.sum(), 1, 3)

    def test_predict_table(self):
        booster = CatGBClassifier()
        model = booster(self.iris)
        pred = model(self.iris)
        self.assertEqual(pred.shape, (len(self.iris),))
        prob = model(self.iris, model.Probs)
        self.assertGreaterEqual(prob.all().all(), 0)
        self.assertLessEqual(prob.all().all(), 1)
        self.assertAlmostEqual(prob.sum(), len(self.iris))

    def test_predict_numpy(self):
        booster = CatGBClassifier()
        model = booster(self.iris)
        pred = model(self.iris.X)
        self.assertEqual(pred.shape, (len(self.iris),))
        prob = model(self.iris.X, model.Probs)
        self.assertGreaterEqual(prob.all().all(), 0)
        self.assertLessEqual(prob.all().all(), 1)
        self.assertAlmostEqual(prob.sum(), len(self.iris))

    def test_predict_sparse(self):
        sparse_data = self.iris.to_sparse()
        booster = CatGBClassifier()
        model = booster(sparse_data)
        pred = model(sparse_data)
        self.assertEqual(pred.shape, (len(sparse_data),))
        prob = model(sparse_data, model.Probs)
        self.assertGreaterEqual(prob.all().all(), 0)
        self.assertLessEqual(prob.all().all(), 1)
        self.assertAlmostEqual(prob.sum(), len(sparse_data))

    def test_set_params(self):
        booster = CatGBClassifier(n_estimators=42, max_depth=4)
        self.assertEqual(booster.params["n_estimators"], 42)
        self.assertEqual(booster.params["max_depth"], 4)
        model = booster(self.iris)
        params = model.cat_model.get_params()
        self.assertEqual(params["n_estimators"], 42)
        self.assertEqual(params["max_depth"], 4)

    def test_scorer(self):
        booster = CatGBClassifier()
        self.assertIsInstance(booster, Scorer)
        booster.score(self.iris)

    def test_discrete_variables(self):
        data = Table("zoo")
        booster = CatGBClassifier()
        cv = CrossValidation(k=3)
        results = cv(data, [booster])
        ca = CA(results)
        self.assertGreater(ca, 0.9)
        self.assertLess(ca, 0.99)

        data = Table("titanic")
        booster = CatGBClassifier()
        cv = CrossValidation(k=3)
        results = cv(data, [booster])
        ca = CA(results)
        self.assertGreater(ca, 0.75)
        self.assertLess(ca, 0.99)

    def test_missing_values(self):
        data = Table("heart_disease")
        booster = CatGBClassifier()
        cv = CrossValidation(k=3)
        results = cv(data, [booster])
        ca = CA(results)
        self.assertGreater(ca, 0.8)
        self.assertLess(ca, 0.99)

    def test_retain_x(self):
        data = Table("heart_disease")
        X = data.X.copy()
        booster = CatGBClassifier()
        model = booster(data)
        model(data)
        np.testing.assert_array_equal(data.X, X)
        self.assertEqual(data.X.dtype, X.dtype)


if __name__ == "__main__":
    unittest.main()