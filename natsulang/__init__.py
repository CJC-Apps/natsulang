#!/usr/bin/env python3

import argparse
import sys
from sys import exit


def throw_error(err, exc=1):
	sys.stderr.write(err)
	exit(exc)


if int(sys.version.split('.')[0]) < 3:
	throw_error("Unable to run natsulang in python version less than 3.0.0. Please upgrade your python to the newest version.", 2)

version = "1.0.0.b10"


def importlib(name):
	if name == "default":
		return """import = eval("__import__");
		int = eval("int");str = eval("str");float = eval("float");
		bool = eval("bool");list = eval("list");bytes = eval("bytes");
		set = eval("set");dict = eval("dict");
		map = eval("map");range = eval("range");
		None = eval("None");input = eval("input");
		print = eval("print");len = eval("len");
		exit = eval("exit");abs = eval("abs");
		all = eval("all");any = eval("any");
		bin = eval("bin");bytearray = eval("bytearray");
		callable = eval("callable");chr = eval("chr");
		compile = eval("compile");complex = eval("complex");
		divmod = eval("divmod");enumerate = eval("enumerate");
		filter = eval("filter");
		frozenset = eval("frozenset");hash = eval("hash");
		hex = eval("hex");id = eval("id");
		isinstance = eval("isinstance");iter = eval("iter");
		max = eval("max");memoryview = eval("memoryview");
		min = eval("min");next = eval("next");
		object = eval("object");oct = eval("oct");
		open = eval("open");ord = eval("ord");
		repr = eval("repr");zip = eval("zip");
		round = eval("round");slice = eval("slice");
		sorted = eval("sorted");sum = eval("sum");
		tuple = eval("tuple");type = eval("type");
		format = eval("format");True = eval("True");False = eval("False");
		flush = eval("output_buff_flush");
		"""
	elif name == "math":
		return """math = import("math");
		acos = math.acos; acosh = math.acosh;
		asin = math.asin; asinh = math.asinh;
		atan = math.atan; atan2 = math.atan2;
		atanh = math.atanh; ceil = math.ceil;
		comb = math.comb; copysign = math.copysign;
		cos = math.cos; cosh = math.cosh;
		degrees = math.degrees; dist = math.dist;
		e = math.e; erf = math.erf;
		erfc = math.erfc; exp = math.exp;
		expm1 = math.expm1; fabs = math.fabs;
		factorial = math.factorial; floor = math.floor;
		fmod = math.fmod; frexp = math.frexp;
		fsum = math.fsum; gamma = math.gamma;
		gcd = math.gcd; hypot = math.hypot;
		inf = math.inf; isclose = math.isclose;
		isfinite = math.isfinite; isinf = math.isinf;
		isnan = math.isnan; isqrt = math.isqrt;
		ldexp = math.ldexp; lgamma = math.lgamma;
		log = math.log; log10 = math.log10;
		log1p = math.log1p; log2 = math.log2;
		modf = math.modf; nan = math.nan;
		perm = math.perm; pi = math.pi;
		pow = math.pow; prod = math.prod;
		radians = math.radians; remainder = math.remainder;
		sin = math.sin; sinh = math.sinh;
		sqrt = math.sqrt; tan = math.tan;
		tanh = math.tanh; tau = math.tau;
		trunc = math.trunc;
		"""
	elif name == "cmath":
		return """cmath = import("cmath");
		acos = cmath.acos; acosh = cmath.acosh;
		asin = cmath.asin; asinh = cmath.asinh;
		atan = cmath.atan; atanh = cmath.atanh;
		cos = cmath.cos; cosh = cmath.cosh;
		e = cmath.e; exp = cmath.exp;
		inf = cmath.inf; infj = cmath.infj;
		isclose = cmath.isclose; isfinite = cmath.isfinite;
		isinf = cmath.isinf; isnan = cmath.isnan;
		log = cmath.log; log10 = cmath.log10;
		nan = cmath.nan; nanj = cmath.nanj;
		phase = cmath.phase; pi = cmath.pi;
		polar = cmath.polar; rect = cmath.rect;
		sin = cmath.sin; sinh = cmath.sinh;
		sqrt = cmath.sqrt; tan = cmath.tan;
		tanh = cmath.tanh; tau = cmath.tau;
		"""
	else:
		return None


