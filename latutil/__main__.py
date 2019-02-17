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
parser.add_argument('input_file', help='input file for the utility.')
parser.add_argument('--header', '-H', help='set if first line in input file describes a header.',
                    action='store_true')
parser.add_argument('--delimiter', '-d', help='set the column delimiter. Default is whitespace.',
                    nargs='?', default=None)
parser.add_argument('--start_line', '-s', help='set the first line of the table. Default is start of file.',
                    nargs='?', default=None, type=int)
parser.add_argument('--end_line', '-e', help='set the last line of the table. Default is end of file.',
                    nargs='?', default=None, type=int)
args = parser.parse_args()

if args.utility_name == "sv_to_latex":
  latutil.sv_to_latex_file(args.input_file, args.header, args.delimiter, args.start_line, args.end_line)
elif args.utility_name == "sv_to_pdf":
  latutil.sv_to_pdf_file(args.input_file, args.header, args.delimiter, args.start_line, args.end_line)
