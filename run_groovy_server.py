import sublime
import sublime_plugin
import subprocess
import os
import tempfile
import Default
from Default.paragraph import expand_to_paragraph

class RunGroovyCommand(sublime_plugin.WindowCommand):
    def run(self, current=False):
        window = sublime.active_window()
        view = window.active_view() if window else None
        file_name = view.file_name() if view else None
        cwd = os.path.dirname(file_name) if file_name else os.getcwd()
        encoding = view.encoding() if str(view.encoding()) != 'Undefined' else 'UTF-8'

        window.run_command('exec_run_groovy', {
            'working_dir': cwd,
            'current': current,
            'encoding': encoding
        })

class ExecRunGroovyCommand(Default.exec.ExecCommand):
    view = None
    temp_file = None

    def run(self, working_dir='', current=False, encoding='UTF-8'):
        self.view = sublime.active_window().active_view()
        self.temp_file = self.__generate_temp_file()

        if current:
            contents = self.__get_current_paragraph_contents()
        elif self.__is_selection_available():
            contents = self.__get_selection_contents()
        else:
            contents = self.__get_buffer_contents()

        self.temp_file.write(bytes(contents, encoding))
        self.temp_file.close()
        super().run(cmd = [
            'groovyclient',
            '-c', encoding,
            '-cp', '/home/josenicomaia/workspaces/josenicomaia/groovyserver/src/groovy:/home/josenicomaia/workspaces/josenicomaia/groovyserver/src/java',
            self.temp_file.name
        ], encoding=encoding, working_dir=working_dir)

    def __generate_temp_file(self):
        return tempfile.NamedTemporaryFile(suffix='.groovy', prefix='gs-', dir=tempfile.gettempdir(), delete=False)

    def __get_current_paragraph_contents(self):
        text = []

        if self.view.sel():
            for region in self.view.sel():
                text.append(self.view.substr(expand_to_paragraph(self.view, region.b)))

        return '\n\n'.join(text)

    def __is_selection_available(self):
        if self.view.sel():
            for region in self.view.sel():
                if not region.empty():
                    return True

        return False

    def __get_selection_contents(self):
        text = []

        if self.view.sel():
            for region in self.view.sel():
                if not region.empty():
                    text.append(self.view.substr(region))

        return '\n\n'.join(text)

    def __get_buffer_contents(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def on_finished(self, proc):
        super().on_finished(proc)
        self.__delete_if_temp_file_available()

    def __delete_if_temp_file_available(self):
        if self.temp_file:
            os.unlink(self.temp_file.name)