global_var = {}
values = []
program = ""
if_count = 0
output_buff = ""


class JiangPuException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


def output_buff_flush():
	global output_buff
	sys.stdout.write(output_buff)
	sys.stdout.flush()
	output_buff = ""


def parse_single(prog, begin, tg="") -> list:
	global if_count
	cur = begin
	tag = tg
	mainprog = ""
	preprog = []
	split = []
	glob = []
	if prog[cur: cur + 3] == "for" and not prog[cur + 3].isalnum() and prog[cur + 3] != "_":
		cur += 3
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or (not prog[cur].isalpha() and prog[cur] != '_'):
			throw_error("In program tag " + tag + " position " + str(cur) + ": Name expected.\n")
		var = ""
		while cur < len(prog) and (prog[cur].isalnum() or prog[cur] == '_'):
			var += prog[cur]
			cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != ':':
			throw_error("In program tag " + tag + " position " + str(cur) + ": ':' expected.\n")
		cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] == ')':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Expression expected.\n")
		expr = parse_program(prog, cur, tg)
		preprog += expr[0]
		preprog.append("for natsulang_" + var + " in " + expr[1][:-1] + ":\n")
		cur = expr[3]
		glob = expr[4]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != ')':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		for i in range(len(res[0])):
			res[0][i] = '\t' + res[0][i]
		preprog += res[0]
		preprog.append('\t' + res[1])
		mainprog = "None\n"
		cur = res[3] + 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		glob += res[4]
		return [preprog, mainprog, cur, glob]
	if prog[cur: cur + 5] == "while" and not prog[cur + 5].isalnum() and prog[cur + 5] != "_":
		cur += 5
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		preprog += res[0]
		preprog.append('while (' + res[1][:-1] + '):\n')
		cur = res[3] + 1
		glob = res[4]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur < len(prog) and prog[cur] != ';':
			if cur >= len(prog) or prog[cur] != '(':
				throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
			res2 = parse_program(prog, cur + 1, tg)
			for i in range(len(res2[0])):
				res2[0][i] = '\t' + res2[0][i]
			preprog += res2[0]
			preprog.append('\t' + res2[1])
			cur = res2[3] + 1
			glob += res2[4]
		elif cur < len(prog) and prog[cur] == ';':
			cur += 1
		res = list(res[0])
		for i in range(len(res)):
			res[i] = '\t' + res[i]
		preprog += res
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		mainprog = "None\n"
		return [preprog, mainprog, cur, glob]
	if prog[cur: cur + 4] == "func" and not prog[cur + 4].isalnum() and prog[cur + 4] != "_":
		cur += 4
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or (not prog[cur].isalpha() and prog[cur] != '_'):
			throw_error("In program tag " + tag + " position " + str(cur) + ": Name expected.\n")
		var = ""
		while cur < len(prog) and (prog[cur].isalnum() or prog[cur] == '_'):
			var += prog[cur]
			cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		cur += 1
		title = "def natsulang_" + var + "("
		while cur < len(prog) and prog[cur] != ')':
			name = ""
			while cur < len(prog) and prog[cur] != ')' and prog[cur] != ',':
				if prog[cur] == ' ' or prog[cur] == '\t' or prog[cur] == '\n':
					cur += 1
					continue
				name += prog[cur]
				if prog[cur] == '"' or prog[cur] == "'":
					quote_type = prog[cur]
					cur += 1
					is_quote, is_trans = True, False
					while cur < len(prog) and is_quote:
						name += prog[cur]
						if not is_trans and prog[cur] == '\\':
							is_trans = True
						elif is_trans:
							is_trans = False
						elif is_quote and prog[cur] == quote_type:
							is_quote = False
						cur += 1
					name += prog[cur]
					if is_quote:
						throw_error("In program tag " + tag + " position " + str(cur) + ": Quote expected.\n")
				cur += 1
			if cur == len(prog):
				throw_error("In program tag " + tag + " position " + str(cur) + ": ',' or bracket expected.\n")
			if name[0].isalnum() or name[0] == '_':
				title += "natsulang_" + name
			else:
				title += name
			if prog[cur] == ',':
				cur += 1
				title += ","
		title += '):\n'
		cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		preprog.append(title)
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		for i in range(len(res[0])):
			res[0][i] = '\t' + res[0][i]
		preprog += res[0]
		preprog.append('\t' + res[1])
		cur = res[3] + 1
		if cur == len(prog):
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		mainprog = "None\n"
		glob = ["natsulang_" + var]
		return [preprog, mainprog, cur, glob]
	if prog[cur: cur + 2] == "if" and not prog[cur + 2].isalnum() and prog[cur + 2] != "_":
		cur += 2
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		preprog += res[0]
		ifres = 'if_result_' + str(if_count)
		if_count += 1
		preprog.append(ifres + ' = None\n')
		preprog.append('if (' + res[1][:-1] + '):\n')
		cur = res[3] + 1
		glob = res[4]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur >= len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		for i in range(len(res[0])):
			res[0][i] = '\t' + res[0][i]
		preprog += res[0]
		preprog.append('\t' + ifres + ' = ' + res[1])
		cur = res[3] + 1
		glob += res[4]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur < len(prog) and prog[cur] == '(':
			res = parse_program(prog, cur + 1, tg)
			for i in range(len(res[0])):
				res[0][i] = '\t' + res[0][i]
			preprog.append("else:\n")
			preprog += res[0]
			preprog.append('\t' + ifres + ' = ' + res[1])
			cur = res[3] + 1
			glob += res[4]
			while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
				cur += 1
		mainprog = ifres + '\n'
		return [preprog, mainprog, cur, glob]
	if prog[cur: cur + 4] == "jump" and not prog[cur + 4].isalnum() and prog[cur + 4] != "_":
		cur += 4
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog) or prog[cur] != '(':
			throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
		res = parse_program(prog, cur + 1, tg)
		preprog += res[0]
		preprog.append("raise JiangPuException(" + res[1][:-1] + ")\n")
		mainprog = "None\n"
		cur = res[3] + 1
		glob = res[4]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		return [preprog, mainprog, cur, glob]
	last_name = False
	in_func = 0
	func_pos = 0
	while cur < len(prog) and prog[cur] != ';' and (prog[cur] != ')' or in_func):
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur == len(prog):
			break
		if (prog[cur].isalnum() or prog[cur] == '_') and not (cur + 1 < len(prog) and prog[cur + 1] in "'\""):
			name = ""
			while cur < len(prog) and (prog[cur].isalnum() or prog[cur] == '_'):
				name += prog[cur]
				cur += 1
			if (not len(mainprog) or mainprog[-1] != '.') and name != "eval" and name != "break" and name != "continue" and name != "return" and not name[0].isdigit():
				mainprog += "natsulang_" + name
				glob.append("natsulang_" + name)
			else:
				if name == "break" or name == "continue":
					preprog.append(name + "\n")
					mainprog += "None"
				else:
					mainprog += name
				if not name[0].isdigit():
					mainprog += " "
			last_name = True
		elif prog[cur] == '(':
			if last_name or (len(mainprog) and (mainprog[-1] == ')' or mainprog[-1] == ']')):
				mainprog += '('  # This is a function
				in_func += 1
				if in_func == 1:
					func_pos = cur
				cur += 1
			else:
				res = parse_program(prog, cur + 1, tg)
				preprog += res[0]
				mainprog += '(' + res[1][:-1] + ')'
				cur = res[3] + 1
				if cur > len(prog):
					cur = len(prog)
			last_name = False
		else:
			last_name = False
			if prog[cur] == ')':
				in_func -= 1
			if prog[cur] == '&' and mainprog[-1] == '&':
				mainprog = mainprog[:-1] + " and "
			elif prog[cur] == '|' and mainprog[-1] == '|':
				mainprog = mainprog[:-1] + " or "
			elif prog[cur] == '!' and (cur == len(prog) or prog[cur + 1] != '='):
				mainprog = mainprog + " not "
			elif prog[cur] == '"' or prog[cur] == "'" or prog[cur].isalnum():
				if prog[cur].isalnum():
					mainprog += prog[cur]
					cur += 1
				quote_type = prog[cur]
				mainprog += prog[cur]
				cur += 1
				is_quote, is_trans = True, False
				if mainprog.endswith("'''") or mainprog.endswith('"""'):
					quote_type *= 3;
				while cur < len(prog) and is_quote:
					mainprog += prog[cur]
					if not is_trans and prog[cur] == '\\':
						is_trans = True
					elif is_trans:
						is_trans = False
					elif is_quote and prog[cur] == quote_type:
						is_quote = False
					elif is_quote and mainprog[len(mainprog) - 3:] == quote_type:
						is_quote = False
					cur += 1
				cur -= 1
				if is_quote:
					throw_error("In program tag " + tag + " position " + str(cur) + ": Quote expected.\n")
			else:
				mainprog += prog[cur]
			cur += 1
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
	if in_func:
		throw_error("In program tag " + tag + " position " + str(func_pos) + ": Unmatched left bracket.\n")
	if mainprog == "":
		mainprog = "None"
	mainprog += '\n'
	return [preprog, mainprog, cur, glob]


