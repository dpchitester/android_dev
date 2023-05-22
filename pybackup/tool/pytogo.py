#! /usr/bin/env python3
'''
Perform crude Python -> Go translation

Not written in Go itself because (a) it needs regexp lookbehinds,
and (b) Python is still better for rapid prototyping when you have
a lot of string-bashing to do.

Copyright 2018 by Eric S. Raymond <esr@thyrsus.com>
SPDX-License-Identifier: BSD-2-Clause
'''
# pylint: disable=anomalous-backslash-in-string,line-too-long,invalid-name,missing-function-docstring,no-else-continue,no-else-break,consider-using-f-string

# pylint: disable=multiple-imports
import sys, re, collections

version = 1.8

verbose = 0

INDENT = 4
TABWIDTH = 8

fmt = False

def metric(s):
    assert s == "" or s.isspace()
    return s.count(" ") + (s.count("\t") * TABWIDTH)

def indepth(s):
    m = re.match("^\s*", s)	# Match leading whitespace
    if m is None:
        return None
    return metric(m.group(0))

def iscomment(s):
    return re.match("^\s*#", s) is not None

def isdocstring(s):
    s = s.strip()
    return len(s) >= 2 and s[0] == '"' and s[-1] == '"'

def isblockstart(line):
    line = line.strip()
    if not line:
        return False
    for kw in ("def ", "func ", "if ", "for", "else", "elif ", "while ", "except", "try", "finally", "with", "class"):
        if line.startswith(kw):
            return True
    return False

transliterations = (
    ("is None", "== nil"),
    ("is not None", "!= nil"),
    ("None", "nil"),
    (" and ", " && "),
    (" or ", " || "),
    (" not ", " !"),
    ("(not ", "(!"),
    ("True", "true"),
    ("False", "false"),
    ("in range", ":= range"),
    ("while true", "for"),
    ("\\\n", "\n"),
    ("def __str__(", "func String("),
    )

