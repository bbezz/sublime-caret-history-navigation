import sublime
import sublime_plugin
import time

class CaretHistoryNavigation():
	def __init__(self):
		self.container = []
		self.current_index = -1
		self.current_position = {}

	def update_current_position(self, row, col, file_name):
		self.current_position = {'row':row, 'col': col, 'file_name':file_name}
		print("Update current position: " + str(row) + " " + str(col) + ". Current index: " + str(self.current_index))

	def save_current_position(self):
		print("\nCALL: save_current_position")
		if self.is_empty() or self.container[-1] != self.current_position:
			self.container.append(self.current_position)
			self.current_index += 1
			self.lenght_control(30)
			print("Save current position: " + str(self.container[-1]['row']) + " " + str(self.container[-1]['col']) + ". Current index: " + str(self.current_index))

	def lenght_control(self, max_lenght):
		if len(self.container) > max_lenght:
			self.container = self.container[-max_lenght:]
			self.current_index = max_lenght - 1

	def trim_right_side_of_current_index(self):
		if len(self.container) - 1 > self.current_index:
			self.container = self.container[:self.current_index + 1]
			print("After trim: " + str(len(self.container)))

	def get_current_position(self):
		return self.current_position

	def is_empty(self):
		return not bool(self.container)

	def is_back_move_available(self):
		return bool(self.current_index > 0 or (len(self.container) - 1 == self.current_index))

	def is_forward_move_available(self):
		return bool(self.current_index < len(self.container) - 1)

	def back_move(self):
		if len(self.container) - 1 == self.current_index:
			self.save_current_position()

		self.current_index -= 1
		self.current_position = self.container[self.current_index]
		print("CALL: back_move. Container len: " + str(len(self.container)) + ". Current index: " + str(self.current_index))
		return self.current_position

	def forward_move(self):
		self.current_index += 1
		self.current_position = self.container[self.current_index]
		print("CALL: forward_move. Container len: " + str(len(self.container)) + ". Current index: " + str(self.current_index))
		return self.current_position

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
		if not caret_history_navigation.is_empty():
			current_position = caret_history_navigation.get_current_position()
			position = view.text_point(current_position['row'], current_position['col'])
			view.sel().clear()
			view.sel().add(sublime.Region(position))
			view.show(position)

		(row,col) = view.rowcol(view.sel()[0].begin())
		caret_history_navigation.update_current_position(row, col, view.file_name())

	def on_deactivated(self, view):
		if command_controller.is_was_commmand() == False:
			caret_history_navigation.trim_right_side_of_current_index()
			caret_history_navigation.save_current_position()

	def on_post_text_command(self, view, name, args):
		if name == "context_menu" or name == "paste":
			return

		elapsed_time = time.time() - self.general_time
		self.general_time = time.time()

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
			return

		if elapsed_time > 1:
			caret_history_navigation.trim_right_side_of_current_index()
			caret_history_navigation.save_current_position()

		(row,col) = view.rowcol(view.sel()[0].begin())
		caret_history_navigation.update_current_position(row, col, view.file_name())

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
