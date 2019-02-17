import csv
import os

from latex import build_pdf
from tabulate import tabulate

min_latex_start = "\\documentclass{article}"
min_latex_doc_start = "\\begin{document}"
min_latex_end = "\\end{document}"

latex_center_start = "\\begin{table}[]\n\\centering"
latex_center_end = "\\end{table}"

latex_landscape = "\\usepackage[landscape]{geometry}"
latex_thin_margins = "\\geometry{left=20mm, right=20mm, top=25mm, bottom=25mm}"

tablefmt = "latex"

def _encapsulate_latex_table(tex_str, landscape, thin_margins):
  latex = min_latex_start
  if landscape:
    latex += "\n" + latex_landscape
  if thin_margins:
    latex += "\n" + latex_thin_margins
  latex += "\n" + min_latex_doc_start
  latex += "\n" + latex_center_start
  latex += "\n" + tex_str
  latex += "\n" + latex_center_end
  return latex + "\n" + min_latex_end

def _is_path(input):
  return "\r" not in input

def _create_save_path(input, ext):
  # We assume that input is path to input and try and extract from that
  if not _is_path(input):
    raise Exception("No path was supplied or could be inferred.")
  dir = os.path.dirname(input)
  split_base = os.path.splitext(os.path.basename(input))
  return dir + os.sep + split_base[0] + ext 

def sv_to_tex(input, has_header=True, delimiter=None, first_line=None, last_line=None):
  if _is_path(input):
    with open(input, 'r') as f:
      input = f.read()

  sep = "\n"
  if "\r\n" in input:
    sep = "\r\n"
  split_input = input.split(sep)
  if first_line is not None:
    split_input = split_input[first_line-1:]
  if last_line is not None:
    split_input = split_input[:last_line]

  if has_header:
    header = split_input[0].split(delimiter)
    body = [line.split(delimiter) for line in split_input[1:]]
    return tabulate(body, header, tablefmt=tablefmt)
  else:
    body = [line.split(delimiter) for line in split_input]
    return tabulate(body, tablefmt=tablefmt)

def sv_to_tex_file(input, has_header=True, delimiter=None, first_line=None, last_line=None,
                   landscape=False, thin_margins=False, save_path=None):
  tex_str = sv_to_tex(input, has_header, delimiter, first_line, last_line)
  if save_path is None:
    save_path = _create_save_path(input, ".tex")
  with open(save_path, 'w+') as f:
    f.write(_encapsulate_latex_table(tex_str, landscape, thin_margins))

def sv_to_pdf(input, has_header=True, delimiter=None, first_line=None, last_line=None,
              landscape=False, thin_margins=False):
  tex_str = sv_to_tex(input, has_header, delimiter, first_line, last_line)
  return build_pdf(_encapsulate_latex_table(tex_str, landscape, thin_margins))

def sv_to_pdf_file(input, has_header=True, delimiter=None, first_line=None, last_line=None, 
                   landscape=False, thin_margins=False, save_path=None):
  pdf = sv_to_pdf(input, has_header, delimiter, first_line, last_line, landscape, thin_margins)
  if save_path is None:
    save_path = _create_save_path(input, ".pdf")
  pdf.save_to(save_path)
