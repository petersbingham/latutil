import csv
import os

from latex import build_pdf
from tabulate import tabulate

min_latex_start = "\documentclass{article}\n\begin{document}"
min_latex_end = "\end{document}"

def _encapsulate_latex(tex_str):
  return min_latex_start + "\n" + tex_str + "\n" + min_latex_end

def _is_path(str):
  return os.sep in str and "\r" not in str

def _create_save_path(str, ext):
  # We assume that str is path to input and try and extract from that
  if not _is_path(str):
    raise Exception("No path was supplied or could be inferred.")
  dir = os.path.dirname(str)
  split_base = os.path.splitext(os.path.basename(str))
  save_path = dir + os.sep + split_base[0] + ext 

def csv_to_latex(str, has_header=True):
  if _is_path(str):
    with open(str, 'r') as f:
      str = f.read()
  if has_header:
    sep = "\n"
    if "\r\n" in str:
      sep = "\r\n"
    split_str = str.split(sep)
    header = split_str[0].split(",")
    body = [line.split(",") for line in str[1:]]
    return tabulate(body, header, tablefmt="latex")
  else:
    body = [line.split(",") for line in str]
    return tabulate(body, tablefmt="latex")

def csv_to_latex_file(str, has_header=True, save_path=None):
  tex_str = csv_to_latex(str, has_header)
  if save_path is None:
    save_path = _create_save_path(str, ".tex")
  with open(save_path, 'w') as f:
    f.write(_encapsulate_latex(tex_str))

def csv_to_pdf(str, has_header=True):
  if _is_path(str):
    with open(str, 'r') as f:
      str = f.read()
  tex_str = csv_to_latex(str, has_header)
  return build_pdf(_encapsulate_latex(tex_str))

def csv_to_pdf_file(str, has_header=True, save_path=None):
  pdf = csv_to_pdf(str, has_header)
  if save_path is None:
    save_path = _create_save_path(str, ".tex")
  pdf.save_to(save_path)
