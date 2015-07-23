import sublime, sublime_plugin, re

class Changer:
    def __init__(self, view):
        self.view = view
        self.line = self.view.line(self.view.sel()[0])
        m = re.match(r"^(\s*)", self.view.substr(self.line))
        self.indent = m.group(1)
        row, _ = self.view.rowcol(self.line.end())
        self.editrow = row
        prevline = self.line
        while True:
            self.pline = self.view.line(self.view.text_point(row - 1, 0))
            if self.pline == prevline or not self.view.substr(self.pline).startswith(self.indent):
                self.before = ""
                return
            prevline = self.pline
            row -= 1
            m = re.match("^" + self.indent + "([^\s\d]*)(\d+)([^\s]* +)", self.view.substr(self.pline))
            if m:
                self.before, self.x, self.after = m.group(1), int(m.group(2)) + 1, m.group(3)
                return
            m = re.match("^" + self.indent + "([^\s\w]*)([A-Za-z])([^\s]* +)", self.view.substr(self.pline))
            if m:
                self.before, self.a, self.after = m.group(1), ord(m.group(2)) + 1, m.group(3)
                return
            m = re.match("^" + self.indent + "([^\s\d]+ +)", self.view.substr(self.pline))
            if m:
                self.before = m.group(1)
                return
    def __iter__(self):
        return self
    def __next__(self):
        self.editrow += 1
        newline = self.view.line(self.view.text_point(self.editrow, 0))
        if newline.a == self.line.a or not self.view.substr(newline).startswith(self.indent) or newline.empty():
            raise StopIteration
        self.line = newline
        return self.view.substr(newline)

def correctNum(ch, edit):
    for c in iter(ch):
        m = re.match("^" + ch.indent + "[^\s\d]*\d+[^\s]* +(.*)$", c)
        if not m:
            continue
        ch.x += 1
        ch.view.replace(edit, ch.line, ch.indent + ch.before + str(ch.x) + ch.after + m.group(1))

def correctAlpha(ch, edit):
    for c in ch:
        m = re.match("^" + ch.indent + "[^\s[A-Za-z]]*A-Za-z[^\s]* +(.*)$", c)
        if not m:
            continue
        ch.a += 1
        ch.view.replace(edit, ch.line, ch.indent + ch.before + chr(ch.a) + ch.after + m.group(1))

class ListContinueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ch = Changer(self.view)
        if hasattr(ch, 'x'):
            self.view.insert(edit, ch.line.end(), ch.before + str(ch.x) + ch.after)
            correctNum(ch, edit)
        elif hasattr(ch, 'a'):
            self.view.insert(edit, ch.line.end(), ch.before + chr(ch.a) + ch.after)
            correctAlpha(ch, edit)
        else:
            self.view.insert(edit, ch.line.end(), ch.before)

class ListFixCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ch = Changer(self.view)
        ch.line = ch.pline
        ch.editrow -= 1
        if hasattr(ch, 'x'):
            ch.x -= 1
            correctNum(ch, edit)
        elif hasattr(ch, 'a'):
            ch.a -= 1
            correctAlpha(ch, edit)
        else:  
            print("No attrs")

class ListUpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ch = Changer(self.view)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(ch.pline.b, ch.pline.b))

class ListDownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ch = Changer(self.view)
        for _ in ch:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(ch.line.b, ch.line.b))
            return
