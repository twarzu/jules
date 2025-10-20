import requests
import json

class ConfluenceClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }

    def _post(self, endpoint, data):
        url = f"{self.base_url}/rest/api/{endpoint}"
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def _put(self, endpoint, data):
        url = f"{self.base_url}/rest/api/{endpoint}"
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def _post_multipart(self, endpoint, files):
        url = f"{self.base_url}/rest/api/{endpoint}"
        headers = {
            "X-Atlassian-Token": "nocheck",
            "Authorization": self.headers['Authorization']
        }
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()

    def create_page(self, space_key, title, content, parent_id=None):
        endpoint = "content"
        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        if parent_id:
            data["ancestors"] = [{"id": parent_id}]

        return self._post(endpoint, data)

    def upload_attachment(self, page_id, file_path, comment=""):
        endpoint = f"content/{page_id}/child/attachment"
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path, f),
                'comment': (None, comment)
            }
            return self._post_multipart(endpoint, files)

    def get_page(self, page_id):
        endpoint = f"content/{page_id}"
        url = f"{self.base_url}/rest/api/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_page(self, page_id, title, content, version):
        endpoint = f"content/{page_id}"
        data = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        return self._put(endpoint, data)