# Python identifier as a matchable group
ID = r"([a-zA-Z_][a-zA-Z0-9_]*)"
# Constant identifier (conventional)
CAPID = r"([A-Z_][A-Z0-9_]*)"
# Python compound reference as a matchable group - may contain interior dots
REF = r"([a-zA-Z_][a-zA-Z0-9_.]*[a-zA-Z0-9_])"
# Opener: compound reference or function/method call
# preceded by a syntactic delimiter.
OID = "(?<=[ 	!(,+])([a-zAZ0-9_.]+(?:\([a-zAZ0-9_.]*\))*)"
# String literal
STR = r"""(["'](?:\\\\|\\["']|[^"'])+["'])"""
# String literal or numeric or variable/structure reference.  More
# kinds of things could go here, but not anything that contains commas
# outside a string.
ARG = '("[^"]*"|[a-zAZ0-9_.]*[a-zAZ0-9_]|[0-9]+)'
# Best place for more transformations. These are applied in such a way
# that they can never alter comments. They could, potentially, mess
# with strings, but this is wildly unlikely unless your strings
# contain Python code snippets.
oneshot = (
    (re.compile(r"^(\s*)if ([^:]+): (.+)"), r"\1if \2 {\n    \1\3"),
    (re.compile(r"^(\s*)while ([^:]+): (.*)"), r"\1while \2 {\n    \1\3"),
    (re.compile(r" *\-= *1\b"), "--"),
    (re.compile(r"\bprint\("), "fmt.Print("),
    (re.compile("^(\s*)for \(?" + ID + ", *" + ID + "\)? in " + REF + ".items\(\)"), r"\1for \2, \3 := range \4"),
    (re.compile("^(\s*)for \(?" + ID + ", *" + ID + "\)? in enumerate\(" + REF + "\)"), r"\1for \2, \3 := range \4"),
    (re.compile("^(\s*)for " + ID + " in " + REF + ".keys\(\)"), r"\1for \2, _ := range \3"),
    (re.compile("^(\s*)for " + ID + " in "), r"\1for _, \2 := range "),
    # main
    (re.compile('if +__name__ +== +"__main__"'), r'func main()'),
    (re.compile("if +__name__ +== +'__main__'"), r'func main()'),
    # elif to else if
    (re.compile("^(\s*)elif"), r"\1else if"),
    # % expressions
    (re.compile('"([^"]*)"\s*%\s*'+ARG), r'fmt.Sprintf("\1", \2)'),
    (re.compile('"([^"]*)"\s*%\s*\(([^)]*)\)'), r'fmt.Sprintf("\1", \2)'),
    # Raw literals to backticks
    (re.compile(r'\br"([^"]*)"'), r"`\1`"),
    (re.compile(r"\br'([^']*)'"), r"`\1`"),
    # Structure methods
    (re.compile(OID + r"\.append\("+ARG+"\)"), r'\1 = append(\1, \2)'),
    (re.compile(r"\bdel +"+ARG+r"\["+ARG+r"\]"), r'delete(\1, \2)'),
    # Method calls. The @@ may be subsituted if we've seen a previous "class"
    # line at the right indent level (that is, INDENT out from the func header).
    (re.compile(r"(def|func) ([a-zA-Z_][a-zA-Z0-9_]*)\(self(, *)?"), r"func (self @@) \2("),
    # Library calls.
    # The Go compiler will object if the result is being used and the error output isn't.
    # Only translations that swap argument order or do nested calls need to happen here;
    # straight substitutions are done elsewhere.
    (re.compile(r"os.symlink\("+ARG+", *"+ARG+"\)"), r"os.Symlink(\2, \1)"),
    (re.compile(r"os.path.relpath\("+ARG+r"\)"),r"filepath.Rel(os.Getwd(), \1)"),
    (re.compile(r"os.path.relpath\("+ARG+", *"+ARG+"\)"), r"filepath.Rel(\2, \1)"),
    # Simple integer/float/string constants
    (re.compile("^(?="+CAPID+r"\s*"+"=\s*[0-9.])"), r"const "),
    (re.compile("^(?="+CAPID+r"\s*"+"=\s*" + STR + ")"), r"const "),
    # New frontiers in translation hackery. The Go library is missing entries.
    (re.compile(r"os.path.exists\("+ARG+r"\)"),r"func(fn string) bool {_,err=os.Stat(fn);return !os.IsNotExist(err)}\(\1\)"),
    (re.compile(r"os.path.isdir\("+ARG+r"\)"),r"func(fn string) bool {st,err=os.Stat(fn);return err==nil && st.Mode().IsDir()}\(\1\)"),
    (re.compile(r"os.path.isfile\("+ARG+r"\)"),r"func(fn string) bool {st,err=os.Stat(fn);return err==nil && st.Mode().IsRegular()}\(\1\)"),
    (re.compile(r"os.path.islink\("+ARG+r"\)"),r"func(fn string) bool {st,err=os.Stat(fn);return err==nil && st.Mode().IsSymlink()}\(\1\)"),
    )

