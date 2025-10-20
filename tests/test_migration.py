import unittest
from unittest.mock import patch, MagicMock
from fogbugz_to_confluence.migrate import migrate
from fogbugz_to_confluence.fogbugz_client import FogBugzClient
from fogbugz_to_confluence.confluence_client import ConfluenceClient

class TestMigration(unittest.TestCase):

    @patch('fogbugz_to_confluence.migrate.FogBugzClient')
    @patch('fogbugz_to_confluence.migrate.ConfluenceClient')
    def test_migration_logic(self, mock_confluence_client, mock_fogbugz_client):
        # --- Mock Configuration ---
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key: {
            ('fogbugz', 'base_url'): 'http://fake-fogbugz.com',
            ('fogbugz', 'token'): 'fb_token',
            ('confluence', 'base_url'): 'http://fake-confluence.com',
            ('confluence', 'api_token'): 'token',
            ('confluence', 'space_key'): 'TEST',
            ('migration', 'download_dir'): 'test_downloads'
        }.get((section, key))

        # --- Mock FogBugz API ---
        mock_fb_instance = mock_fogbugz_client.return_value
        mock_fb_instance.list_wikis.return_value = [{'id': '1', 'title': 'Test Wiki'}]
        mock_fb_instance.list_articles.return_value = [{'id': '1'}, {'id': '2'}]
        mock_fb_instance.view_article.side_effect = [
            {'id': '1', 'title': 'Page 1', 'content': '<html><body><p>Page 1 content</p><a href="default.asp?W2">Link to Page 2</a></body></html>', 'parent_id': '0'},
            {'id': '2', 'title': 'Page 2', 'content': '<html><body><p>Page 2 content</p><img src="default.asp?pg=pgDownload&pgType=pgWikiAttachment&ixAttachment=11&sFileName=test.png"></body></html>', 'parent_id': '1'}
        ]

        # --- Mock Confluence API ---
        mock_conf_instance = mock_confluence_client.return_value
        mock_conf_instance.create_page.side_effect = [
            {'id': '101', 'version': {'number': 1}},
            {'id': '102', 'version': {'number': 1}}
        ]
        mock_conf_instance.get_page.side_effect = [
            {'id': '101', 'version': {'number': 1}},
            {'id': '102', 'version': {'number': 1}}
        ]

        # --- Run Migration ---
        migrate(mock_config)

        # --- Assertions ---
        # Assert that the clients were initialized correctly
        mock_fogbugz_client.assert_called_with('http://fake-fogbugz.com', 'fb_token')
        mock_confluence_client.assert_called_with('http://fake-confluence.com', 'token')

        # Assert that pages were created
        self.assertEqual(mock_conf_instance.create_page.call_count, 2)

        # Assert that pages were updated
        self.assertEqual(mock_conf_instance.update_page.call_count, 2)

        # Assert that attachments were downloaded and uploaded
        mock_fb_instance.download_attachment.assert_called_once()
        mock_conf_instance.upload_attachment.assert_called_once()


if __name__ == '__main__':
    unittest.main()