# Unit tests

Unit tests are defined in test.py executed with run_tests.sh. This tests that pdf and tex files can be create from the test.csv test data.

# CLI tests

The testl.align and testl2.align are designed to check tex and pdf construction for tables that are left aligned on header. Use:
1: python -m tutil pdf ./testl.align --start_line 25 --end_line 99 --input_type sv --tex_landscape --tex_thin_margins --tex_big_table --tex_raw --left_aligned_to_header --header_gap_size 1 --tex_thin_margins
2: python -m tutil pdf ./testl2.align --start_line 25 --end_line 99 --input_type sv --tex_raw --left_aligned_to_header --header_gap_size 1 --tex_thin_margins
3: python -m tutil pdf ./testr.align --start_line 25 --end_line 99 --input_type sv --tex_raw --right_aligned_to_header --header_gap_size 1 --tex_thin_margins
4: python -m tutil pdf ./testr2.align --start_line 25 --end_line 99 --input_type sv --tex_raw --right_aligned_to_header --header_gap_size 1 --tex_thin_margins

In 2, 3 & 4 the tables will be truncated, because the tex_big_table_options has not been supplied. Also will be portrait and wide margins.

5: python -m tutil pdf ./test.tsv --end_line 16 --input_type sv --tex_raw
6: python -m tutil pdf ./target-compare.out --input_type sv --tex_landscape --tex_thin_margins --tex_big_table --tex_raw --right_aligned_to_header --header_gap_size 1 --name "Bonds" --tex_thin_margins --num_lbl_cols 2 --num_table_splits 2
7: python -m tutil pdf ./target-compare.out --input_type sv --tex_landscape --tex_thin_margins --tex_big_table --tex_raw --right_aligned_to_header --header_gap_size 1 --name "Bonds" --tex_thin_margins --num_lbl_cols 2 --num_table_splits 2 --transpose
