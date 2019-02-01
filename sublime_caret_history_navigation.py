import sublime
import sublime_plugin

class CaretHistoryNavigation():
	def __init__(self):
		self._history = []
		self._current_position = -1
		self._is_back_forward_move = False

	def add(self, row, col):
		self._history.append({'row' : row, 'col' : col})
		lenght = len(self._history) - 1
		print("Added caret position: " + str(self._history[lenght]['row']) + " " + str(self._history[lenght]['col']))
		self._current_position += 1

	def back_move(self):
		print("Back move")
		self._is_back_forward_move = True
		self._current_position -= 1
		return (self._history[self._current_position]['row'], self._history[self._current_position]['col'])

	def forward_move(self):
		print("Forward move")
		self._is_back_forward_move = True
		self._current_position += 1
		return (self._history[self._current_position]['row'], self._history[self._current_position]['col'])

	def is_back_forward_move(self):
		return self._is_back_forward_move

	def сomplete_back_forward_move(self):
		self._is_back_forward_move = False
		print("сomplete_back_forward_move")

caret_history_navigation = CaretHistoryNavigation()

class CaretPositionChanged(sublime_plugin.EventListener):
	def on_post_text_command(self, view, name, args):
		if caret_history_navigation.is_back_forward_move() == True :
			caret_history_navigation.сomplete_back_forward_move()
		else :
			print("Move event")
			(row,col) = view.rowcol(view.sel()[0].begin())
			caret_history_navigation.add(row, col)

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		(row, col) = caret_history_navigation.back_move()
		position = self.view.text_point(row, col)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(position))
		self.view.show(position)

class SublimeCaretHistoryNavigationForwardMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		(row, col) = caret_history_navigation.forward_move()
		position = self.view.text_point(row, col)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(position))
		self.view.show(position)