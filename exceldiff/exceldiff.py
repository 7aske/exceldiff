#!/usr/bin/env python3
import re
from os.path import exists, basename, splitext
from sys import stderr, argv, exit, stdout
import argparse
from typing import List
import json
import tempfile

import pandas as pd

opts = None


def main():
	opts = getoptions(getparser(), argv)
	path_OLD = opts.book1
	path_NEW = opts.book2

	if not exists(path_OLD):
		print_usage("{}: no such file".format(path_OLD))
	if not exists(path_NEW):
		print_usage("{}: no such file".format(path_NEW))

	path_OLD_base, ext_OLD = splitext(basename(path_OLD))
	path_NEW_base, ext_NEW = splitext(basename(path_NEW))

	if ext_OLD.lower() != ".xlsx":
		print_usage("{}: is not a valid excel file".format(path_OLD))
	if ext_NEW.lower() != ".xlsx":
		print_usage("{}: is not a valid excel file".format(path_NEW))

	# READ EXCEL FILES
	df_OLD = None
	try:
		df_OLD = pd.read_excel(path_OLD, sheet_name=None, na_filter=False)
	except:
		print_usage("{}: is not a valid excel file".format(path_OLD))

	df_NEW = None
	try:
		df_NEW = pd.read_excel(path_NEW, sheet_name=None, na_filter=False)
	except:
		print_usage("{}: is not a valid excel file".format(path_NEW))

	# END READ EXCEL FILES

	json_fname = splitvers(path_OLD_base)[0] + ".json"
	xlsx_fname = splitvers(path_OLD_base)[0] + ".xlsx"

	json_data = {}
	plain_data = ""
	for sheet in df_OLD.keys():
		for col in df_OLD[sheet].keys():
			for row in df_OLD[sheet][col].keys():
				value_OLD = df_OLD[sheet][col][row]
				try:
					value_NEW = df_NEW[sheet][col][row]

					if value_OLD != value_NEW:
						plain_data += plain_row_format(sheet, col, row, value_OLD, value_NEW)
						add_keys(json_data, sheet=sheet, col=col, row=row)
						json_data[sheet][col][row]["old"] = value_OLD
						json_data[sheet][col][row]["new"] = value_NEW
				except Exception as e:
					if value_OLD != "":
						plain_data += plain_row_format(sheet, col, row, value_OLD, "")
						add_keys(json_data, sheet=sheet, col=col, row=row)
						json_data[sheet][col][row]["old"] = value_OLD
						json_data[sheet][col][row]["new"] = ""

	for sheet in df_NEW.keys():
		for col in df_NEW[sheet].keys():
			for row in df_NEW[sheet][col].keys():
				value_OLD = df_NEW[sheet][col][row]
				try:
					value_NEW = df_OLD[sheet][col][row]
				except Exception as e:
					if value_OLD.strip(" ") != "":
						plain_data += plain_row_format(sheet, col, row, value_OLD, "")
						add_keys(json_data, sheet=sheet, col=col, row=row)
						json_data[sheet][col][row]["old"] = value_OLD
						json_data[sheet][col][row]["new"] = ""

	if opts.type in ["json", "j"]:
		if opts.pretty:
			print(json.dumps(json_data, indent=4))
		else:
			print(json.dumps(json_data))
	elif opts.type in ["xlsx", "x"]:
		with tempfile.NamedTemporaryFile(suffix=xlsx_fname) as file:
			output_diff_xlsx(file.name, json_data, df_OLD)
			file.seek(0)
			data = file.read()
			stdout.buffer.write(data)
	elif opts.type in ["text", "t"]:
		print(plain_data)


def print_help():
	getparser().print_help(file=stderr)
	exit(2)


def print_usage(message):
	getparser().print_usage(file=stderr)
	print(message, file=stderr)
	exit(2)


def getparser():
	parser = argparse.ArgumentParser(description="Shows the difference between two excel workbooks")
	parser.add_argument('book1', type=str, help='Old diff book')
	parser.add_argument('book2', type=str, help='New diff book')
	parser.add_argument('-t', "--type", type=str, default="json", choices=["json", "j", "xlsx", "x", "text", "t"],
	                    help='output type (xlsx, json, plain)')
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


def diff(file1, file2):
	if not exists(file1):
		return"{}: no such file".format(file1)
	if not exists(file2):
		return "{}: no such file".format(file2)

	file1_base, ext_OLD = splitext(basename(file1))
	file2_base, ext_NEW = splitext(basename(file2))

	if ext_OLD.lower() != ".xlsx":
		return "{}: is not a valid excel file".format(file1)
	if ext_NEW.lower() != ".xlsx":
		return "{}: is not a valid excel file".format(file2)

	# READ EXCEL FILES
	df_OLD = None
	try:
		df_OLD = pd.read_excel(file1, sheet_name=None, na_filter=False)
	except:
		return "{}: is not a valid excel file".format(file1)

	df_NEW = None
	try:
		df_NEW = pd.read_excel(file2, sheet_name=None, na_filter=False)
	except:
		return "{}: is not a valid excel file".format(file2)
	data = ""
	for sheet in df_OLD.keys():
		for col in df_OLD[sheet].keys():
			for row in df_OLD[sheet][col].keys():
				value_OLD = df_OLD[sheet][col][row]
				try:
					value_NEW = df_NEW[sheet][col][row]
					if value_OLD != value_NEW:
						data += plain_row_format(sheet, col, row, value_OLD, value_NEW)
				except Exception as e:
					if value_OLD != "":
						data += plain_row_format(sheet, col, row, value_OLD, "")

	for sheet in df_NEW.keys():
		for col in df_NEW[sheet].keys():
			for row in df_NEW[sheet][col].keys():
				value_OLD = df_NEW[sheet][col][row]
				try:
					value_NEW = df_OLD[sheet][col][row]
				except Exception as e:
					if value_OLD.strip(" ") != "":
						data += plain_row_format(sheet, col, row, value_OLD, "")
	return data


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
