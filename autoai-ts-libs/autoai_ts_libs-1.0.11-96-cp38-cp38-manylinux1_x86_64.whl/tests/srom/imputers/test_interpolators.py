import unittest 
import pandas as pd
import numpy as np
from autoai_ts_libs.srom.imputers.interpolators import InterpolateImputer,PolynomialImputer,SplineImputer,CubicImputer,QuadraticImputer,AkimaImputer,LinearImputer,BaryCentricImputer,PreMLImputer

class TestInterpolators(unittest.TestCase):
    """ class for testing different Interpolators"""
    @classmethod
    def setUp(cls):
        uni_x = pd.DataFrame({"A":[12, 4, 5, None, 1]})
        multi_x = pd.DataFrame({"A":[12, 4, 5, None, 1],
                   "B":[None, 2, 54, 3, None],
                   "C":[20, 16, None, 3, 8],
                   "D":[14, 3, None, None, 6]})
        cls.uni_x = uni_x
        cls.multi_x = multi_x

    
    def test_interpolate_imputer(self):
        """ Test  InterpolateImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = InterpolateImputer(time_column=-1,
        missing_values=np.nan,
        method="linear",
        )
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.nanmean(X_tf),5.0,2)
        
        #Test multivariate
        imputer = InterpolateImputer(time_column=-1,
        missing_values=np.nan,
        method="linear",
        )
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.nanmean(X_tf),9.2368,2)
        
        #Test numpy
        imputer = InterpolateImputer(time_column=-1,
        missing_values=np.nan,
        method="linear",
        )
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.nanmean(X_tf),5.0,2)
        
        #Test numpy
        imputer = InterpolateImputer(time_column=-1,
        missing_values=np.nan,
        method="linear",
        )
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.nanmean(X_tf),9.2368,2)
            
    def test_polynomial_imputer(self):
        """ Test  PolynomialImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = PolynomialImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf),5.0,2)
        
        #Test multivariate
        imputer = PolynomialImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),8.875,2)
        
        #Test numpy
        imputer = PolynomialImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf),5.0,2)
        
        #Test numpy
        imputer = PolynomialImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf),8.875,2)

    def test_spline_imputer(self):
        """ Test  SplineImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = SplineImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 4.9174,2)
        
        #Test multivariate
        imputer = SplineImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),6.51,2)
        
        #Test numpy
        imputer = SplineImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 4.9174,2)
        
        #Test numpy
        imputer = SplineImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf),6.51,2)

    def test_cubic_imputer(self):
        """ Test  CubicImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x[["A","C"]]
        
        #Test univariate
        imputer = CubicImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf),  5.75,2)
        
        #Test multivariate
        imputer = CubicImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),8.375,2)
        
        #Test numpy
        imputer = CubicImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf),  5.75,2)
        
        #Test numpy
        imputer = CubicImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf),8.375,2)

    def test_quadratic_imputer(self):
        """ Test  QuadraticImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = QuadraticImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.3157,2)
        
        #Test multivariate
        imputer = QuadraticImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),8.2789,2)
        
        #Test numpy
        imputer = QuadraticImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 5.3157,2)
        
        #Test numpy
        imputer = QuadraticImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf),8.2789,2)

    def test_akima_imputer(self):
        """ Test  AkimaImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = AkimaImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.1125,2)
        
        #Test multivariate
        imputer = AkimaImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf), 8.5031,2)
        
        #Test numpy
        imputer = AkimaImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 5.1125,2)
        
        #Test numpy
        imputer = AkimaImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 8.5031,2)

    def test_linear_imputer(self):
        """ Test  LinearImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = LinearImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test multivariate
        imputer = LinearImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf), 8.875,2)
        
        #Test numpy
        imputer = LinearImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test numpy
        imputer = LinearImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 8.875,2)

    def test_bary_centric_imputer(self):
        """ Test  BaryCentricImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = BaryCentricImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.75,2)
        
        #Test multivariate
        imputer = BaryCentricImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf), 0.6874,2)
        
        #Test numpy
        imputer = BaryCentricImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 5.75,2)
        
        #Test numpy
        imputer = BaryCentricImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 0.6874,2)

    def test_pre_ml_imputer(self):
        """ Test  PreMLImputer """
        test_class = self.__class__
        uni_x = test_class.uni_x
        multi_x = test_class.multi_x
        
        #Test univariate
        imputer = PreMLImputer()
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test multivariate
        imputer = PreMLImputer()
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),  8.5031,2)
        
        #Test numpy
        imputer = PreMLImputer()
        X_tf = imputer.transform(uni_x.values)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test numpy
        imputer = PreMLImputer()
        X_tf = imputer.transform(multi_x.values)
        self.assertAlmostEqual(np.mean(X_tf),  8.5031,2)

    def test_other_missing_values(self):
        test_class = self.__class__
        uni_x = pd.DataFrame({"A":[12, 4, 5, -999, 1]})
        multi_x = pd.DataFrame({"A":[12, 4, 5, -999, 1],
                   "B":[-999, 2, 54, 3, -999],
                   "C":[20, 16, -999, 3, 8],
                   "D":[14, 3, -999, -999, 6]})
        
        #Test univariate
        imputer = LinearImputer(missing_values=-999)
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test multivariate
        imputer = LinearImputer(missing_values=-999)
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf), 8.875,2)

        #Test univariate
        imputer = PreMLImputer(missing_values=-999)
        X_tf = imputer.transform(uni_x)
        self.assertAlmostEqual(np.mean(X_tf), 5.0,2)
        
        #Test multivariate
        imputer = PreMLImputer(missing_values=-999)
        X_tf = imputer.transform(multi_x)
        self.assertAlmostEqual(np.mean(X_tf),  8.5031,2)
        
    def test_none_input(self):
        test_class = self.__class__
        uni_x = None
        #Test univariate
        imputer = LinearImputer()
        X_tf = imputer.transform(uni_x)
        self.assertIsNone(X_tf)
        
        #Test univariate
        imputer = PreMLImputer()
        X_tf = imputer.transform(uni_x)
        self.assertIsNone(X_tf)
        
    def test_no_missing_values(self):
        test_class = self.__class__
        uni_x = pd.DataFrame({"A":[12, 4, 5, 9, 1]})
        multi_x = pd.DataFrame({"A":[12, 4, 5, 9, 1],
                   "B":[9, 2, 54, 3, 9],
                   "C":[20, 16, 9, 3, 8],
                   "D":[14, 3, 9, 9, 6]})
        
        imputer = LinearImputer()
        X_tf = imputer.transform(uni_x)
        np.testing.assert_array_almost_equal(X_tf,uni_x)
        
        imputer = LinearImputer()
        X_tf = imputer.transform(multi_x)
        np.testing.assert_array_almost_equal(X_tf,multi_x)
        
        imputer = PreMLImputer()
        X_tf = imputer.transform(uni_x)
        np.testing.assert_array_almost_equal(X_tf,uni_x)
        
        imputer = PreMLImputer()
        X_tf = imputer.transform(multi_x)
        np.testing.assert_array_almost_equal(X_tf,multi_x)
        


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
