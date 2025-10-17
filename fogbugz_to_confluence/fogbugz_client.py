import requests
import os
from xml.etree import ElementTree

class FogBugzClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None

    def _get_token(self):
        if not self.token:
            api_url = f"{self.base_url}/api.asp"
            params = {
                'cmd': 'logon',
                'email': self.email,
                'password': self.password
            }
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            tree = ElementTree.fromstring(response.content)
            self.token = tree.find('token').text
        return self.token

    def get_wiki_pages(self):
        token = self._get_token()
        api_url = f"{self.base_url}/api.asp"
        params = {
            'cmd': 'listWikis',
            'token': token
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        pages = []
        for wiki in tree.findall('.//wiki'):
            page_id = wiki.find('ixWiki').text
            title = wiki.find('sTitle').text
            parent_id = wiki.find('ixWikiParent').text
            pages.append({'id': page_id, 'title': title, 'parent_id': parent_id})
        return pages

    def get_wiki_page_content(self, page_id):
        token = self._get_token()
        api_url = f"{self.base_url}/api.asp"
        params = {
            'cmd': 'viewArticle',
            'token': token,
            'ixWikiPage': page_id
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        content = tree.find('.//article/sHTML').text
        return content

    def download_attachment(self, attachment_url, download_path):
        token = self._get_token()
        # The attachment URL is relative, so we need to construct the full URL
        full_url = f"{self.base_url}/{attachment_url}&token={token}"
        response = requests.get(full_url, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return download_path