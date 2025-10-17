import requests
import os
from xml.etree import ElementTree

class FogBugzClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def list_wikis(self):
        api_url = f"{self.base_url}/api.asp"
        params = {
            'cmd': 'listWikis',
            'token': self.token
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        wikis = []
        for wiki in tree.findall('.//wiki'):
            wiki_id = wiki.find('ixWiki').text
            title = wiki.find('sTitle').text
            wikis.append({'id': wiki_id, 'title': title})
        return wikis

    def list_articles(self, wiki_id):
        api_url = f"{self.base_url}/api.asp"
        params = {
            'cmd': 'listArticles',
            'token': self.token,
            'ixWiki': wiki_id
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        articles = []
        for article in tree.findall('.//article'):
            page_id = article.find('ixWikiPage').text
            articles.append({'id': page_id})
        return articles

    def view_article(self, page_id):
        api_url = f"{self.base_url}/api.asp"
        params = {
            'cmd': 'viewArticle',
            'token': self.token,
            'ixWikiPage': page_id
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        tree = ElementTree.fromstring(response.content)
        article = tree.find('.//article')
        title = article.find('sHeadline').text
        content = article.find('sHTML').text
        parent_id = article.find('ixWikiPageParent').text
        return {'id': page_id, 'title': title, 'content': content, 'parent_id': parent_id}

    def download_attachment(self, attachment_url, download_path):
        # The attachment URL is relative, so we need to construct the full URL
        full_url = f"{self.base_url}/{attachment_url}&token={self.token}"
        response = requests.get(full_url, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return download_path