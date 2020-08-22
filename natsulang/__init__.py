#!/usr/bin/env python3

import argparse
import sys
from sys import exit


def throw_error(err, exc=1):
    sys.stderr.write(err)
    exit(exc)


if int(sys.version.split('.')[0]) < 3:
    throw_error("Unable to run natsulang in python version less than 3.0.0. Please upgrade your python to the newest version.", 2)

version = "1.0.0.0"

imports = dict(default="""import = eval("__import__");
int = eval("int");str = eval("str");float = eval("float");
bool = eval("bool");list = eval("list");
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
""")

global_var = {}
values = []
program = ""


def parse_single(prog, begin, tg="") -> list:
    cur = begin
    tag = tg
    mainprog = ""
    preprog = []
    split = []
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
        return [preprog, mainprog, cur]
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
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        if cur >= len(prog) or prog[cur] != '(':
            throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
        res2 = parse_program(prog, cur + 1, tg)
        for i in range(len(res2[0])):
            res2[0][i] = '\t' + res2[0][i]
        preprog += res2[0]
        preprog.append('\t' + res2[1])
        res = list(res[0])
        for i in range(len(res)):
            res[i] = '\t' + res[i]
        preprog += res
        cur = res2[3] + 1
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        mainprog = "None\n"
        return [preprog, mainprog, cur]
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
        return [preprog, mainprog, cur]
    if prog[cur: cur + 2] == "if" and not prog[cur + 2].isalnum() and prog[cur + 2] != "_":
        cur += 2
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        if cur == len(prog) or prog[cur] != '(':
            throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
        res = parse_program(prog, cur + 1, tg)
        preprog += res[0]
        preprog.append('if_result = None\n')
        preprog.append('if (' + res[1][:-1] + '):\n')
        cur = res[3] + 1
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        if cur >= len(prog) or prog[cur] != '(':
            throw_error("In program tag " + tag + " position " + str(cur) + ": Bracket expected.\n")
        res = parse_program(prog, cur + 1, tg)
        for i in range(len(res[0])):
            res[0][i] = '\t' + res[0][i]
        preprog += res[0]
        preprog.append('\tif_result = ' + res[1])
        cur = res[3] + 1
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        if cur < len(prog) and prog[cur] == '(':
            res = parse_program(prog, cur + 1, tg)
            for i in range(len(res[0])):
                res[0][i] = '\t' + res[0][i]
            preprog.append("else:\n")
            preprog += res[0]
            preprog.append('\tif_result = ' + res[1])
            cur = res[3] + 1
            while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
                cur += 1
        mainprog = "if_result\n"
        return [preprog, mainprog, cur]
    last_name = False
    in_func = 0
    func_pos = 0
    while cur < len(prog) and prog[cur] != ';' and (prog[cur] != ')' or in_func):
        while cur < len(prog) and (prog[cur] == ' ' or prog[cur] == '\n' or prog[cur] == '\t'):
            cur += 1
        if cur == len(prog):
            break
        if prog[cur].isalnum() or prog[cur] == '_':
            name = ""
            while cur < len(prog) and (prog[cur].isalnum() or prog[cur] == '_'):
                name += prog[cur]
                cur += 1
            if (not len(mainprog) or mainprog[-1] != '.') and name != "eval" and name != "break" and name != "continue" and name != "return" and not name[0].isdigit():
                mainprog += "natsulang_" + name
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
            elif prog[cur] == '"' or prog[cur] == "'":
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
        throw_error("In program tag " + tag + " position " + func_pos + ": Unmatched left bracket.\n")
    if mainprog == "":
        mainprog = "None"
    mainprog += '\n'
    return [preprog, mainprog, cur]


def parse_program(prog, begin, tg="") -> list:
    cur = begin
    tag = tg + ":"
    tagged = False
    mainprog = ""
    preprog = []
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
            if imports[name] is None:
                throw_error("In program tag " + tag + " position " + str(position) + ": No libs with name '" + name + "'\n")
            preprog += parse_program(imports[name], 0)[0]
        elif cur == len(prog) or prog[cur] == ';' or prog[cur] == ")":
            continue
        else:
            res = parse_single(prog, cur, tg)
            preprog += res[0]
            preprog.append(res[1])
            cur = res[2]
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
    for i in range(len(mainprog) - 1):
        if mainprog[i] == '=' and (i < 1 or mainprog[i - 1] not in "<=>!" or (i >= 2 and mainprog[i - 2] == mainprog[i - 1])) and mainprog[i + 1] != '=':
            is_equal = i + 1
            break
    if is_equal:
        if mainprog[is_equal - 2] in "+-*/%<>&|^":
            is_equal -= 1
            if mainprog[is_equal - 2] == mainprog[is_equal - 1]:
                is_equal -= 1
        preprog.append(mainprog)
        mainprog = mainprog[0: is_equal - 1] + "\n"
    return [preprog, mainprog, tag, cur]


answer = parse_program("@default@;", 0)
exec(''.join(answer[0]))
left = False
isInQuote, isTransformed = False, False
stack = 0
skip_tag = ""


def addchar(ch):
    global left, stack, isInQuote, isTransformed, skip_tag, left, program
    if not left:
        if ch == "{":
            left = True
            stack = 1
        else:
            if skip_tag != "":
                return
            sys.stdout.write(ch)
            sys.stdout.flush()
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
            left = False
            stack = []
            answer = parse_program(program, 0)
            if answer[2] != skip_tag and skip_tag != "":
                return
            exec(''.join(answer[0]))
            result = eval(answer[1])
            if result is None:
                result = ''
            sys.stdout.write(str(result))
            sys.stdout.flush()
            program = ""


def parsefile(file):
    while True:
        ch = file.read(1)
        if len(ch) == 0:
            if left:
                sys.stderr.write("Error: Unexpected end of file.\n")
                exit(1)
            break
        addchar(ch)


def run(args=None):
    Parser = argparse.ArgumentParser(prog="natsulang", description="Natsu Language version " + version + " by Natsu Kinmoe")
    Parser.add_argument("-s", "--stream", help="execute a program inputted in stream, [file] will be ignored", action='store_true', default=False)
    Parser.add_argument("file", help="The file that will be executed.", nargs="?", default="")
    Args = Parser.parse_args(args)
    if Args.file == "" and not Args.stream:
        Parser.print_help()
        exit()
    file = sys.stdin if Args.stream else open(Args.file, "r")
    parsefile(file)

if __name__ == "__main__":
	run()