stdlibcalls = (
    # Map basic library calls.  Argument signatures and turn types (if
    # any, the Python calls often throw OsError or whatever, and the
    # Go function may be dual-return with an error) are not guaranteed
    # to match exactly. But each of these gets us closer, and the Go
    # compiler will generate useful complaints.
    #
    # Math library calls are listed in the order they occur in the
    # Python documentation rather than alphabetically, except where
    # reordering was required to prevent false prefix matches.
    ("cmath.phase", "cmplx.Phase"),
    ("cmath.polar", "cmplx.Polar"),
    ("cmath.rect", "cmplx.Rect"),
    ("cmath.exp", "cmplx.Exp"),
    ("cmath.rect", "cmplx.Rect"),
    ("cmath.log10", "cmplx.log10"),
    ("cmath.log", "cmplx.log"),
    ("cmath.sqrt", "cmplx.Sqrt"),
    ("cmath.acos", "cmplx.Acos"),
    ("cmath.asin", "cmplx.Asin"),
    ("cmath.atan", "cmplx.Atan"),
    ("cmath.cos", "cmplx.Cos"),
    ("cmath.sin", "cmplx.Sin"),
    ("cmath.tan", "cmplx.Tan"),
    ("cmath.acosh", "cmplx.Acosh"),
    ("cmath.asinh", "cmplx.Asinh"),
    ("cmath.atanh", "cmplx.Atanh"),
    ("cmath.cosh", "cmplx.Cosh"),
    ("cmath.sinh", "cmplx.Sinh"),
    ("cmath.tanh", "cmplx.Tanh"),
    ("cmath.isnan", "cmplx.IsNan"),
    ("math.ceil", "math.Ceil"),
    ("math.copysign", "math.Copysign"),
    ("math.fabs", "math.Abs"),
    ("math.floor", "math.Floor"),
    ("math.fmod", "math.Mod"),		# Dangerous curve
    ("math.isnan", "math.IsNan"),
    ("math.ldexp", "math.Ldexp"),
    ("math.modf", "math.Modf"),
    ("math.fabs", "math.Abs"),
    ("math.exp", "math.Exp"),
    ("math.expm1", "math.Expm1"),
    ("math.log10", "math.Log10"),
    ("math.log", "math.Log"),		# Dangerous curve - in Python this can have two arguments
    ("math.pow", "math.Pow"),
    ("math.sqrt", "math.Sqrt"),
    ("math.acos", "math.Acos"),
    ("math.asin", "math.Asin"),
    ("math.atan", "math.Atan"),
    ("math.cos", "math.Cos"),
    ("math.hypot", "math.Hypot"),
    ("math.sin", "math.Sin"),
    ("math.tan", "math.Tan"),
    ("math.acosh", "math.Acosh"),
    ("math.asinh", "math.Asinh"),
    ("math.atanh", "math.Atanh"),
    ("math.cosh", "math.Cosh"),
    ("math.sinh", "math.Sinh"),
    ("math.tanh", "math.Tanh"),
    ("math.erf", "math.Erf"),
    ("math.erfc", "math.Erfc"),
    ("math.gamma", "math.Gamma"),
    ("math.lgamma", "math.Lgamma"),
    ("os.chdir", "os.Chdir"),
    ("os.chmod", "os.Chmod"),
    ("os.chown", "os.Chown"),
    ("os.dup", "sys.Dup"),
    ("os.ftruncate", "os.Ftruncate"),
    ("os.fsync", "sys.Fsync"),
    ("os.getegid", "os.Getegid"),
    ("os.geteuid", "os.Geteuid"),
    ("os.getpid", "os.Getpid"),
    ("os.getppid", "os.Getppid"),
    ("os.getuid", "os.Getuid"),
    ("os.getcwd", "os.Getwd"),
    ("os.getenv", "os.Getenv"),
    ("os.getgroups", "os.Getgroups"),
    ("os.lchown", "os.Lchown"),
    ("os.open", "os.OpenFile"),
    ("os.mkdir", "os.Mkdir"),
    ("os.remove", "os.Remove"),
    ("os.rename", "os.Rename"),
    ("os.rmdir", "os.Remove"),	# No separate rmdir in Go
    ("os.path.abspath", "filepath.Abs"),
    ("os.path.basename", "filepath.Base"),
    ("os.path.dirname", "filepath.Dir"),
    ("os.path.isabs", "filepath.IsAbs"),
    ("os.path.normpath", "filepath.Clean"),
    ("os.path.split", "filepath.Split"),
    ("os.unsetenv", "os.Unsetenv"),
    ("sys.exit", "os.Exit"),
    ("sys.maxint", "int(^uint(0) >> 1)"),
    )

sysvars = (
    ("cmath.e", "math.E"),
    ("cmath.pi", "math.Pi"),
    ("math.e", "math.E"),
    ("math.pi", "math.Pi"),
    ("os.sep", "string(os.PathSeparator)"),
    ("sys.argv", "os.Args"),
    ("sys.environ", "os.Environ()"),
    ("sys.stderr","os.Stderr"),
    ("sys.stdin","os.Stdin"),
    ("sys.stdout","os.Stdout"),
    )

