from __future__ import absolute_import

import sys
import os

path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

import argparse
import tutil

parser = argparse.ArgumentParser(description='Execute table utility.')
parser.add_argument('function_name', help='function to execute.',
                    choices=['sv_to_tex', 'sv_to_pdf', 'tex_to_pdf'])
parser.add_argument('input_file', help='input file for the utility.')
parser.add_argument('--delimiter', '-d', help='set the column delimiter. Default is whitespace.',
                    nargs='?', default=None)
parser.add_argument('--has_header', '-H', help='flag for first line in table file describing header.',
                    action='store_true')
parser.add_argument('--left_aligned_to_header', '-L', help='flag to only delimit the header and then to align cells to their column header position.',
                    action='store_true')
parser.add_argument('--right_aligned_to_header', '-R', help='as for left_aligned_to_header except header titles right aligned.',
                    action='store_true')
parser.add_argument('--has_header_gap', '-g', help='set the number of lines to ignore between the header and first row. Default is zero',
                    nargs='?', default=0, type=int)
parser.add_argument('--start_line', '-s', help='set the first line of the table. Default is start of file.',
                    nargs='?', default=None, type=int)
parser.add_argument('--end_line', '-e', help='set the last line of the table. Default is end of file.',
                    nargs='?', default=None, type=int)
parser.add_argument('--create_landscape', '-l', help='flag to create a landscape orientated tex, instead of portrait.',
                    action='store_true')
parser.add_argument('--create_thin_margins', '-t', help='flag to create thin margined tex.',
                    action='store_true')
parser.add_argument('--create_raw_latex', '-r', help='flag to not escape special latex characters in created tex.',
                    action='store_true')
parser.add_argument('--create_big_table', '-b', help='flag to indicate that created table is likely to span multiple pages.',
                    action='store_true')
parser.add_argument('--create_lines_horz', '-Z', help='flag to add horizontal lines separating the rows.',
                    action='store_true')
args = parser.parse_args()

if args.create_raw_latex:
  tutil.tablefmt = "latex_raw"

arg_list = (args.input_file, args.delimiter, args.has_header, args.left_aligned_to_header, args.right_aligned_to_header,
            args.has_header_gap, args.start_line, args.end_line,
            args.create_landscape, args.create_thin_margins, args.create_big_table, args.create_lines_horz)

if args.function_name == "sv_to_tex":
  tutil.sv_to_tex_file(*arg_list)
elif args.function_name == "sv_to_pdf":
  tutil.sv_to_pdf_file(*arg_list)
elif args.function_name == "tex_to_pdf":
  tutil.tex_to_pdf_file(args.input_file)
