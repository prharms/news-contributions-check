"""Tests for config module."""

import re
from datetime import datetime
from unittest.mock import patch

from news_contribution_check.config import get_timestamped_filename


class TestConfig:
    """Test cases for configuration functions."""

    def test_get_timestamped_filename_default(self) -> None:
        """Test timestamped filename generation with default extension."""
        filename = get_timestamped_filename("test_file")
        
        # Should match pattern: test_file_YYYYMMDD_HHMMSS.csv
        pattern = r"test_file_\d{8}_\d{6}\.csv"
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_get_timestamped_filename_custom_extension(self) -> None:
        """Test timestamped filename generation with custom extension."""
        filename = get_timestamped_filename("data_export", "json")
        
        # Should match pattern: data_export_YYYYMMDD_HHMMSS.json
        pattern = r"data_export_\d{8}_\d{6}\.json"
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_get_timestamped_filename_specific_time(self) -> None:
        """Test timestamped filename generation with mocked time."""
        # Mock datetime.now() to return a specific time
        mock_datetime = datetime(2024, 1, 15, 14, 30, 45)
        
        with patch('news_contribution_check.config.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            filename = get_timestamped_filename("report")
            
            expected = "report_20240115_143045.csv"
            assert filename == expected

    def test_get_timestamped_filename_empty_base_name(self) -> None:
        """Test timestamped filename generation with empty base name."""
        filename = get_timestamped_filename("")
        
        # Should match pattern: _YYYYMMDD_HHMMSS.csv
        pattern = r"_\d{8}_\d{6}\.csv"
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_get_timestamped_filename_special_characters(self) -> None:
        """Test timestamped filename generation with special characters in base name."""
        filename = get_timestamped_filename("my-file_name.backup")
        
        # Should match pattern: my-file_name.backup_YYYYMMDD_HHMMSS.csv
        pattern = r"my-file_name\.backup_\d{8}_\d{6}\.csv"
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_timestamp_format_consistency(self) -> None:
        """Test that timestamp format is consistent across multiple calls."""
        import time
        
        # Generate multiple filenames in quick succession
        filenames = []
        for _ in range(3):
            filenames.append(get_timestamped_filename("test"))
            time.sleep(0.1)  # Small delay to potentially get different timestamps
        
        # All should have the same base pattern
        for filename in filenames:
            pattern = r"test_\d{8}_\d{6}\.csv"
            assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"
        
        # Extract timestamps and verify they're in chronological order
        timestamps = []
        for filename in filenames:
            timestamp_part = filename.replace("test_", "").replace(".csv", "")
            timestamps.append(timestamp_part)
        
        # Timestamps should be in non-decreasing order (same or increasing)
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i-1], f"Timestamps not in order: {timestamps}"