def parse_program(prog, begin, tg="") -> list:
	cur = begin
	tag = tg + ":"
	tagged = False
	mainprog = ""
	preprog = []
	glob = []
	while cur < len(prog) and prog[cur] != ')':
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if prog[cur] == '#':
			cur += 1
			while cur < len(prog) and prog[cur] != '#':
				if not tagged:
					tag += prog[cur]
				cur += 1
			tagged = True
			if cur == len(prog):
				throw_error("In program tag " + tag + " position " + str(cur) + ": Another '#' expected\n")
			cur += 1
		elif prog[cur] == '@':
			position = cur
			cur += 1
			name = ""
			while cur < len(prog) and prog[cur] != '@':
				name += prog[cur]
				cur += 1
			if cur == len(prog):
				throw_error("In program tag " + tag + " position " + str(cur) + ": Another '@' expected\n")
			cur += 1
			lib = importlib(name)
			if lib is None:
				throw_error("In program tag " + tag + " position " + str(position) + ": No libs with name '" + name + "'\n")
			result = parse_program(lib, 0)
			preprog += result[0]
			preprog.append("None\n")
			glob += result[4]
		elif cur == len(prog) or prog[cur] == ';' or prog[cur] == ")":
			continue
		else:
			res = parse_single(prog, cur, tg)
			preprog += res[0]
			preprog.append(res[1])
			cur = res[2]
			glob += res[3]
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
		if cur < len(prog) and prog[cur] != ';' and prog[cur] != ')':
			throw_error("In program tag " + tag + " position " + str(cur) + ": ';' expected.\n")
		if cur < len(prog) and prog[cur] == ';':
			cur += 1
			while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
				cur += 1
			if cur == len(prog) or prog[cur] == ')':
				preprog.append("None\n")
		while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
			cur += 1
	if not len(preprog):
		mainprog = "None\n"
	else:
		mainprog = preprog[-1]
		preprog.pop()
	is_equal = 0
	isInQuote, isTransformed = False, False
	for i in range(len(mainprog) - 1):
		if not isInQuote and (mainprog[i] == '"' or mainprog[i] == "'"):
			isInQuote = mainprog[i]
		elif isInQuote and isTransformed:
			isTransformed = False
		elif isInQuote and mainprog[i] == '\\':
			isTransformed = True
		elif isInQuote and mainprog[i] == isInQuote:
			isInQuote = False
		if not isInQuote and mainprog[i] == '=' and (i < 1 or mainprog[i - 1] not in "<=>!" or (i >= 2 and mainprog[i - 2] == mainprog[i - 1])) and mainprog[i + 1] != '=':
			is_equal = i + 1
			break
	if is_equal:
		if mainprog[is_equal - 2] in "+-*/%<>&|^":
			is_equal -= 1
			if mainprog[is_equal - 2] == mainprog[is_equal - 1]:
				is_equal -= 1
		preprog.append(mainprog)
		mainprog = mainprog[0: is_equal - 1] + "\n"
	return [preprog, mainprog, tag, cur, glob]


