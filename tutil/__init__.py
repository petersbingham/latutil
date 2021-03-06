import copy
import csv
import os
import splot
import re

from latex import build_pdf
from tabulate import tabulate

min_latex_start = "\\documentclass{article}"
latex_name = "\\textbf{"
latex_long_table_package = "\\usepackage{longtable}"
min_latex_doc_start = "\\begin{document}"
min_latex_end = "\\end{document}"

latex_center_start = "\\begin{table}{}\n\\centering"
latex_center_end = "\\end{table}"

latex_caption = "\\caption{"

latex_tex_landscape = "\\usepackage[landscape]{geometry}"
latex_tex_thin_margins = "\\usepackage{geometry}\geometry{left=20mm, right=20mm, top=25mm, bottom=25mm}"

latextablefmt = "latex"

default_plt_cmd = 'h:*'

def _encapsulate_latex_table(tab_tex_strs, caption, name, number_label_columns, tex_lines, tex_long_table, tex_landscape, tex_thin_margins):
  latex = min_latex_start
  if tex_long_table:
    tab_tex_strs = [t.replace("{tabular}", "{longtable}") for t in tab_tex_strs]
    latex += "\n" + latex_long_table_package
  if tex_landscape:
    latex += "\n" + latex_tex_landscape
  if tex_thin_margins:
    latex += "\n" + latex_tex_thin_margins
  latex += "\n" + min_latex_doc_start
  if name is not None:
    latex += "\n" + latex_name + name + "}"
  if not tex_long_table:
    latex += "\n" + latex_center_start
  if tex_lines:
    tab_tex_strs = [t.replace(r'\hline','').replace(r'\\',r'\\\hline') for t in tab_tex_strs]
  elif number_label_columns>0:
    # Labels define grouping if their value is empty (grouped with the row above)
    new_tab_tex_strs = []
    for t in tab_tex_strs:
      s = t.split('\n')
      if any([r.strip()[0]=='&' for r in s[:-1]]):
        first_cell_empty_last = None
        for i,r in enumerate(s):
          first_cell_empty = '&' in r and r.strip()[0]=='&'
          if first_cell_empty_last and not first_cell_empty:
            s[i-1] = s[i-1].replace(r'\hline','').replace(r'\\',r'\\\hline')
          first_cell_empty_last = first_cell_empty
      new_tab_tex_strs.append('\n'.join(s))
    tab_tex_strs = new_tab_tex_strs
  for i,t in enumerate(tab_tex_strs):
    latex += "\n" + t
    if i != len(tab_tex_strs)-1:
      latex += "\n\\newpage"
  if caption is not None:
    cap_str = "\n" + latex_caption + caption + "}"
    if not tex_long_table:
      latex += cap_str
    else:
      latex = latex.replace("\\end{longtable}", cap_str+"\n\\end{longtable}")
  if not tex_long_table:
    latex += "\n" + latex_center_end
  return latex + "\n" + min_latex_end

def _is_path(input):
  return "\r" not in input

def _save_path(input, ext):
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
    save_path = _save_path(input, ".pdf")
  pdf.save_to(save_path)

def transpose_table(header, body, number_label_columns):
  num_rows = len(body[0]) - number_label_columns
  num_cols = len(body)
  mod = 0
  if header is not None:
    mod = 1
    num_cols += 1

  new_body = [[0 for i in range(num_cols)] for j in range(num_rows)]
  for i in range(num_rows):
    for j in range(num_cols):
      if j==0 and header is not None:
        new_body[i][0] = header[number_label_columns + i]
      else:
        new_body[i][j] = body[j - mod][i + number_label_columns]

  new_header = amalgamate_column_labels(body, number_label_columns)
  if header is not None and new_header is not None:
    new_header = [''] + new_header

  return new_header, new_body

