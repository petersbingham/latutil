import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

import unittest
import latutil

class TestFiles(unittest.TestCase):
    def test_sv_to_latex(self):
      latutil.sv_to_latex_file("./test.csv", delimiter=",")
      self.assertTrue(os.path.exists("./test.tex"))
    
    def test_sv_to_pdf(self):
      latutil.sv_to_pdf_file("./test.csv", delimiter=",")
      self.assertTrue(os.path.exists("./test.pdf"))

if __name__ == "__main__":
    #Just for debug
    b = test_history()
    b.runTest()
