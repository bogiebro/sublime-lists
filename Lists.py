import sublime, sublime_plugin, re

# makes corrections, starting the line after 'line' with x+1
def correctNum(self, edit, line, indent, x, before, after):
    editrow, _ = self.view.rowcol(line.end())
    while True:
        editrow += 1
        newline = self.view.line(self.view.text_point(editrow, 0))
        if newline.a == line.a or not self.view.substr(newline).startswith(indent) or newline.empty():
            return
        line = newline
        m = re.match("^" + indent + "[^\s\d]*\d+[^\s]* +(.*)$", self.view.substr(newline))
        if not m:
            continue
        x += 1
        self.view.replace(edit, newline, before + str(x) + after + m.group(1))

# makes corrections, starting the line after 'line' with a+1
def correctAlpha(self, edit, line, indent, a, before, after):
    editrow, _ = self.view.rowcol(line.end())
    while True:
        editrow += 1
        a += 1
        newline = self.view.line(self.view.text_point(editrow, 0))
        if newline.a == line.a or not self.view.substr(newline).startswith(indent) or newline.empty():
            return
        line = newline
        m = re.match("^" + indent + "[^\s[A-Za-z]]*A-Za-z[^\s]* +(.*)$", self.view.substr(newline))
        if not m:
            continue
        self.view.replace(edit, newline, before + chr(a) + after + m.group(1))

# returns indent, current line, parent line, x, a, before, after
def findParent(self):
    line = self.view.line(self.view.sel()[0])
    m = re.match(r"^(\s*)", self.view.substr(line))
    indent = m.group(1)
    row, _ = self.view.rowcol(line.end())
    prevline = line
    while True:
        newline = self.view.line(self.view.text_point(row - 1, 0))
        if newline == prevline or not self.view.substr(newline).startswith(indent):
            return indent, line, newline, "", None, None, None
        prevline = newline
        row -= 1
        m = re.match("^" + indent + "([^\s\d]*)(\d+)([^\s]* +)", self.view.substr(newline))
        if m:
            return indent, line, newline, m.group(1), int(m.group(2)) + 1, None, m.group(3)
        m = re.match("^" + indent + "([^\s\w]*)([A-Za-z])([^\s]* +)", self.view.substr(newline))
        if m:
            return indent, line, newline, m.group(1), None, ord(m.group(2)) + 1, m.group(3)
        m = re.match("^" + indent + "([^\s\d]+ +)", self.view.substr(newline))
        if m:
            return indent, line, newline, m.group(1), None, None, None

class ListContinueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        indent, line, _, before, x, a, after = findParent(self)
        if x:
            self.view.insert(edit, line.end(), before + str(x) + after)
            correctNum(self, edit, self.view.line(line), indent, x, before, after)
        elif a:
            self.view.insert(edit, line.end(), before + chr(a) + after)
            correctAlpha(self, edit, self.view.line(line), indent, a, before, after)
        else:
            self.view.insert(edit, line.end(), before)


class ListFixCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        indent, line, _, before, x, a, after = findParent(self)
        row, _ = self.view.rowcol(line.end())
        newline = self.view.line(self.view.text_point(row - 1, 0))
        if x:
            correctNum(self, edit, newline, indent, x-1, before, after)
        elif a:
            correctAlpha(self, edit, newline, indent, a-1, before, after)

class ListUpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("got it")
        _, _, newline, _, _, _, _ = findParent(self)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(newline.b, newline.b))



