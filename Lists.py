import sublime, sublime_plugin, re

class ListItemCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		line = self.view.line(self.view.sel()[0])
		self.view.sel().clear()
		m = re.match(r"^(\s*[^ ]*)(\d+)([^ ]* +)", self.view.substr(line))
		self.view.sel().add(sublime.Region(line.b, line.b))
		if not m:
			self.view.insert(edit, line.end(), "\n")
			return
		self.view.insert(edit, line.end(), "\n" + m.group(1) + m.group(2) + m.group(3))

		while True:
			row, _ = self.view.rowcol(line.end())
			newline = self.view.line(self.view.text_point(row + 1, 0))
			if newline == line:
				return
			line = newline
			m = re.match(r"^(\s*)(\d+)(.*)$", self.view.substr(line))
			if not m:
				return
			self.view.replace(edit, line, m.group(1) + str(int(m.group(2)) + 1) + m.group(3))

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
