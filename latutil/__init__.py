import csv
import os

from latex import build_pdf
from tabulate import tabulate

min_latex_start = "\\documentclass{article}\n\\begin{document}"
min_latex_end = "\\end{document}"

def _encapsulate_latex(tex_str):
  return min_latex_start + "\n" + tex_str + "\n" + min_latex_end

def _is_path(input):
  return "\r" not in input

def _create_save_path(input, ext):
  # We assume that input is path to input and try and extract from that
  if not _is_path(input):
    raise Exception("No path was supplied or could be inferred.")
  dir = os.path.dirname(input)
  split_base = os.path.splitext(os.path.basename(input))
  return dir + os.sep + split_base[0] + ext 

def sv_to_latex(input, has_header=True, delimiter=None):
  if _is_path(input):
    with open(input, 'r') as f:
      input = f.read()
  if has_header:
    sep = "\n"
    if "\r\n" in input:
      sep = "\r\n"
    split_input = input.split(sep)
    header = split_input[0].split(delimiter)
    body = [line.split(delimiter) for line in split_input[1:]]
    return tabulate(body, header, tablefmt="latex")
  else:
    body = [line.split(delimiter) for line in input]
    return tabulate(body, tablefmt="latex")

def sv_to_latex_file(input, has_header=True, delimiter=None, save_path=None):
  tex_str = sv_to_latex(input, has_header, delimiter)
  if save_path is None:
    save_path = _create_save_path(input, ".tex")
  with open(save_path, 'w+') as f:
    f.write(_encapsulate_latex(tex_str))

def sv_to_pdf(input, has_header=True, delimiter=None):
  tex_str = sv_to_latex(input, has_header, delimiter)
  return build_pdf(_encapsulate_latex(tex_str))

def sv_to_pdf_file(input, has_header=True, delimiter=None, save_path=None):
  pdf = sv_to_pdf(input, has_header, delimiter)
  if save_path is None:
    save_path = _create_save_path(input, ".pdf")
  pdf.save_to(save_path)
