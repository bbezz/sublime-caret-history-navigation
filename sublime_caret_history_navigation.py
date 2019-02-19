import sublime
import sublime_plugin
import time

class Window:
	def __init__(self, id):
		self.id = id
		self.history = []
		self.current_index = -1

class Position:
	def __init__(self, file_name, row, col):
		self.file_name = file_name
		self.row = row
		self.col = col

class Navigator():
	def __init__(self):
		self.windows = []
		self.window = None
		self.is_was_open_file = False
		self.settings = sublime.load_settings("Default.sublime-settings")

	def insert_window(self, id):
		if not id in [window.id for window in self.windows]:
			self.windows.append(Window(id))

	def set_active_window(self, id):
		index = [i.id for i in self.windows].index(id)
		self.window = self.windows[index]

	def position(self):
		return self.window.history[self.window.current_index]

	def add(self, file_name, row, col):
		new_position = Position(file_name, row, col)
		if not bool(self.window.history) or (self.position().row != new_position.row 
			or self.position().col != new_position.col 
			or self.position().file_name != new_position.file_name):
			self.window.current_index += 1
			self.window.history.insert(self.window.current_index, new_position)
			self.lenght_control()

	def lenght_control(self):
		max_history_lenght = self.settings.get('max_history_lenght', 10)
		if len(self.window.history) <= max_history_lenght:
			return

		if self.window.current_index < len(self.window.history) - 1:
			self.window.history = self.window.history[:-1]
			return

		self.window.history = self.window.history[1:]
		self.window.current_index -= 1

	def clear_history_after_current_index(self):
		del self.window.history[self.window.current_index + 1:]

	def is_back_move_available(self):
		return self.window.current_index > 0

	def is_forward_move_available(self):
		return self.window.current_index < len(self.window.history) - 1

	def back_move_position(self):
		self.window.current_index -= 1
		return self.position()

	def forward_move_position(self):
		self.window.current_index += 1
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
		self.last_activated_file_name = None

	def on_activated(self, view):
		active_file_name = view.window().active_view().file_name()
		if self.last_activated_file_name != None and self.last_activated_file_name == active_file_name:
			return
		self.last_activated_file_name = active_file_name

		window_id = view.window().id()
		navigator.insert_window(window_id)
		navigator.set_active_window(window_id)

		if navigator.is_was_open_file:
			navigator.is_was_open_file = False
			if bool(navigator.window.history):
				position = view.text_point(navigator.position().row, navigator.position().col)
				view.sel().clear()
				view.sel().add(sublime.Region(position))
				view.show(position)

		add_active_position(view)

	def on_deactivated(self, view):
		if command_controller.is_was_commmand() == False:
			add_active_position(view)

	def on_text_command(self, view, name, args):
		if name == "move_to":
			add_active_position(view)
			return

		elapsed_time = time.time() - self.general_time
		self.general_time = time.time()

		if name in self.ignored_command:
			return

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
			return

		if elapsed_time > navigator.settings.get('downtime_to_save_position', 1.0):
			add_active_position(view)

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		if command_controller.is_was_commmand() == False:
			add_active_position(sublime.active_window().active_view())

		if navigator.is_back_move_available():
			command_controller.is_was_command_set_state(True)
			position = navigator.back_move_position()
			caret_move(self.view, position)

			if navigator.settings.get('back_move_cleans_history_after_current_position', False):
				navigator.clear_history_after_current_index()

class SublimeCaretHistoryNavigationForwardMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		if command_controller.is_was_commmand() == False:
			add_active_position(sublime.active_window().active_view())

		if navigator.is_forward_move_available():
			command_controller.is_was_command_set_state(True)
			position = navigator.forward_move_position()
			caret_move(self.view, position)

def add_active_position(view):
	(row,col) = view.rowcol(view.sel()[0].begin())
	navigator.add(view.file_name(), row, col)

def caret_move(view, caret_position):
	active_view = sublime.active_window().find_open_file(caret_position.file_name)

	if active_view == None:
		active_view = view.window().open_file(caret_position.file_name)
		navigator.is_was_open_file = True

	sublime.active_window().focus_view(active_view)

	position = active_view.text_point(caret_position.row, caret_position.col)
	active_view.sel().clear()
	active_view.sel().add(sublime.Region(position))
	active_view.show(position)