repeatable = (
    # Map Python string methods to Go string library calls. Note that
    # the lstrip/rstrip methods might be slightly buggy if the
    # difference between ASCII and Unicode whitespace is ever
    # significant.
    (re.compile(OID + r"\.capitalize\(\)"), r'strings.ToTitle(\1)'),
    (re.compile(OID + r"\.count\("+ARG+"\)"), r'strings.Count(\1, \2)'),
    (re.compile(OID + r"\.endswith\("+ARG+"\)"), r'strings.HasSuffix(\1, \2)'),
    (re.compile(OID + r"\.find\("+ARG+"\)"), r'strings.Index(\1, \2)'),
    (re.compile(STR + r"\.join\("+ARG+"\)"), r"strings.Join(\2, \1)"),
    (re.compile(OID + r"\.join\("+ARG+"\)"), r"strings.Join(\2, \1)"),
    (re.compile(OID + r"\.lower\(\)"), r'strings.ToLower(\1)'),
    (re.compile(OID + r"\.lstrip\(\)"), r'strings.TrimLeft(\1, " \\n\\t")'),
    (re.compile(OID + r"\.replace\("+ARG+", *"+ARG+"\)"), r"strings.Replace(\1, \2, -1)"),
    (re.compile(OID + r"\.replace\("+ARG+", *"+ARG+", *"+ARG+"\)"), r"strings.Replace(\1, \2, \3)"),
    (re.compile(OID + r"\.rfind\("+ARG+"\)"), r'strings.Lastindex(\1, \2)'),
    (re.compile(OID + r"\.rstrip\(\)"), r'strings.TrimRight(\1, " \\n\\t")'),
    (re.compile(OID + r"\.split\("+ARG+"\)"), r'strings.Split(\1, \2)'),
    (re.compile(OID + r"\.split\(\)"), r'strings.Fields(\1)'),
    (re.compile(OID + r"\.startswith\("+ARG+"\)"), r'strings.HasPrefix(\1, \2)'),
    (re.compile(OID + r"\.strip\(\)"), r'strings.TrimSpace(\1)'),
    (re.compile(OID + r"\.upper\(\)"), r'strings.ToUpper(\1)'),
    )

# Earlier matches prevent later ones.  The detector for if/else
# expressions in returns has to go first, otherwise we could false
# match to an if/else expression containing a boolean guard but which
# actually returns some other type.
returnmatch = (
    (re.compile("^\s+return .*if"), None),
    (re.compile("^\s+return true"), "bool"),
    (re.compile("^\s+return false"), "bool"),
    (re.compile("^\s+return .* !"), "bool"),
    (re.compile("^\s+return .* =="), "bool"),
    (re.compile("^\s+return .* !="), "bool"),
    (re.compile("^\s+return .* <"), "bool"),
    (re.compile("^\s+return .* >"), "bool"),
    (re.compile("^\s+return .* >="), "bool"),
    (re.compile("^\s+return .* <="), "bool"),
    (re.compile("^\s+return .* && "), "bool"),
    #(re.compile("^\s+return .* \|\| "), "bool"),
    #(re.compile("^\s+return .*<="), "bool"),
    (re.compile("^\s+return -?[0-9]+$"), "int"),
    (re.compile('^\s+return "[^"]*"'), "string"),
    )

import_map = {
    "bz2": "compress/gzip",
    "cmath": "math/cmplx",
    #"cmd": 'kommandant "gitlab.com/ianbruene/Kommandant"',
    "collections": None,
    "copy": "reflect",
    "datetime": "time",
    "functools": None,
    "itertools": None,
    "cProfile": None,
    "email.message": "net/mail",
    "email.parser": "net/mail",
    "filecmp": None,
    "glob": "path/filepath",
    "heapq": None,
    "operator": None,
    "os.path": "path",
    "re": "regexp",
    "sre_constants": None,
    "stat": "os",
    "subprocess": "os/exec",
    "shlex": None,
    "sys": None,
    "tempfile": "io/ioutil",
    "uuid": "github.com/google/uuid",
    "unittest": None,
    }

