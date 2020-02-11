import os
import sys
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,basedir+'/../..')

import filecmp
import unittest
import tutil

class TestFiles(unittest.TestCase):
    def test_sv_to_tex(self):
       tutil.sv_to_tex_file("./test.csv", has_header=True, delimiter=",")
       self.assertTrue(filecmp.cmp("./test.tex", "./test-exp.tex"))
     
    def test_sv_to_tex_tran(self):
       tutil.sv_to_tex_file("./test.csv", has_header=True, delimiter=",", transpose=True)
       self.assertTrue(filecmp.cmp("./test.tex", "./test-tran-exp.tex"))

    def test_sv_to_pdf(self):
      tutil.sv_to_pdf_file("./test.csv", delimiter=",")
      self.assertTrue(os.path.exists("./test.pdf"))

if __name__ == "__main__":
    unittest.main()
