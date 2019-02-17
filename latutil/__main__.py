from __future__ import absolute_import

import sys
import os

path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

import argparse
import latutil

parser = argparse.ArgumentParser(description='Execute latex utility.')
parser.add_argument('utility_name', help='utility to execute.',
                    choices=['sv_to_latex', 'sv_to_pdf'])
parser.add_argument('input_file', help='Input file for the utility.')
parser.add_argument('--header', '-H', help='First line in input file describes header.',
                    action='store_true')
parser.add_argument('--delimiter', '-d', nargs='?', default=None)
args = parser.parse_args()

if args.utility_name == "sv_to_latex":
  latutil.sv_to_latex_file(args.input_file, args.header, args.delimiter)
elif args.utility_name == "sv_to_pdf":
  latutil.sv_to_pdf_file(args.input_file, args.header, args.delimiter)