# Post-blocking translations
# ["']((?:\\\\|\\["']|[^"'])+)["']
postblock = (
    (re.compile(r"""^(\s*)if\s""" + STR + r"""\sin\s""" + REF + r"(.*)"), r"""\1if string.Contains(\3, \2) \4"""),
    )

#' Magic comment to de-confuse Emacs Python highlighting after that string

def nuke_line(line):
    return line.startswith("from __future__ import")

def process_imports(lines):
    "Process a span of imports into an equivalent Go-like form"
    bucket = []
    if fmt:
        bucket.append("fmt")
    for line in lines:
        bucket += map(lambda x: x.strip(), line[7:].strip().split(","))
    bucket = list(filter(lambda x: x is not None, map(lambda x: import_map.get(x, x), bucket)))
    bucket = list(set(bucket))
    bucket.sort()
    return ["import (\n"] + ['\t"%s"\n' % x for x in bucket]  + [")\n"]

def instring(s, n):
    "Is position n within a string literal in s?"
    indouble = False
    insingle = False
    # pylint: disable=consider-using-enumerate
    for i in range(len(s)):
        if s[i] == '"':
            indouble = not indouble
        elif s[i] == "'":
            insingle = not insingle
        elif i == n:
            return indouble or insingle
    return False

def outreplace(text, a, b):
    "Perform replacement outside of string literals."
    while True:
        saved = text
        # pylint: disable=consider-using-enumerate
        for i in range(len(text)):
            # Can't substitute if our match start is outside a string
            if text[i:].startswith(a) and not instring(text, i):
                text = text[:i] + b + text[i+len(a):]
                break
        if text == saved:
            break
    return text

def flipsingle(s):
    "Map multicharacter single-quote literals to double-quote literals."
    indouble = False
    insingle = None
    escaped = False
    e = list(s)
    # pylint: disable=consider-using-enumerate
    for i in range(len(e)):
        # Prevent special handling of quotes with backslash
        if escaped:
            escaped = False
            continue
        elif e[i] == '\\':
            escaped = True
            continue
        # Possible comment
        if e[i] == '#' and not insingle and not indouble:
            return "".join(e[:i]), s[i:]
        # Starting a doublequoted string span outside a single-quote span?
        if s[i] == '"' and insingle is None:
            indouble = not indouble
            continue
        if indouble:
            continue
        # If we get here, we're outside any double quotes.
        # Pass through anything not a single quote.
        if e[i] != "'":
            continue
        # We're at a single quote.
        if not indouble and insingle is None: # Opener
            insingle = i
            continue
        if insingle is not None and s[insingle:i].count('"') == 0:
            e[insingle] = e[i] = '"'
            insingle = None
    return "".join(e), None

def transliterate(line):
    "Run all rules on a text line."
    body, comment = flipsingle(line)
    for (f, t) in transliterations:
        body = outreplace(body, f, t)
    for (f, t) in oneshot:
        body = f.sub(t, body)
    for (f, t) in stdlibcalls:
        body = outreplace(body, f + "(", t + "(")
    for (f, t) in sysvars:
        body = outreplace(body, f, t)
    while True:
        stash = body
        for (f, t) in repeatable:
            body = f.sub(t, body)
        if stash == body:
            break
        else:
            stash = body
    if comment is None:
        line = body
    else:
        line = body + "//" + comment[1:]
    return line

def isfuncstart(s):
    lookat = s.lstrip()
    return lookat.startswith("func ") or lookat.startswith("def ")

def outerfuncstart(s):
    return s.startswith("func ") or s.startswith("def ")

def typemapper(s):
    "Map PEP484 basic type names to Go basic typenames"
    for f, t in (("str", "string"), ("float", "float64"), ("complex", "complex128")):
        s = s.replace(f, t)
    return s

