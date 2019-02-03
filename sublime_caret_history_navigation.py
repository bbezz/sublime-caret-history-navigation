import sublime
import sublime_plugin

class CaretHistoryNavigation():
	def __init__(self):
		self._history = []
		self._current_index = -1

	def add(self, row, col, file_view):
		self.trim_right_side_of_current_index()

		if not bool(self._history):
			print("\nAdd lock position, file name: " + str(file_view.file_name()))
			self._history.append({'row':row, 'col':col, 'lock':True, 'file_view':file_view, 'file_name':file_view.file_name()})
			self._current_index += 1
			print(self._history)
			return

		if self._history[-1]['row'] == row and abs(self._history[-1]['col'] - col) == 1:
			if self._history[-1]['lock'] == True:
				print("Add unlock position")
				self._history.append({'row':row, 'col':col, 'lock':False})
				self._current_index += 1
			else:
				print("Rewrite last unlock position")
				self._history[-1]['row'] = row
				self._history[-1]['col'] = col
			return

		if self._history[-1]['lock'] == False:
			if abs(self._history[-1]['col'] - self._history[-2]['col']) > 1:
				print("Lock -> unlock position")
				self._history[-1]['lock'] = True
			else:
				print("Remove unlock position")
				del self._history[-1]
				self._current_index -= 1

		print("Add lock position, file name: " + str(file_view.file_name()))
		self._history.append({'row':row, 'col':col, 'lock':True, 'file_view':file_view, 'file_name':file_view.file_name()})
		self._current_index += 1
		print(self._history)

	def trim_right_side_of_current_index(self):
		self._history = self._history[:self._current_index + 1]

	def is_back_move_available(self):
		result = True
		if self._current_index == 0:
			result = False
		return result

	def is_forward_move_available(self):
		result = True
		print("Forward move, indexes: current " + str(self._current_index) + ", len " + str(len(self._history) - 1))
		if (self._current_index == len(self._history) - 1):
			result = False
		return result

	def back_move(self):
		self._current_index -= 1
		print(str(self._current_index) + " -> " + str(self._history[self._current_index]) + "\n")
		return (self._history[self._current_index]['row'],
			self._history[self._current_index]['col'],
			self._history[self._current_index]['file_view'],
			self._history[self._current_index]['file_name'])

	def forward_move(self):
		self._current_index += 1
		print(str(self._current_index) + " -> " + str(self._history[self._current_index]) + "\n")
		return (self._history[self._current_index]['row'],
			self._history[self._current_index]['col'],
			self._history[self._current_index]['file_view'],
			self._history[self._current_index]['file_name'])

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
	def on_activated(self, view):
		print("ONNNN, is_was_commmand: " + str(command_controller.is_was_commmand()))
		if command_controller.is_was_commmand() == False:
			(row,col) = view.rowcol(view.sel()[0].begin())
			caret_history_navigation.add(row, col, view)

	def on_post_text_command(self, view, name, args):
		print("on_post_text_command")
		if name == "scroll_lines" or name == "context_menu":
			return

		if command_controller.is_was_commmand() == True:
			command_controller.is_was_command_set_state(False)
		else:
			(row,col) = view.rowcol(view.sel()[0].begin())
			caret_history_navigation.add(row, col, view)

class SublimeCaretHistoryNavigationBackMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		command_controller.is_was_command_set_state(True)

		if caret_history_navigation.is_back_move_available():
			(row, col, file_view, file_name) = caret_history_navigation.back_move()

			needed_view = file_view
			if (needed_view != self.view):
				print("Back not view")
				# self.view.window().focus_view(file_view)
				needed_view = self.view.window().open_file(file_name)
				print("file_view name: " + str(file_name))

			position = needed_view.text_point(row, col)
			needed_view.sel().clear()
			needed_view.sel().add(sublime.Region(position))
			needed_view.show(position)

class SublimeCaretHistoryNavigationForwardMoveCommand(sublime_plugin.TextCommand):
	def run(self, args):
		command_controller.is_was_command_set_state(True)

		print("is_forward_move_available: " + str(caret_history_navigation.is_forward_move_available()))
		if caret_history_navigation.is_forward_move_available():
			(row, col, file_view, file_name) = caret_history_navigation.forward_move()

			needed_view = file_view
			if (needed_view != self.view):
				print("Forward not view")
				# self.view.window().focus_view(file_view)
				needed_view = self.view.window().open_file(file_name)
				print("file_view name: " + str(file_name))

			position = needed_view.text_point(row, col)
			needed_view.sel().clear()
			needed_view.sel().add(sublime.Region(position))
			needed_view.show(position)
