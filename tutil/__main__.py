from __future__ import absolute_import

import sys
import os

path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

import argparse
import tutil

parser = argparse.ArgumentParser(description='Execute table utility.')
parser.add_argument('output_type', help='Name/s of output types to generate. String will be searched for the types. Examples: pdf, texpdf, pdf_tex')
parser.add_argument('input_file', help='input file containing the ascii table to convert.')
parser.add_argument('--input_type', '-t', help='input table type. Default is sv (separated values).',
                    nargs='?', default='sv', choices=['sv', 'tex'], type=str)
parser.add_argument('--caption', '-c', help='set the table caption.',
                    nargs='?', default=None)
parser.add_argument('--name', '-n', help='set the table name.',
                    nargs='?', default=None)
parser.add_argument('--delimiter', '-d', help='set the column delimiter. Default is whitespace.',
                    nargs='?', default=None)
parser.add_argument('--has_header', '-H', help='flag for first line in table file describing header.',
                    action='store_true')
parser.add_argument('--left_aligned_to_header', '-l', help='flag to only delimit the header and then to align cells to their column header position.',
                    action='store_true')
parser.add_argument('--right_aligned_to_header', '-r', help='as for left_aligned_to_header except header titles right aligned.',
                    action='store_true')
parser.add_argument('--header_gap_size', '-g', help='set the number of lines to ignore between the header and first row. Default is zero',
                    nargs='?', default=0, type=int)
parser.add_argument('--num_lbl_cols', '-C', help='set the number of columns used as labels. Default is zero',
                    nargs='?', default=0, type=int)
parser.add_argument('--start_line', '-s', help='set the first line of the table. Default is start of file.',
                    nargs='?', default=None, type=int)
parser.add_argument('--end_line', '-e', help='set the last line of the table. Default is end of file.',
                    nargs='?', default=None, type=int)
parser.add_argument('--num_table_splits', '-S', help='set the number of times the table should be split. Columns labels are include in each split table. Default is zero',
                    nargs='?', default=0, type=int)
parser.add_argument('--transpose', '-f', help='flag to transpose table.',
                    action='store_true')
parser.add_argument('--formula', '-F', help='command to modify the data. eg "+1" adds 1 to all data. "+[i][0]" adds the first value in each row to all other values in that row. Note requires enclosing "", to remove cli issues with minus signs.',
                    nargs='?', default=None)
parser.add_argument('--tex_lines_horz', '-z', help='flag to add horizontal lines separating the rows.',
                    action='store_true')
parser.add_argument('--tex_raw', '-R', help='flag to not escape special latex characters in created tex.',
                    action='store_true')
parser.add_argument('--tex_big_table', '-b', help='flag to indicate that created table is likely to span multiple pages.',
                    action='store_true')
parser.add_argument('--tex_landscape', '-L', help='flag to create a landscape orientated tex, instead of portrait.',
                    action='store_true')
parser.add_argument('--tex_thin_margins', '-T', help='flag to create thin margined tex.',
                    action='store_true')
parser.add_argument('--plot_command', '-p', help='command to specify the plot. eg 1:* plots column 1 as x axis against all others.',
                    nargs='?', default=None)
parser.add_argument('--plot_interactive', '-i', help='flag to show interactive plot.',
                    action='store_true')
args = parser.parse_args()

if args.tex_raw:
  tutil.latextablefmt = 'latex_raw'

has_header = False
if args.has_header or args.header_gap_size > 0:
  has_header = True

if 'sv' == args.input_type:
  arg_list = [args.input_file, args.caption, args.name, args.delimiter, has_header, args.left_aligned_to_header,
              args.right_aligned_to_header, args.header_gap_size, args.num_lbl_cols, args.start_line, args.end_line,
              args.transpose, args.formula]
  if 'plot' in args.output_type:
    if 'gnuplot' in args.output_type:
      tutil.sv_to_gnuplot_file(*arg_list)
    elif 'splot' == args.output_type:
      arg_list.extend([args.plot_command, args.plot_interactive])
      tutil.sv_to_splot_files(*arg_list)
  else:
    arg_list.extend([args.num_table_splits,
                     args.tex_lines_horz, args.tex_big_table, args.tex_landscape, args.tex_thin_margins])
    if 'tex' in args.output_type:
      tutil.sv_to_tex_file(*arg_list)
    elif 'pdf' in args.output_type:
      tutil.sv_to_pdf_file(*arg_list)
elif 'tex' == args.input_type:
  tutil.tex_to_pdf_file(args.input_file)
