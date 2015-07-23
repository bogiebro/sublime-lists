import sublime, sublime_plugin, re

class ListContinueCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        line = self.view.line(self.view.sel()[0])
        m = re.match(r"^(\s*)", self.view.substr(line))
        indent = m.group(1)
        row, _ = self.view.rowcol(line.end())
        prevline = line
        while True:
            newline = self.view.line(self.view.text_point(row - 1, 0))
            if newline == prevline or not self.view.substr(newline).startswith(indent):
                return
            prevline = newline
            row -= 1

            # Test for numbered bullet
            m = re.match("^" + indent + "([^\s\d]*)(\d+)([^\s]* +)", self.view.substr(newline))
            if m:
                self.view.insert(edit, line.end(), m.group(1) + str(int(m.group(2)) + 1) + m.group(3))
                line = self.view.line(line)
                editrow, _ = self.view.rowcol(line.end())
                while True:
                    editrow += 1
                    newline = self.view.line(self.view.text_point(editrow, 0))
                    if newline.a == line.a or not self.view.substr(newline).startswith(indent) or newline.empty():
                        return
                    line = newline
                    m = re.match("^(" + indent + "[^\s\d]*)(\d+)(.*)$", self.view.substr(newline))
                    if not m:
                        continue
                    self.view.replace(edit, newline, m.group(1) + str(int(m.group(2)) + 1) + m.group(3))
                return

            # Test for static bullet
            m = re.match("^(" + indent + "[^\s]* +)", self.view.substr(newline))
            if m:
                self.view.insert(edit, line.end(), m.group(1))
                return

# class ListUpCommand(sublime_plugin.TextCommand):
#   def run(self, edit):

# class ListDownCommand(sublime_plugin.TextCommand):
#   def run(self, edit):

class SelectIndentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        line = self.view.line(self.view.sel()[0])
        m = re.match(r"^(\s*)", self.view.substr(line))
        indent = m.group(1)
        row, _ = self.view.rowcol(line.end())
        uprow = row
        downrow = row
        while True:
            newline = self.view.line(self.view.text_point(uprow - 1, 0))
            if newline == line or not self.view.substr(newline).startswith(indent):
                break
            line = newline
            uprow -= 1
        while True:
            newline = self.view.line(self.view.text_point(downrow + 1, 0))
            if newline == line or not self.view.substr(newline).startswith(indent):
                break
            line = newline
            downrow += 1
        self.view.sel().add(
            self.view.line(sublime.Region(
            self.view.text_point(uprow, 0),
            self.view.text_point(downrow, 0))))
