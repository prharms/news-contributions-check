from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from news_contribution_check.cli import cli


def _make_mock_result(csv_path: Path):
    class RF:
        def __init__(self, main_results):
            self.main_results = main_results
    return SimpleNamespace(result_files=RF(csv_path))


def test_cli_debug_branch_calls_main():
    with patch('news_contribution_check.cli.AppConfig') as mock_cfg_cls, \
         patch('news_contribution_check.cli.main') as mock_main, \
         patch('pathlib.Path.exists', return_value=True):
        mock_cfg = Mock()
        mock_cfg.data_directory = 'data'
        mock_cfg.output_directory = 'output'
        mock_cfg_cls.return_value = mock_cfg
        with patch('sys.argv', ['script', 'testfile.docx', '--debug']):
            cli()
        mock_main.assert_called_once()


def test_cli_quiet_branch_calls_main():
    with patch('news_contribution_check.cli.AppConfig') as mock_cfg_cls, \
         patch('news_contribution_check.cli.main') as mock_main, \
         patch('pathlib.Path.exists', return_value=True):
        mock_cfg = Mock()
        mock_cfg.data_directory = 'data'
        mock_cfg.output_directory = 'output'
        mock_cfg_cls.return_value = mock_cfg
        with patch('sys.argv', ['script', 'testfile.docx', '--quiet']):
            cli()
        mock_main.assert_called_once()


def test_cli_file_outside_data_dir_error():
    with patch('news_contribution_check.cli.AppConfig') as mock_cfg_cls, \
         patch('pathlib.Path.exists', return_value=True):
        mock_cfg = Mock()
        mock_cfg.data_directory = 'data'
        mock_cfg.output_directory = 'output'
        mock_cfg_cls.return_value = mock_cfg
        # Absolute path outside the data directory
        with patch('sys.argv', ['script', 'C:/outside/testfile.docx']):
            rc = cli()
            assert rc == 1


def test_cli_compare_to_cf_invokes_matcher(tmp_path: Path):
    with patch('news_contribution_check.cli.AppConfig') as mock_cfg_cls, \
         patch('news_contribution_check.cli.Container') as mock_container_cls, \
         patch('news_contribution_check.cli.main') as mock_main, \
         patch('pathlib.Path.exists', return_value=True):
        mock_cfg = Mock()
        mock_cfg.data_directory = 'data'
        mock_cfg.output_directory = 'output'
        mock_cfg_cls.return_value = mock_cfg

        mock_report = tmp_path / 'report.txt'
        mock_report.write_text('ok', encoding='utf-8')

        mock_matcher = Mock()
        mock_matcher.compare.return_value = mock_report
        mock_container = Mock()
        mock_container.get_cf_matcher.return_value = mock_matcher
        mock_container_cls.return_value = mock_container

        mock_main.return_value = _make_mock_result(tmp_path / 'company.csv')

        with patch('sys.argv', ['script', 'testfile.docx', '--compare-to-cf', 'cf.csv']):
            cli()

        mock_matcher.compare.assert_called_once()


def test_cli_leading_slash_branch_no_adjust():
    with patch('news_contribution_check.cli.AppConfig') as mock_cfg_cls, \
         patch('news_contribution_check.cli.main') as mock_main, \
         patch('pathlib.Path.exists', return_value=True):
        mock_cfg = Mock()
        mock_cfg.data_directory = '/config/data'
        mock_cfg.output_directory = '/config/out'
        mock_cfg_cls.return_value = mock_cfg
        with patch('sys.argv', ['script', '/config/data/testfile.docx']):
            cli()
        mock_main.assert_called_once()