def _apply_op(body, i, j, op, val):
  val = float(val)
  try:
    if op == '+':
      return str(float(body[i][j]) + val)
    if op == '-': # Fix issue with - as command line argument
      return str(float(body[i][j]) - val)
    if op == '*':
      return str(float(body[i][j]) * val)
    if op == '/':
      return str(float(body[i][j]) / val)
  except ValueError:
    pass
  return str(val)

def _modify(body, op, mod, number_label_columns):
  id = mod[0]
  new_body = copy.deepcopy(body)
  if id != '[':
    val = mod
    for i in range(len(body)):
      for j in range(number_label_columns, len(body[i])):
        new_body[i][j] = _apply_op(body, i, j, op, val)
  else:
    b1 = mod.index('[')
    b2 = mod.index(']')
    b3 = mod.rindex('[')
    b4 = mod.rindex(']')
    ir = mod[b1+1:b2]
    ic = mod[b3+1:b4]
    if ir == 'i':
      # It's floating. Use the row value in that row
      for i in range(len(body)):
        val = body[i][number_label_columns+int(ic)]
        for j in range(number_label_columns, len(body[i])):
          new_body[i][j] = _apply_op(body, i, j, op, val)
    if ic == 'i':
      # It's floating. Use the column value in that row
      for i in range(len(body)):
        for j in range(number_label_columns, len(body[i])):
          val = body[int(ir)][j]
          new_body[i][j] = _apply_op(body, i, j, op, val)
    else:
      val = body[int(ir)][number_label_columns+int(ic)]
      for i in range(len(body)):
        for j in range(number_label_columns, len(body[i])):
          new_body[i][j] = _apply_op(body, i, j, op, val)
  return new_body

def get_table(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
              header_gap_size=0, start_line=None, end_line=None, number_label_columns=0, transpose=False, formula=None):
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

  #clean
  split_input = [s for s in split_input if len(s.strip())>0]

  if has_header:
    header = split_input[0].split(delimiter)
    if not left_aligned_to_header and not right_aligned_to_header:
      body = [line.split(delimiter) for line in split_input[1+header_gap_size:]]
    else:
      cell_poss_start = []
      cell_poss_end = []
      for title in header:
        if len(cell_poss_end) > 0:
          last_val = cell_poss_end[len(cell_poss)-1]
          split_input_sub = split_input[0][last_val:] 
        else:
          last_val = 0
          split_input_sub = split_input[0]
        cell_poss_start.append(last_val+split_input_sub.index(title))
        cell_poss_end.append(last_val+split_input_sub.index(title)+len(title))
        if left_aligned_to_header:
          cell_poss = cell_poss_start
        else:
          cell_poss = cell_poss_end
      body = []
      for line in split_input[1+header_gap_size:]:
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
  else:
    header = None
    body = [line.split(delimiter) for line in split_input]

  if formula is not None:
    formula = formula[1:-1] # Remove enclising "" (required to prevent cli issues with minus signs)
    mods = re.split('\+|-|\*|/', formula)
    ops = [c for c in formula if c in ('+','-','*','/')]
    for op, mod in zip(ops, mods[1:]):
      body = _modify(body, op, mod, number_label_columns)

  if transpose:
    trans_has_lbl_col = header is not None
    header, body = transpose_table(header, body, number_label_columns)
    number_label_columns = 0
    if trans_has_lbl_col:
      number_label_columns = 1

  return header, body, number_label_columns

def amalgamate_column_labels(body, number_label_columns):
  amal_lbls = None
  if number_label_columns > 0:
    amal_lbls = []
    lbls = ['' for _ in range(number_label_columns)]
    for row in body:
      for i in range(number_label_columns):
        if row[i] != '':
          lbls[i] = row[i]
      amal_lbls.append(' '.join(lbls))
  return amal_lbls

