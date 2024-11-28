import unittest
from unittest.mock import patch, MagicMock
import subprocess
from visualize_graph import get_commit_history, build_graph, save_graph_to_file, main


class TestCommitVisualizer(unittest.TestCase):

    @patch('your_module.Repo')
    def test_get_commit_history_empty(self, mock_repo):
        mock_repo.return_value.iter_commits.return_value = []

        result = get_commit_history('some/path', 'some_file.py')
        self.assertEqual(result, [])

    @patch('your_module.Repo')
    def test_get_commit_history_with_commits(self, mock_repo):
        mock_commit = MagicMock()
        mock_commit.hexsha = '12345'
        mock_commit.stats.files = {'some_file.py': {'lines': 1}}

        mock_repo.return_value.iter_commits.return_value = [mock_commit]

        result = get_commit_history('some/path', 'some_file.py')
        self.assertEqual(result, [mock_commit])

    def test_build_graph(self):
        mock_commit_1 = MagicMock()
        mock_commit_1.hexsha = '12345'
        mock_commit_1.parents = []

        mock_commit_2 = MagicMock()
        mock_commit_2.hexsha = '67890'
        mock_commit_2.parents = [mock_commit_1]

        commits = [mock_commit_2]
        graph_data = build_graph(commits)

        expected_graph_data = "digraph G {\n  \"12345\" -> \"67890\";\n}\n"
        self.assertEqual(graph_data, expected_graph_data)

    @patch('your_module.subprocess.run')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_graph_to_file_success(self, mock_open, mock_subprocess):
        mock_subprocess.return_value = None

        graph_data = "digraph G {\n}"
        output_path = 'output.png'
        graph_visualizer_path = 'dot'

        save_graph_to_file(graph_data, output_path, graph_visualizer_path)

        # Проверка открытия файла
        mock_open.assert_called_once_with('graph.dot', 'w')
        # Проверка вызова subprocess.run
        mock_subprocess.assert_called_once_with([graph_visualizer_path, '-Tpng', 'graph.dot', '-o', output_path],
                                                check=True)

    @patch('your_module.subprocess.run')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_graph_to_file_failure(self, mock_open, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'cmd')

        graph_data = "digraph G {\n}"
        output_path = 'output.png'
        graph_visualizer_path = 'dot'

        with self.assertRaises(SystemExit):
            save_graph_to_file(graph_data, output_path, graph_visualizer_path)

    @patch('your_module.get_commit_history')
    @patch('your_module.build_graph')
    @patch('your_module.save_graph_to_file')
    @patch('your_module.os.path.isdir', return_value=True)
    @patch('your_module.sys.exit')
    def test_main_success(self, mock_exit, mock_save_graph, mock_build_graph, mock_get_commit_history):
        mock_get_commit_history.return_value = [MagicMock()]
        mock_build_graph.return_value = "graph data"

        with patch('argparse.ArgumentParser.parse_args',
                   return_value=MagicMock(repo_path='repo', graph_visualizer_path='path', output_path='output.png',
                                          filename='some_file.py')):
            main()
            mock_save_graph.assert_called_once()

    @patch('your_module.get_commit_history')
    @patch('your_module.os.path.isdir', return_value=False)
    @patch('your_module.sys.exit')
    def test_main_repo_not_exist(self, mock_exit, mock_isdir, mock_get_commit_history):
        with self.assertRaises(SystemExit):
            main()
        mock_exit.assert_called_once()

    @patch('your_module.os.path.isdir', return_value=True)
    @patch('your_module.sys.exit')
    def test_main_no_commits(self, mock_exit, mock_isdir, mock_get_commit_history):
        mock_get_commit_history.return_value = []

        with self.assertRaises(SystemExit):
            main()
        mock_exit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
