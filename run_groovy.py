import sublime
import sublime_plugin
import subprocess
import os
import tempfile
import Default

class RunGroovyCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = sublime.active_window()
        view = window.active_view() if window else None
        file_name = view.file_name() if view else None
        cwd = os.path.dirname(file_name) if file_name else os.getcwd()
        encoding = view.encoding() if str(view.encoding()) != 'Undefined' else 'UTF-8'

        window.run_command('exec_run_groovy', {
            'file_name': file_name,
            'encoding': encoding,
            'working_dir': cwd
        })

class ExecRunGroovyCommand(Default.exec.ExecCommand):
    view = None
    temp_file = None
    temp_dir = tempfile.gettempdir()

    def run(self, file_name=None, working_dir='', encoding='UTF-8'):
        self.view = sublime.active_window().active_view()

        if self.__is_selection_available():
            self.temp_file = self.__copy_selection_to_temp(working_dir, encoding)
            file_name = self.temp_file.name
        elif self.__is_scratch_file():
            self.temp_file = self.__copy_buffer_to_temp(working_dir, encoding)
            file_name = self.temp_file.name

        super().run(cmd=["groovyclient", file_name], encoding=encoding, working_dir=working_dir)

    def __is_selection_available(self):
        if self.view.sel():
            for region in self.view.sel():
                if not region.empty():
                    return True

        return False

    def __is_scratch_file(self):
        return False if self.view.file_name() else True

    def __copy_selection_to_temp(self, working_dir, encoding):
        file = self.__generate_temp_file(working_dir)
        contents = self.__get_selection_content(self.view)
        file.write(bytes(contents, encoding))
        file.close()

        return file

    def __generate_temp_file(self, working_dir):
    	try:
        	return tempfile.NamedTemporaryFile(suffix='.groovy', prefix='gs-', dir=working_dir, delete=False)
    	except PermissionError:
    		return tempfile.NamedTemporaryFile(suffix='.groovy', prefix='gs-', dir=self.temp_dir, delete=False)

    def __get_selection_content(self, view):
        text = []

        if view.sel():
            for region in view.sel():
                if not region.empty():
                    text.append(view.substr(region))

        return ''.join(text)

    def __copy_buffer_to_temp(self, working_dir, encoding):
        file = self.__generate_temp_file(working_dir)
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        file.write(bytes(contents, encoding))
        file.close()

        return file

    def on_finished(self, proc):
        super().on_finished(proc)
        self.__delete_if_temp_file_available()

    def __delete_if_temp_file_available(self):
        if self.temp_file:
            os.unlink(self.temp_file.name)