def pep484(line):
    "Transform PEP484 type hints to Go syntax."
    if not (line.count("(") == 1 and line.count(")") == 1):
        return line
    (pre, post) = line.split("(", 1)
    (signature, retclause) = post.split(")", 1)

    rebuilt = []
    for part in signature.split(","):
        peplike = part.split(":")
        if len(peplike) == 2:
            name = peplike[0].strip()
            typedec = peplike[1].strip()
            rebuilt.append(name + " " + typemapper(typedec))
        else:
            part = part.lstrip()
            if part.startswith("*") and not part.startswith("**"):
                part = part[1:] + " ..."
            rebuilt.append(part)
    retclause = typemapper(retclause)
    retclause = retclause.replace(" -> ", " ")
    return pre + "(" + ", ".join(rebuilt) + ")" + retclause

# pylint: disable=too-many-branches,too-many-statements,too-many-locals
def translate(instream, outstream):
    skipme = 0
    firstpass = []
    returnmatches = {}
    # First pass: translation to Go syntax without end scopes
    for line in instream:
        line = line.replace('"""', '`')
        skipme += line.count('`')
        if (skipme % 2) or line.count('`') == 1:
            line = "|" + line
        elif nuke_line(line):
            continue
        else:
            line = transliterate(line)
            if iscomment(line):
                line = line.replace("#", "//", 1)
            if isdocstring(line):
                line = line.replace('"', "// ", 1)
                line = line.replace('"', "",)
            else:
                line = line.rstrip()
                if line.endswith(":"):
                    line = line[:-1] + " {"
                if line.startswith("def "):
                    line = "func " + line[4:]
                line += "\n"
        firstpass.append(line)
    # Now add magic cookies to force scope closing
    secondpass = []
    firstpass.reverse()
    afterscope = True
    cookie = "#@ MAGIC scope ENDER@\n"
    for i, line in enumerate(firstpass):
        if afterscope and line.strip():
            secondpass.append(cookie)
            afterscope = False
        if outerfuncstart(line):
            afterscope = True
        secondpass.append(line)
    secondpass.reverse()
    if verbose:
        sys.stderr.write("After second pass:\n")
        # pylint: disable=consider-using-enumerate
        for i in range(len(secondpass)):
            sys.stderr.write(("%03d: " % i) + secondpass[i])
    # Third pass: Add block-end markers
    lines = []
    indents = []
    frames = []
    defstack = []
    # Loop is written this way  so we can back up and/or mutate it without
    # offending the Python gods
    i = -1
    while True:
        i += 1
        if i >= len(secondpass):
            break
        line = secondpass[i]
        # Skip multiline string contents
        if line.startswith("|"):
            lines.append(line)
            continue
        # These next two lines are to prevent a spacer line within
        # a function from neing treated like end of function and
        # closing all blocks.
        if not line.strip() and indents:
            lines.append(line)
            continue
        # Indent tracking. This is trickier to get right than it looks;
        # be sure you know what you're doing before you mess with it.
        depth = indepth(line)
        if indents and depth < indents[-1] + INDENT:
            startdepth = depth
            while indents and indents[-1] >= startdepth:
                lines.append((indents[-1] * " ") + "}\n")
                # pylint: disable=consider-using-enumerate
                for j in range(len(frames)):
                    if frames[j][0] >= i:
                        frames[j][0] += 1
                        frames[j][1] += 1
                indents.pop()
            # If we just matched indents with the top of the defstack,
            # record an end of frame. Later we'll use this to analyze
            # function scopes
            if len(defstack) > 0 and len(indents) == defstack[-1][1]:
                frames.append([defstack[-1][0], len(lines)-1, defstack[-1][2], defstack[-1][3]])
                defstack.pop()
        # Find starts of func/end frames
        if line.strip().startswith("func "):
            header = line.strip()[5:]
            if "@@" in header:
                header = header[len("(self @@) "):]
            funcnm = header.split("(")[0]
            defstack.append([len(lines), len(indents), set([]), funcnm])
        if line.strip().startswith("global "):
            newglobalvars = line.strip()[7:].replace(",", " ").split()
            defstack[-1][2] = defstack[-1][2].union(set(newglobalvars))
        # Mate else with preceding brackets.
        if len(lines) > 0 and lines[-1].endswith("}\n") and line.lstrip().startswith("else"):
            lines[-1] = lines[-1].rstrip() + " " + line.lstrip()
        else:
            lines.append(line)
        if isblockstart(line):
            indents.append(depth)
        # Ugh...
        # pylint: disable=global-statement
        global fmt
        if "fmt." in line:
            fmt = True
    if verbose:
        sys.stderr.write("After third pass:\n")
        # pylint: disable=consider-using-enumerate
        for i in range(len(lines)):
            sys.stderr.write(("%03d: " % i) + lines[i])
        sys.stderr.write("Frames: %s\n" % frames)
    # Fourth pass: post-blocking translations
    fourthpass = []
    for line in lines:
        for (f, t) in postblock:
            line = f.sub(t, line)
            fourthpass.append(line)
    lines = fourthpass
    if verbose:
        sys.stderr.write("After fourth pass:\n")
        # pylint: disable=consider-using-enumerate
        for i in range(len(lines)):
            sys.stderr.write(("%03d: " % i) + lines[i])
    # Attempt to fix up assignments
    detector = re.compile("^\s+([a-zA-Z_][a-zA-Z0-9_]*) *=[^=]")
    assignloc = {}
    for (start, end, globalvars, funcname) in frames:
        cnt = collections.Counter()
        for i in range(start, end+1):
            if line.startswith("|"):
                continue
            # Look for return-type cues
            for (cond, returntype) in returnmatch:
                if funcname is not None and cond.match(lines[i]):
                    returnmatches[funcname] = returntype
                    if verbose:
                        sys.stderr.write("Found %s return in %r (%d)\n" % (cond.pattern, lines[i], i))
                    break
            # Look for assignments
            m = detector.match(lines[i])
            if m:
                cnt[m.group(1)] += 1
                assignloc[m.group(1)] = i
        # Second pass: fix up returntypes
        oh = returnmatches.get(funcname)
        for i in range(start, end+1):
            if line.startswith("|"):
                continue
            if "func " in lines[i]:
                lines[i] = pep484(lines[i])
                if oh and lines[i].endswith(") {\n"):
                    lines[i] = lines[i].replace(") {", ") " + oh + " {")
                if lines[i+1].lstrip().startswith("//"):
                    docstring = lines[i+1]
                    lines[i+1] = lines[i]
                    if docstring[0:INDENT] == " " * INDENT:
                        docstring = docstring[INDENT:]
                    lines[i] = docstring
        for n in globalvars:
            cnt[n] +=1
        singles = [x for x in cnt if cnt[x] == 1]
        for tok in singles:
            j = assignloc[tok]
            lines[j] = lines[j].replace(tok + " =", tok + " :=", 1)
    # Package and library translation
    if lines and re.compile("^//!.*python").match(lines[0]):
        lines[0] = "package main\n"
    i = -1
    see_import = -1
    while True:
        i += 1
        if i >= len(lines):
            break
        line = lines[i]
        if see_import == -1 and line.startswith("import"):
            see_import = i
        elif see_import != -1  and not line.startswith("import"):
            filtered = process_imports(lines[see_import:i])
            lines = lines[:see_import] + filtered + lines[i:]
            see_import = -1
            i = len(lines)
    # Ship results
    for i, line in enumerate(lines):
        if line.startswith("|"):
            line = line[1:]
        if line != cookie:
            outstream.write(line)

if __name__ == "__main__":
    if sys.argv[1:].count("-v") > 0:
        print(version)
        raise SystemExit(0)
    verbose = sys.argv[1:].count("-d")
    translate(sys.stdin, sys.stdout)

# end
