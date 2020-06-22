#!/usr/bin/env python3
import re
from os.path import exists, basename, splitext
from sys import stderr, argv, exit, stdout
import argparse
from typing import List
import json
import tempfile

import pandas as pd


def main():
	opts = getoptions(getparser(), argv)
	path_old = opts.book1
	path_new = opts.book2

	if not exists(path_old):
		print_usage("{}: no such file".format(path_old))
	if not exists(path_new):
		print_usage("{}: no such file".format(path_new))

	path_old_base, ext_old = splitext(basename(path_old))
	path_new_base, ext_new = splitext(basename(path_new))

	if ext_old.lower() != ".xlsx":
		print_usage("{}: is not a valid excel file".format(path_old))
	if ext_new.lower() != ".xlsx":
		print_usage("{}: is not a valid excel file".format(path_new))

	# READ EXCEL FILES
	df_old = None
	try:
		df_old = pd.read_excel(path_old, sheet_name=None, na_filter=False)
	except:
		print_usage("{}: is not a valid excel file".format(path_old))

	df_new = None
	try:
		df_new = pd.read_excel(path_new, sheet_name=None, na_filter=False)
	except:
		print_usage("{}: is not a valid excel file".format(path_new))

	# END READ EXCEL FILES

	json_fname = splitvers(path_old_base)[0] + ".json"
	xlsx_fname = splitvers(path_old_base)[0] + ".xlsx"

	json_data = {}
	plain_data = ""
	for sheet in df_old.keys():
		for col in df_old[sheet].keys():
			for row in df_old[sheet][col].keys():
				value_old = str(df_old[sheet][col][row])
				try:
					value_new = str(df_new[sheet][col][row])

					if value_old != value_new:
						plain_data += plain_row_format(sheet, col, row, value_old, value_new)
						add_value(json_data, sheet=sheet, col=col, row=row, val_new=value_new, val_old=value_old)
				except:
					if value_old != "":
						plain_data += plain_row_format(sheet, col, row, value_old, "")
						add_value(json_data, sheet=sheet, col=col, row=row, val_new="", val_old=value_old)

	for sheet in df_new.keys():
		for col in df_new[sheet].keys():
			for row in df_new[sheet][col].keys():
				value_old = str(df_new[sheet][col][row])
				try:
					value_new = str(df_old[sheet][col][row])
				except:
					if value_old.strip(" ") != "":
						plain_data += plain_row_format(sheet, col, row, value_old, "")
						add_value(json_data, sheet=sheet, col=col, row=row, val_new="", val_old=value_old)

	if opts.type in ["json", "j"]:
		if opts.pretty:
			data_str = json.dumps(json_data, indent=4)
		else:
			data_str = json.dumps(json_data)

		stdout.buffer.write(bytes(data_str, encoding="utf8"))

		if opts.outfile:
			filename = opts.outfile
			if not filename.endswith(".json"):
				filename += ".json"
			with open(filename, "w") as file:
				file.write(data_str)
				stderr.buffer.write(bytes(f"Output written to {filename}", encoding="utf8"))

	elif opts.type in ["xlsx", "x"]:
		with tempfile.NamedTemporaryFile(suffix=xlsx_fname) as tfile:
			output_diff_xlsx(tfile.name, json_data, df_old)
			tfile.seek(0)
			data = tfile.read()
			if opts.outfile:
				filename = opts.outfile
				if not filename.endswith(".xlsx"):
					filename += ".xlsx"
				with open(filename, "w") as file:
					file.buffer.write(data)
					stderr.buffer.write(bytes(f"Output written to {filename}", encoding="utf8"))
			else:
				stdout.buffer.write(data)

	elif opts.type in ["text", "t"]:
		if opts.outfile:
			filename = opts.outfile
			if not filename.endswith(".txt"):
				filename += ".txt"
			with open(filename, "w") as file:
				file.buffer.write(bytes(plain_data, encoding="utf8"))
		else:
			stdout.buffer.write(bytes(plain_data, encoding="utf8"))


def print_help():
	getparser().print_help(file=stderr)
	exit(2)


def print_usage(message):
	getparser().print_usage(file=stderr)
	stderr.buffer.write(bytes(message, encoding="utf8"))
	exit(2)


def getparser():
	parser = argparse.ArgumentParser(description="Shows the difference between two excel workbooks")
	parser.add_argument('book1', type=str, help='Old diff book')
	parser.add_argument('book2', type=str, help='New diff book')
	parser.add_argument('-t', "--type", type=str, default="text", choices=["json", "j", "xlsx", "x", "text", "t"],
	                    help='output type (xlsx, json, plain)')
	parser.add_argument('-o', "--outfile", type=str, help='output filename')
	parser.add_argument("--pretty", action="store_true", default=False, help="pretty print json")
	return parser


def getoptions(parser: argparse.ArgumentParser, args: List):
	return parser.parse_args(args[1:])


