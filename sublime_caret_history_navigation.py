import sublime
import sublime_plugin
import time

class Window:
	def __init__(self, id):
		self.id = id
		self.history = []
		self.actual_index = -1

class Position:
	def __init__(self, file_name, row, col):
		self.file_name = file_name
		self.row = row
		self.col = col

class Navigator():
	def __init__(self):
		self.windows = []
		self.window = None

	def is_window_exists(self, id):
		return id in [i.id for i in self.windows]

	def add_window(self, id):
		self.windows.append(Window(id))

	def set_active_window(self, id):
		index = [i.id for i in self.windows].index(id)
		self.window = self.windows[index]

	def position(self):
		return self.window.history[self.window.actual_index]

	def add(self, file_name, row, col):
		new_position = Position(file_name, row, col)
		if not bool(self.window.history) or (self.position().row != new_position.row 
			or self.position().col != new_position.col 
			or self.position().file_name != new_position.file_name):
			self.window.actual_index += 1
			self.window.history.insert(self.window.actual_index, new_position)
			self.lenght_control(10)

	def lenght_control(self, max_lenght):
		if len(self.window.history) <= max_lenght:
			return

		if self.window.actual_index < len(self.window.history) - 1:
			self.window.history = self.window.history[:-1]
			return

		self.window.history = self.window.history[1:]
		self.window.actual_index -= 1

	def is_back_move_available(self):
		return self.window.actual_index > 0

	def is_forward_move_available(self):
		return self.window.actual_index < len(self.window.history) - 1

	def back_move(self):
		self.window.actual_index -= 1
		return self.position()

	def forward_move(self):
		self.window.actual_index += 1
		return self.position()

navigator = Navigator()

class CommandController():
	def __init__(self):
		self._is_was_command = False

	def is_was_commmand(self):
		return self._is_was_command

	def is_was_command_set_state(self, state):
		self._is_was_command = state

command_controller = CommandController()

class CaretPositionChanged(sublime_plugin.EventListener):
	def __init__(self):
		self.general_time = time.time() - 1
		self.ignored_command = ['context_menu', 'paste', 'sublime_caret_history_navigation_back_move', 'sublime_caret_history_navigation_forward_move']

	def on_activated(self, view):
		window_id = view.window().id()
		if not navigator.is_window_exists(window_id):
			navigator.add_window(window_id)

		if navigator.window != None and navigator.position().file_name == view.window().active_view().file_name():
			return

		navigator.set_active_window(window_id)

		if bool(navigator.window.history):
			position = view.text_point(navigator.position().row, navigator.position().col)
			view.sel().clear()
			view.sel().add(sublime.Region(position))
			view.show(position)

		(row,col) = view.rowcol(view.sel()[0].begin())
		navigator.add(view.file_name(), row, col)

	def on_text_command(self, view, name, args):
		elapsed_time = time.time() - self.general_time
		self.general_time = time.time()

		if name in self.ignored_command:
			return

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
			return

		if elapsed_time > 1:
			(row,col) = view.rowcol(view.sel()[0].begin())
			navigator.add(view.file_name(), row, col)

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		adding_position_before_move_command()

		if navigator.is_back_move_available():
			command_controller.is_was_command_set_state(True)
			caret_position = navigator.back_move()
			caret_move(self.view, caret_position)

class SublimeCaretHistoryNavigationForwardMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		adding_position_before_move_command()

		if navigator.is_forward_move_available():
			command_controller.is_was_command_set_state(True)
			caret_position = navigator.forward_move()
			caret_move(self.view, caret_position)

def adding_position_before_move_command():
	if command_controller.is_was_commmand() == False:
			active_view = sublime.active_window().active_view()
			(row,col) = active_view.rowcol(active_view.sel()[0].begin())
			navigator.add(active_view.file_name(), row, col)

def caret_move(view, caret_position):
	active_view = view.window().active_view()

	if active_view.file_name() != caret_position.file_name:
		active_view = view.window().open_file(caret_position.file_name)

	position = active_view.text_point(caret_position.row, caret_position.col)
	active_view.sel().clear()
	active_view.sel().add(sublime.Region(position))
	active_view.show(position)