def split_table(header, body, number_label_columns, number_table_splits):
  header_lbls = header[:number_label_columns]
  body_lbls = [row[:number_label_columns] for row in body]
  headers = []
  bodies = []
  num_tables = number_table_splits + 1
  val_cols_per_table = len(header[number_label_columns:]) / num_tables
  rem_cols_per_table = len(header[number_label_columns:]) % num_tables
  start_ind = None
  for i in range(num_tables):
    if start_ind is None:
      start_ind = number_label_columns 
    else:
      start_ind = end_ind
    end_ind = start_ind + val_cols_per_table
    if rem_cols_per_table > 0:
      end_ind += 1
      rem_cols_per_table -= 1
    headers.append(header_lbls + header[start_ind: end_ind])
    tab_body = []
    for lbls, row in zip(body_lbls, body):
      tab_body.append(lbls + row[start_ind: end_ind])
    bodies.append(tab_body)
  return headers, bodies

def sv_to_tex(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
              header_gap_size=0, number_label_columns=0, start_line=None, end_line=None, transpose=False, formula=None, number_table_splits=0):

  header, body, number_label_columns = get_table(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header, header_gap_size, start_line, end_line, number_label_columns, transpose, formula)
  if number_table_splits > 0:
    headers, bodies = split_table(header, body, number_label_columns, number_table_splits)
  else:
    headers, bodies = [header], [body]

  tab_tex_strs = []
  for h, b in zip(headers, bodies):
    if h is None: 
      tab_tex_strs.append(tabulate(b, tablefmt=latextablefmt))
    else:
      tab_tex_strs.append(tabulate(b, h, tablefmt=latextablefmt))
  return tab_tex_strs

def sv_to_gnuplot(input, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                  header_gap_size=0, number_label_columns=0, start_line=None, end_line=None, transpose=False, formula=None):

  header, body, number_label_columns = get_table(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header, header_gap_size, start_line, end_line, number_label_columns, transpose, formula)

  for i in range(len(body)):
    for j in range(len(body[i]) - number_label_columns):
      if body[i][j + number_label_columns] == '':
        body[i][j + number_label_columns] = '?'

  new_header = []
  for h in header:
    if h == '':
      new_header.append('-')
    else:
      new_header.append(h.replace(' ', '-').replace('\\','').replace('^','').replace('_','').replace('{','').replace('}','').replace('$',''))

  return tabulate(body, new_header, tablefmt='plain')

def sv_to_splot(input, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                header_gap_size=0, number_label_columns=0, start_line=None, end_line=None, transpose=False, formula=None, plot_command=None,
                interactive=False, plot_parameters=None, save_paths=None):
  if plot_command is None:
    plot_command = default_plt_cmd
  if plot_parameters is None:
    plot_parameters = [20, 15, 0.05, 14, 6]

  header, body, number_label_columns = get_table(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header, header_gap_size, start_line, end_line, number_label_columns, transpose, formula)

  for i in range(len(body)):
    for j in range(len(body[i]) - number_label_columns):
      if body[i][j + number_label_columns] == '':
        body[i][j + number_label_columns] = None

  plt_cmd_spt = plot_command.split(':')
  if plt_cmd_spt[0] != 'h':
    raise Exception('Plot command {} not supported.'.format(plot_command))

  legend = amalgamate_column_labels(body, number_label_columns)
  plt_header = header[number_label_columns:]
  plt_body = [b[number_label_columns:] for b in body]
  if plt_cmd_spt[1] != '*':
    if ',' in plt_cmd_spt[1] and '->' in plt_cmd_spt[1]:
      raise Exception('Plot command {} not supported.'.format(plot_command))
    else:
      if ',' in plt_cmd_spt[1]:
        indices = eval('[' + plt_cmd_spt[1] + ']')
      elif '->' in plt_cmd_spt[1]:
        plt_rng_spt = plt_cmd_spt[1].split('->')
        indices = range(int(plt_rng_spt[0]), int(plt_rng_spt[1])+1)
      legend = [legend[i] for i in range(len(legend)) if i in indices]
      plt_body = [plt_body[i] for i in range(len(plt_body)) if i in indices]

  splot.place_legend_outside(15)
  splot.set_img_size(plot_parameters[0], plot_parameters[1])
  splot.set_legend_spacing(plot_parameters[2])
  splot.set_font_size(plot_parameters[3], plot_parameters[4])
  if name is None:
    name = ''
  splot.scatter(plt_header, plt_body, legend=legend, title=name, display=interactive, path=save_paths)

