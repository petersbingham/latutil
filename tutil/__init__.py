import csv
import os

from latex import build_pdf
from tabulate import tabulate

min_latex_start = "\\documentclass{article}"
latex_long_table_package = "\\usepackage{longtable}"
min_latex_doc_start = "\\begin{document}"
min_latex_end = "\\end{document}"

latex_center_start = "\\begin{table}{}\n\\centering"
latex_center_end = "\\end{table}"

latex_create_landscape = "\\usepackage[create_landscape]{geometry}"
latex_create_thin_margins = "\\usepackage{geometry}\geometry{left=20mm, right=20mm, top=25mm, bottom=25mm}"

tablefmt = "latex"

def _encapsulate_latex_table(tex_str, create_landscape, create_thin_margins, create_long_table, create_lines):
  latex = min_latex_start
  if create_long_table:
    tex_str = tex_str.replace("{tabular}", "{longtable}")
    latex += "\n" + latex_long_table_package
  if create_landscape:
    latex += "\n" + latex_create_landscape
  if create_thin_margins:
    latex += "\n" + latex_create_thin_margins
  latex += "\n" + min_latex_doc_start
  if not create_long_table:
    latex += "\n" + latex_center_start
  if create_lines:
    tex_str = tex_str.replace(r'\hline','').replace(r'\\',r'\\\hline')
  latex += "\n" + tex_str
  if not create_long_table:
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

def _get_table_str(input):
  if _is_path(input):
    with open(input, 'r') as f:
      input = f.read()
  return input

def _save_pdf(pdf, input, save_path):
  if save_path is None:
    save_path = _create_save_path(input, ".pdf")
  pdf.save_to(save_path)

def sv_to_tex(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
              has_header_gap=0, start_line=None, end_line=None):
  input = _get_table_str(input)

  sep = "\n"
  if "\r\n" in input:
    sep = "\r\n"
  split_input = input.split(sep)

  if start_line is not None and end_line is not None:
    split_input = split_input[start_line-1:end_line]
  elif start_line is not None:
    split_input = split_input[start_line-1:]
  elif end_line is not None:
    split_input = split_input[:end_line]

  if has_header:
    header = split_input[0].split(delimiter)
    if not left_aligned_to_header and not right_aligned_to_header:
      body = [line.split(delimiter) for line in split_input[1+has_header_gap:]]
    else:
      cell_poss = []
      for title in header:
        if left_aligned_to_header:
          cell_poss.append(split_input[0].index(title)+1)
        else: 
          cell_poss.append(split_input[0].index(title)+len(title)+1)
      body = []
      for line in split_input[1+has_header_gap:]:
        body.append([])
        for i in range(len(cell_poss)):
          if left_aligned_to_header:
            if i < len(cell_poss)-1:
              val = line[cell_poss[i]:cell_poss[i+1]]
            else:
              val = line[cell_poss[i]:]
          else:
            if i == 0:
              val = line[:cell_poss[0]]
            else:
              val = line[cell_poss[i-1]:cell_poss[i]]
          body[len(body)-1].append(val.strip())
    table = tabulate(body, header, tablefmt=tablefmt)
  else:
    body = [line.split(delimiter) for line in split_input]
    table = tabulate(body, tablefmt=tablefmt)
  return table

def sv_to_tex_file(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                   has_header_gap=0, start_line=None, end_line=None,
                   create_landscape=False, create_thin_margins=False, create_long_table=False, create_lines=False,
                   save_path=None):
  tex_str = sv_to_tex(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                      has_header_gap, start_line, end_line)
  if save_path is None:
    save_path = _create_save_path(input, ".tex")
  with open(save_path, 'w+') as f:
    f.write(_encapsulate_latex_table(tex_str, create_landscape, create_thin_margins, create_long_table, create_lines))

def sv_to_pdf(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
              has_header_gap=0, start_line=None, end_line=None,
              create_landscape=False, create_thin_margins=False, create_long_table=False, create_lines=False):
  tex_str = sv_to_tex(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                      has_header_gap, start_line, end_line)
  return build_pdf(_encapsulate_latex_table(tex_str, create_landscape, create_thin_margins, create_long_table, create_lines))

def sv_to_pdf_file(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                   has_header_gap=0, start_line=None, end_line=None,
                   create_landscape=False, create_thin_margins=False, create_long_table=False, create_lines=False,
                   save_path=None):
  pdf = sv_to_pdf(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header, has_header_gap,
                  start_line, end_line,
                  create_landscape, create_thin_margins, create_long_table, create_lines)
  _save_pdf(pdf, input, save_path)

def tex_to_pdf_file(input, save_path=None): 
  tex_str = _get_table_str(input)
  pdf = build_pdf(tex_str)
  _save_pdf(pdf, input, save_path)

