import sublime
import sublime_plugin
import time

class CaretHistoryNavigation():
	def __init__(self):
		self.container = []
		self.current_index = -1
		self.last_position = {}

	def update_last_position(self, row, col, file_name):
		self.last_position = {'row':row, 'col': col, 'file_name':file_name}
		print("Update last position: " + str(row) + " " + str(col) + ". Current index: " + str(self.current_index))

	def save_last_position(self):
		print("\nCALL: save_last_position")
		if not bool(self.container) or self.container[-1] != self.last_position:
			self.container.append(self.last_position)
			self.current_index += 1
			self.lenght_control(30)
			print("Save last position: " + str(self.container[-1]['row']) + " " + str(self.container[-1]['col']) + ". Current index: " + str(self.current_index))

	def trim_right_side_of_current_index(self):
		if len(self.container) - 1 > self.current_index:
			self.container = self.container[:self.current_index + 1]
			print("After trim: " + str(len(self.container)))

	def lenght_control(self, max_lenght):
		if len(self.container) > max_lenght:
			self.container = self.container[-max_lenght:]
			self.current_index = max_lenght - 1

	def is_back_move_available(self):
		result = False
		if self.current_index > 0 or (self.current_index == 0 and len(self.container) - 1 == self.current_index):
			result = True
		return result

	def is_forward_move_available(self):
		result = False
		if self.current_index < len(self.container) - 1:
			result = True
		return result

	def back_move(self):
		if len(self.container) - 1 == self.current_index:
			self.save_last_position()

		self.current_index -= 1
		self.last_position = self.container[self.current_index]
		print("CALL: back_move. Container len: " + str(len(self.container)) + ". Current index: " + str(self.current_index))
		return self.container[self.current_index]

	def forward_move(self):
		self.current_index += 1
		self.last_position = self.container[self.current_index]
		print("CALL: forward_move. Container len: " + str(len(self.container)) + ". Current index: " + str(self.current_index))
		return self.container[self.current_index]

	def current_position(self):
		return self.container[self.current_position]

caret_history_navigation = CaretHistoryNavigation()

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

	def on_activated(self, view):
		print("on_activated: " + str(view.file_name()))
		(row,col) = view.rowcol(view.sel()[0].begin())
		caret_history_navigation.update_last_position(row, col, view.file_name())

	def on_deactivated(self, view):
		print("on_deactivated: " + str(view.file_name()))
		if command_controller.is_was_commmand() == False:
			caret_history_navigation.trim_right_side_of_current_index()
			caret_history_navigation.save_last_position()

	# def on_load(self, view):
	# 	current_position = caret_history_navigation.current_position()
	# 	position = view.text_point(current_position['row'], current_position['col'])
	# 	view.sel().clear()
	# 	view.sel().add(sublime.Region(position))
	# 	view.show(position)

	def on_post_text_command(self, view, name, args):
		print(name)
		if name == "scroll_lines" or name == "context_menu" or name == "paste":
			return

		elapsed_time = time.time() - self.general_time
		self.general_time = time.time()

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
			return

		if elapsed_time > 1:
			caret_history_navigation.trim_right_side_of_current_index()
			caret_history_navigation.save_last_position()

		(row,col) = view.rowcol(view.sel()[0].begin())
		caret_history_navigation.update_last_position(row, col, view.file_name())

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		command_controller.is_was_command_set_state(True)
		if caret_history_navigation.is_back_move_available():
			caret_position = caret_history_navigation.back_move()
			caret_move(self.view, caret_position)

class SublimeCaretHistoryNavigationForwardMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		command_controller.is_was_command_set_state(True)
		if caret_history_navigation.is_forward_move_available():
			caret_position = caret_history_navigation.forward_move()
			caret_move(self.view, caret_position)

def caret_move(view, caret_position):
	active_view = view.window().active_view()

	if active_view.file_name() != caret_position['file_name']:
		active_view = view.window().open_file(caret_position['file_name'])

	position = active_view.text_point(caret_position['row'], caret_position['col'])
	active_view.sel().clear()
	active_view.sel().add(sublime.Region(position))
	active_view.show(position)
