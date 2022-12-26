from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    def test_wait_for_database_ready(self):
        """Test that the command waits for the database to be ready"""

        with patch("django.db.utils.ConnectionHandler.__getitem__") as mock:
            mock.return_value = True
            call_command("wait_for_database")
            self.assertEqual(mock.call_count, 1)

    @patch("time.sleep", return_value=True)
    def test_wait_for_database(self, ts):
        """Test wating for database"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as mock:
            mock.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_database")
            self.assertEqual(mock.call_count, 6)
