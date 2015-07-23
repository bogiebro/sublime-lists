import sublime, sublime_plugin, re

# makes corrections, starting the line after 'line' with x+1
def correct(self, edit, line, indent, x, before, after):
    editrow, _ = self.view.rowcol(line.end())
    while True:
        editrow += 1
        x += 1
        newline = self.view.line(self.view.text_point(editrow, 0))
        if newline.a == line.a or not self.view.substr(newline).startswith(indent) or newline.empty():
            return
        line = newline
        m = re.match("^" + indent + "[^\s\d]*\d+[^\s]* +(.*)$", self.view.substr(newline))
        if not m:
            continue
        self.view.replace(edit, newline, before + str(x) + after + m.group(1))

# returns indent of parent, current line, x of parent, before of parent, after of parent
def findParent(self):
    line = self.view.line(self.view.sel()[0])
    m = re.match(r"^(\s*)", self.view.substr(line))
    indent = m.group(1)
    row, _ = self.view.rowcol(line.end())
    prevline = line
    while True:
        newline = self.view.line(self.view.text_point(row - 1, 0))
        if newline == prevline or not self.view.substr(newline).startswith(indent):
            return indent, line, "", -1, ""
        prevline = newline
        row -= 1
        m = re.match("^" + indent + "([^\s\d]*)(\d+)([^\s]* +)", self.view.substr(newline))
        if m:
            return indent, line, m.group(1), int(m.group(2)) + 1, m.group(3)
        m = re.match("^" + indent + "([^\s\d]+ +)", self.view.substr(newline))
        if m:
            return indent, line, m.group(1), -1, ""

class ListContinueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        indent, line, before, x, after = findParent(self)
        if x < 0:
            self.view.insert(edit, line.end(), before)
        else:
            self.view.insert(edit, line.end(), before + str(x) + after)
            correct(self, edit, self.view.line(line), indent, x, before, after)

class ListFixCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        indent, line, before, x, after = findParent(self)
        row, _ = self.view.rowcol(line.end())
        newline = self.view.line(self.view.text_point(row - 1, 0))
        correct(self, edit, newline, indent, x-1, before, after)