def sv_to_tex_file(input, caption=None, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                   header_gap_size=0, number_label_columns=0, start_line=None, end_line=None,
                   transpose=False, formula=None, number_table_splits=0, 
                   tex_lines=False, tex_long_table=False, tex_landscape=False, tex_thin_margins=False,
                   save_path=None):
  tab_tex_strs = sv_to_tex(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                           header_gap_size, number_label_columns, start_line, end_line, transpose, formula, number_table_splits)
  if save_path is None:
    save_path = _save_path(input, ".tex")
  with open(save_path, 'w+') as f:
    f.write(_encapsulate_latex_table(tab_tex_strs, caption, name, number_label_columns, tex_lines, tex_long_table, tex_landscape, tex_thin_margins))

def sv_to_pdf(input, caption=None, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
              header_gap_size=0, number_label_columns=0, start_line=None, end_line=None,
              transpose=False, formula=None, number_table_splits=0, 
              tex_lines=False, tex_long_table=False, tex_landscape=False, tex_thin_margins=False):
  tex_str = sv_to_tex(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                      header_gap_size, number_label_columns, start_line, end_line, transpose, formula, number_table_splits)
  return build_pdf(_encapsulate_latex_table(tex_str, caption, name, number_label_columns, tex_lines, tex_long_table, tex_landscape, tex_thin_margins))

def sv_to_pdf_file(input, caption=None, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                   header_gap_size=0, number_label_columns=0, start_line=None, end_line=None,
                   transpose=False, formula=None, number_table_splits=0,
                   tex_lines=False, tex_long_table=False, tex_landscape=False, tex_thin_margins=False,
                   save_path=None):
  pdf = sv_to_pdf(input, caption, name, delimiter, has_header, left_aligned_to_header, right_aligned_to_header, header_gap_size, number_label_columns,
                  start_line, end_line,
                  transpose, formula, number_table_splits, 
                  tex_lines, tex_long_table, tex_landscape, tex_thin_margins)
  _save_pdf(pdf, input, save_path)

def tex_to_pdf_file(input, save_path=None): 
  tex_str = _get_table_str(input)
  pdf = build_pdf(tex_str)
  _save_pdf(pdf, input, save_path)

def sv_to_gnuplot_file(input, caption=None, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                       header_gap_size=0, number_label_columns=0, start_line=None, end_line=None,
                       transpose=False, formula=None, save_path=None):
  gnuplot_str = sv_to_gnuplot(input, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                              header_gap_size, number_label_columns, start_line, end_line, transpose, formula)
  if save_path is None:
    save_path = _save_path(input, ".dat")
  with open(save_path, 'w+') as f:
    f.write(gnuplot_str)

def sv_to_splot_files(input, caption=None, name=None, delimiter=None, has_header=True, left_aligned_to_header=False, right_aligned_to_header=False,
                      header_gap_size=0, number_label_columns=0, start_line=None, end_line=None,
                      transpose=False, formula=None, plot_command=None, interactive=False, plot_parameters=None, save_path=None):
  if save_path is None:
    save_paths = [_save_path(input, ".svg"), _save_path(input, ".png")]
  gnuplot_str = sv_to_splot(input, name, delimiter, has_header, left_aligned_to_header, right_aligned_to_header,
                            header_gap_size, number_label_columns, start_line, end_line, transpose, formula, plot_command, interactive, plot_parameters, save_paths)

