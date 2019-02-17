import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

import unittest
import latutil

class test_test_files(unittest.TestCase):
    def test_csv_to_latex(self):
      latutil.csv_to_latex_file("./test.csv")
      self.assertTrue(os.path.exists("./test.tex"))
    
    def test_csv_to_pdf(self):
      latutil.csv_to_pdf_file("./test.csv")
      self.assertTrue(os.path.exists("./test.pdf"))

if __name__ == "__main__":
    #Just for debug
    b = test_history()
    b.runTest()
