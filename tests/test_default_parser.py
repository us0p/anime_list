import io
import sys
from unittest import TestCase
from src.parsers.default_parser import DefaultArgumentParser

class TestDefaultParser(TestCase):
    def setup_stdout_redirect(self):
        default_stdout = sys.stdout
        stdout = io.StringIO()
        sys.stdout = stdout
        return (default_stdout, stdout)

    def setup_stderr_redirect(self):
        default_stderr = sys.stderr
        stderr = io.StringIO()
        sys.stderr = stderr
        return (default_stderr, stderr)

    def test_empty_args_prints_help_message(self):
        default_stdout, stdout = self.setup_stdout_redirect()
        default_parser = DefaultArgumentParser()
        try:
            default_parser.parse([])
            raise Exception("Should have failed with argument error")
        except SystemExit:
            sys.stdout = default_stdout
            stdout.seek(0)
            empty_arguments_message = stdout.readlines()
            default_stdout, stdout = self.setup_stdout_redirect()
            try:
                default_parser._parser.parse_args(["-h"])
            except SystemExit:
                sys.stdout = default_stdout
                stdout.seek(0)
                default_help_message = stdout.readlines()
                self.assertEqual(
                    empty_arguments_message,
                    default_help_message
                )
                 
    def test_add_expects_anime_id(self):
        default_stderr, stderr = self.setup_stderr_redirect()
        default_parser = DefaultArgumentParser()
        try:
            default_parser.parse(["add"])
            raise Exception("Should have failed with missing anime_id")
        except SystemExit:
            sys.stderr = default_stderr
            stderr.seek(0)
            expected_message_lines = [
                'usage: Anime List add [-h] anime_id\n',
                'Anime List add: error: the following arguments are required: anime_id\n'
            ]
            self.assertEqual(
                    expected_message_lines,
                    stderr.readlines()
            )

    def test_remove_expects_anime_id(self):
        default_stderr, stderr = self.setup_stderr_redirect()
        default_parser = DefaultArgumentParser()
        try:
            default_parser.parse(["remove"])
            raise Exception("Should have failed with missing anime_id")
        except SystemExit:
            sys.stderr = default_stderr
            stderr.seek(0)
            expected_message_lines = [
                'usage: Anime List remove [-h] anime_id\n',
                'Anime List remove: error: the following arguments are required: anime_id\n'
            ]
            self.assertEqual(
                    expected_message_lines,
                    stderr.readlines()
            )

    def test_update_expects_anime_id(self):
        default_stderr, stderr = self.setup_stderr_redirect()
        default_parser = DefaultArgumentParser()
        try:
            default_parser.parse(["update"])
            raise Exception("Should have failed with missing anime_id")
        except SystemExit:
            sys.stderr = default_stderr
            stderr.seek(0)
            expected_message_lines = [
                'usage: Anime List update [-h] [-us UPDATE_SEASONS] [-ue UPDATE_EPISODES]\n',
                '                         anime_id\n',
                'Anime List update: error: the following arguments are required: anime_id\n'
            ]
            self.assertEqual(
                    expected_message_lines,
                    stderr.readlines()
            )

    def test_update_expects_at_least_one_option(self):
        default_stderr, stderr = self.setup_stderr_redirect()
        default_stdout, stdout = self.setup_stdout_redirect()
        default_parser = DefaultArgumentParser()
        try:
            default_parser.parse(["update", '1'])
            raise Exception("Should have failed with missing obligatory option")
        except SystemExit:
            sys.stderr = default_stderr
            sys.stdout= default_stdout
            stdout.seek(0)
            stderr.seek(0)
            expected_message_line = [
                'usage: Anime List update [-h] [-us UPDATE_SEASONS] [-ue UPDATE_EPISODES]\n',
                '                         anime_id\n',
                '\n',
                'positional arguments:\n',
                '  anime_id\n',
                '\n',
                'options:\n',
                '  -h, --help            show this help message and exit\n',
                '  -us UPDATE_SEASONS, --update-seasons UPDATE_SEASONS\n', '                        Update the number of watched seasons.\n', '  -ue UPDATE_EPISODES, --update-episodes UPDATE_EPISODES\n', '                        Update the number of watched episodes, also upates the\n', '                        last time watched column with the current date.\n'
            ]
            expected_error_message_line = [
                'Anime List update: error: must provide update_seasons or update_episodes\n'
            ]
            self.assertEqual(
                expected_message_line,
                stdout.readlines()
            )
            self.assertEqual(
                    expected_error_message_line,
                    stderr.readlines()
            )

    def test_add_command_to_namespace(self):
        default_parser = DefaultArgumentParser()
        namespace = default_parser.parse(["add", '1'])
        self.assertEqual(namespace.anime_id, 1)
        self.assertEqual(namespace.command, "add")