def get_book_version(book_name: str):
	groups = re.search("(v[0-9]\\.[0-9]{1,2})$", book_name)
	if groups is not None:
		return groups.group(0)
	else:
		return ""


# def diff(file1, file2):
# 	if not exists(file1):
# 		return "{}: no such file".format(file1)
# 	if not exists(file2):
# 		return "{}: no such file".format(file2)
#
# 	file1_base, ext_OLD = splitext(basename(file1))
# 	file2_base, ext_NEW = splitext(basename(file2))
#
# 	if ext_OLD.lower() != ".xlsx":
# 		return "{}: is not a valid excel file".format(file1)
# 	if ext_NEW.lower() != ".xlsx":
# 		return "{}: is not a valid excel file".format(file2)
#
# 	# READ EXCEL FILES
# 	df_OLD = None
# 	try:
# 		df_OLD = pd.read_excel(file1, sheet_name=None, na_filter=False)
# 	except:
# 		return "{}: is not a valid excel file".format(file1)
#
# 	df_NEW = None
# 	try:
# 		df_NEW = pd.read_excel(file2, sheet_name=None, na_filter=False)
# 	except:
# 		return "{}: is not a valid excel file".format(file2)
#
# 	data = ""
# 	for sheet in df_OLD.keys():
# 		for col in df_OLD[sheet].keys():
# 			for row in df_OLD[sheet][col].keys():
# 				value_OLD = df_OLD[sheet][col][row]
# 				try:
# 					value_NEW = df_NEW[sheet][col][row]
# 					if value_OLD != value_NEW:
# 						data += plain_row_format(sheet, col, row, value_OLD, value_NEW)
# 				except Exception as e:
# 					if value_OLD != "":
# 						data += plain_row_format(sheet, col, row, value_OLD, "")
#
# 	for sheet in df_NEW.keys():
# 		for col in df_NEW[sheet].keys():
# 			for row in df_NEW[sheet][col].keys():
# 				value_OLD = df_NEW[sheet][col][row]
# 				try:
# 					value_NEW = df_OLD[sheet][col][row]
# 				except Exception as e:
# 					if value_OLD.strip(" ") != "":
# 						data += plain_row_format(sheet, col, row, value_OLD, "")
# 	return data
#

def splitvers(book_name: str) -> (str, str):
	"""
	Splits the file name to name and version suffix
	:param book_name:
	:return: (str, str)  (base, version)
	"""
	vers = get_book_version(book_name)
	name = book_name[:-len(vers)].rstrip(".-_/\\")
	return name, vers


def plain_row_format(sheet, col, row, data1, data2):
	"""
	:return: formatted plain text row output
	"""
	return "'{}' '{}' '{}' '{}' '{}'\n".format(sheet, col, row, data1, data2)


def add_keys(data: dict, sheet: str = None, col: str = None, row: str = None):
	"""
	:param data: json data destination dictionary
	:param sheet: workbook sheet to insert
	:param col: sheet column to insert
	:param row: column row to insert
	:return: None
	"""
	if sheet not in data.keys():
		data[sheet] = {}
	if col not in data[sheet].keys():
		data[sheet][col] = {}
	if row not in data[sheet][col].keys():
		data[sheet][col][row] = {}


def add_value(data: dict, sheet: str = None, col: str = None, row: str = None, val_new: str = "", val_old: str = ""):
	"""
	:param data: json data destination dictionary
	:param sheet: workbook sheet to insert
	:param col: sheet column to insert
	:param row: column row to insert
	:param val_old: old value to insert
	:param val_new: new value to insert
	:return: None
	"""
	add_keys(data, sheet=sheet, col=col, row=row)
	data[sheet][col][row]["old"] = val_old
	data[sheet][col][row]["new"] = val_new


def output_diff_xlsx(fname: str, data: dict, df_OLD):
	"""
	:param data: json data to save as xlsx workbook
	:param fname: file path of the output file
	:return: None
	"""
	diff = df_OLD.copy()
	writer = pd.ExcelWriter(fname, engine='xlsxwriter')
	for sheet in data.keys():
		for col in data[sheet].keys():
			for row in data[sheet][col].keys():
				value_NEW = data[sheet][col][row]["new"]
				value_OLD = data[sheet][col][row]["old"]
				if value_OLD != value_NEW:
					diff[sheet][col][row] = "{}→{}".format(value_OLD, value_NEW)
		diff_sheet = sheet + "_diff"
		diff[sheet].to_excel(writer, sheet_name=diff_sheet, index=False)

		workbook = writer.book
		worksheet = writer.sheets[diff_sheet]
		highlight_fmt = workbook.add_format({"font_color": "#FF0000", "bg_color": "#B1B3B3"})

		worksheet.conditional_format("A1:ZZ1000", {"type"    : "text",
		                                           "criteria": "containing",
		                                           "value"   : "→",
		                                           "format"  : highlight_fmt})

	writer.save()


if __name__ == "__main__":
	main()