answer = parse_program("@default@;", 0)
exec(''.join(answer[0]))
left = False
isInQuote, isTransformed = False, False
stack = 0
skip_tag = ""


def addchar(ch):
	global left, stack, isInQuote, isTransformed, skip_tag, left, program, output_buff
	if not left:
		if ch == "{":
			left = True
			stack = 1
		else:
			if skip_tag != "":
				return
			output_buff += ch
			if len(output_buff) >= 262144 or ch == '\n' or ch == '\0':
				sys.stdout.write(output_buff)
				sys.stdout.flush()
				output_buff = ""
	else:
		if ch != "}" or isInQuote or stack > 1:
			program += ch
			if not isInQuote and (ch == "'" or ch == '"'):
				isInQuote = ch
			elif isInQuote and not isTransformed and ch == '\\':
				isTransformed = True
			elif isInQuote and isTransformed:
				isTransformed = False
			elif isInQuote and (ch == isInQuote):
				isInQuote = False
			if ch == '}' and not isInQuote:
				stack -= 1
			if ch == '{' and not isInQuote:
				stack += 1
		else:
			sys.stdout.write(output_buff)
			sys.stdout.flush()
			output_buff = ""
			left = False
			stack = []
			answer = parse_program(program, 0)
			if answer[2] != skip_tag and skip_tag != "":
				program = ""
				return
			skip_tag = ""
			glob = answer[4]
			try:
				if len(glob):
					exec('global ' + ','.join(list(set(glob))) + '\n' + ''.join(answer[0]))
				else:
					exec(''.join(answer[0]))
				result = eval(answer[1])
				if result is None:
					result = ''
				if type(result) == bytes:
					result = result.decode('utf-8')
				sys.stdout.write(str(result))
				sys.stdout.flush()
			except JiangPuException as e:
				if e.value is None:
					skip_tag = "exit"
				else:
					skip_tag = ":" + str(e.value)
			except Exception as e:
				sys.stderr.write("Exception occured in program tag " + answer[2] + "\n")
				raise
			program = ""


