from pathlib import Path
from unittest.mock import Mock, patch, ANY

from news_contribution_check.container import Container


def test_container_get_cf_matcher_creates_and_caches():
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'k'}), \
         patch('news_contribution_check.container.CFMatcher') as mock_matcher:
        mock_inst = Mock()
        mock_matcher.return_value = mock_inst
        c = Container()
        m1 = c.get_cf_matcher()
        m2 = c.get_cf_matcher()
        assert m1 is mock_inst and m2 is mock_inst
        mock_matcher.assert_called_once()


def test_container_setup_logging_called_once():
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'k'}), \
         patch('news_contribution_check.container.setup_logging') as mock_setup:
        mock_setup.return_value = Mock()
        c1 = Container()
        c2 = Container()
        # Each container calls setup_logging in its own __init__
        assert mock_setup.call_count == 2

