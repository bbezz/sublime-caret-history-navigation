import sublime
import sublime_plugin
import time

class CaretHistoryNavigation():
	def __init__(self):
		self.container = []
		self.current_index = -1
		self.last_position = {}

	def add(self, row, col, file_name):
		permission_to_add = True
		if bool(self.last_position):
			permission_to_add = False
			# if row != self.last_position['row'] or (row == self.last_position['row'] and abs(col - self.last_position['col']) > 1):
			self.try_insert_last_position()
			permission_to_add = True

		self.trim_right_side_of_current_index()

		if permission_to_add:
			self.container.append({'row':row, 'col':col, 'file_name':file_name})
			self.current_index += 1
			print("Add new: " + str(row) + " " + str(col))
			print("current_index: " + str(self.current_index))

		self.last_position = {'row':row, 'col': col, 'file_name':file_name}
		print("last_position: row " + str(row) + " " + str(col))
		self.lenght_control(200)

	def add2(self, row, col, file_name):
		if not bool(self.last_position):
			self.last_position = {'row':row, 'col': col, 'file_name':file_name}
			print("_last_position: " + str(row) + " " + str(col))
			print("_current_index: " + str(self.current_index))
			return

		self.container.append(self.last_position)
		self.current_index += 1
		self.last_position = {'row':row, 'col': col, 'file_name':file_name}
		print("save new: " + str(self.container[-1]['row']) + " " + str(self.container[-1]['col']))
		print("current_index: " + str(self.current_index))
		print("last_position: " + str(row) + " " + str(col))

	def update_last_position(self, row, col, file_name):
		print(">>> update_last_position")
		self.last_position = {'row':row, 'col': col, 'file_name':file_name}
		print("_last_position: " + str(row) + " " + str(col))
		print("_current_index: " + str(self.current_index))

	def last_position_to_container(self):
		print(">>> last_position_to_container")
		if bool(self.container):
			print(">>> -1: " + str(self.container[-1]) + " " + str(self.last_position))
		is_needed_add = False
		if not bool(self.container):
			print(">>> last_position_to_container 1")
			is_needed_add = True
		elif self.container[-1] != self.last_position:
			print(">>> last_position_to_container 1")
			is_needed_add = True

		if is_needed_add == True:
			self.container.append(self.last_position)
			self.current_index += 1
			self.lenght_control(30)
			print("save new: " + str(self.container[-1]['row']) + " " + str(self.container[-1]['col']))
			print("current_index: " + str(self.current_index))

	def lenght_control(self, max_lenght):
		if len(self.container) > max_lenght:
			self.container = self.container[-max_lenght:]
			self.current_index = max_lenght - 1

	def try_insert_last_position(self):
		# if self.last_position['row'] == self.container[-1]['row'] and abs(self.last_position['col'] - self.container[-1]['col']) > 1:
		if self.last_position != self.container[-1]:
			self.container.append(self.last_position)
			self.current_index += 1

	def trim_right_side_of_current_index(self):
		self.container = self.container[:self.current_index + 1]

	def is_back_move_available(self):
		self.try_insert_last_position()
		result = True
		if self.current_index == 0:
			result = False
		return result

	def back_move(self):		
		self.current_index -= 1
		return self.current_position()

	def is_forward_move_available(self):
		result = True
		if (self.current_index == len(self.container) - 1):
			result = False
		return result

	def forward_move(self):
		self.current_index += 1
		return self.current_position()

	def current_position(self):
		return self.container[self.current_index]

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
		self.general_time = time.time()
		self.is_needed_save = False

	def on_activated(self, view):
		if command_controller.is_was_commmand() == False:
			(row,col) = view.rowcol(view.sel()[0].begin())
			# caret_history_navigation.add(row, col, view.file_name())
			# caret_history_navigation.add2(row, col, view.file_name())
			caret_history_navigation.update_last_position(row, col, view.file_name())

	def on_load(self, view):
		current_position = caret_history_navigation.current_position()
		position = view.text_point(current_position['row'], current_position['col'])
		view.sel().clear()
		view.sel().add(sublime.Region(position))
		view.show(position)

	def on_post_text_command(self, view, name, args):
		if name == "scroll_lines" or name == "context_menu" or name == "paste":
			return

		elapsed_time = time.time() - self.general_time
		self.general_time = time.time()

		# if self.is_needed_save == False:

		# if self.is_needed_save == True:
		# if elapsed_time > 1:
			# return

		# if self.is_needed_save == False:
		# 	if elapsed_time > 1:
		# 		self.is_needed_save = True
		# 	return

		# if self.is_needed_save == True:
		# 	if elapsed_time < 1:
		# 		return

		print(elapsed_time)

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
		else:
			if elapsed_time > 1:
				caret_history_navigation.last_position_to_container()

			(row,col) = view.rowcol(view.sel()[0].begin())
			caret_history_navigation.update_last_position(row, col, view.file_name())

			# (row,col) = view.rowcol(view.sel()[0].begin())
			# caret_history_navigation.add(row, col, view.file_name())
			# caret_history_navigation.add2(row, col, view.file_name())
			# self.is_needed_save = False

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		command_controller.is_was_command_set_state(True)
		if caret_history_navigation.is_back_move_available():
			caret_position = caret_history_navigation.back_move()
			print(caret_position)
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