def parsefile(file):
	while True:
		ch = file.read(1)
		if len(ch) == 0:
			if left:
				sys.stderr.write("Error: Unexpected end of file.\n")
				exit(1)
			sys.stdout.write(output_buff)
			sys.stdout.flush()
			break
		addchar(ch)


def run(args=None):
	Parser = argparse.ArgumentParser(prog="natsulang", description="Natsu Language version " + version + " by Natsu Kinmoe")
	Parser.add_argument("-s", "--stream", help="execute a program inputted in stream, [file] will be ignored", action='store_true', default=False)
	Parser.add_argument("-v", "--version", help="show the version of this program and exit", action='store_true', default=False)
	Parser.add_argument("--check-updates", help="check if your natsulang is up to date", action='store_true', default=False)
	Parser.add_argument("--ignore-header", help="ignore the first line of the program", action='store_true', default=False)
	Parser.add_argument("file", help="the file that will be executed", nargs="?", default="")
	Args = Parser.parse_args(args)
	if Args.version:
		print(version)
		exit()
	if Args.check_updates:
		from xmlrpc.client import ServerProxy
		from functools import reduce
		print("Checking for updates ...")
		pypi = ServerProxy("https://pypi.python.org/pypi")
		possible_package_names = ["natsulang", "Natsulang"]
		available = reduce(lambda a, b: a if a is not None else b, map(pypi.package_releases, possible_package_names))
		Version = ""
		for i in range(len(version)):
			if i < len(version) and version[i] == '.' and version[i + 1].isalpha():
				continue
			Version += version[i]
		if available[0] != Version:
			print("Updates found. You are using version", Version)
			print("but the newest version is", available[0])
			print("You can upgrade natsulang via the")
			print("'pip install --upgrade natsulang' command.")
		else:
			print("Your natsulang is up to date.")
		exit()
	if Args.file == "" and not Args.stream:
		Parser.print_help()
		exit()
	file = sys.stdin if Args.stream else open(Args.file, "r")
	if Args.ignore_header:
		ch = ''
		while ch != '\n':
			ch = file.read(1)
			if len(ch) == 0:
				exit(0)
	parsefile(file)

if __name__ == "__main__":
	run()
