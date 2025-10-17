import os
import re
import logging
import configparser
from bs4 import BeautifulSoup
from fogbugz_to_confluence.fogbugz_client import FogBugzClient
from fogbugz_to_confluence.confluence_client import ConfluenceClient

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Migration Logic ---
def migrate(config):
    # Initialize clients
    fb_client = FogBugzClient(
        config.get('fogbugz', 'base_url'),
        config.get('fogbugz', 'token')
    )
    conf_client = ConfluenceClient(
        config.get('confluence', 'base_url'),
        config.get('confluence', 'username'),
        config.get('confluence', 'api_token')
    )

    # Get all wikis from FogBugz
    logging.info("Fetching wikis from FogBugz...")
    wikis = fb_client.list_wikis()
    logging.info(f"Found {len(wikis)} wikis to migrate.")

    for wiki in wikis:
        logging.info(f"Migrating wiki: {wiki['title']}")
        # Get all wiki pages from FogBugz
        logging.info("Fetching articles from FogBugz...")
        articles = fb_client.list_articles(wiki['id'])
        logging.info(f"Found {len(articles)} articles to migrate.")

        # A map to store the mapping between FogBugz page IDs and Confluence page IDs
        page_id_map = {}

        # A list to store the page details
        fb_pages = []

        # Get all page details first to build the hierarchy
        for article in articles:
            try:
                logging.info(f"Fetching details for article: {article['id']}")
                page_details = fb_client.view_article(article['id'])
                fb_pages.append(page_details)
            except Exception as e:
                logging.error(f"Error fetching details for article {article['id']}: {e}")

        # Create pages in Confluence
        for page in fb_pages:
            try:
                # Create the page in Confluence
                parent_id = page_id_map.get(page['parent_id'])
                logging.info(f"Creating page: {page['title']}")
                new_page = conf_client.create_page(config.get('confluence', 'space_key'), page['title'], page['content'], parent_id)
                page_id_map[page['id']] = new_page['id']
                logging.info(f"Created page: {page['title']} -> {new_page['id']}")
            except Exception as e:
                logging.error(f"Error creating page {page['title']}: {e}")


        # Update pages with attachments and corrected links
        for page in fb_pages:
            try:
                confluence_page_id = page_id_map.get(page['id'])
                if not confluence_page_id:
                    continue

                logging.info(f"Updating page: {page['title']}")
                soup = BeautifulSoup(page['content'], 'html.parser')

                # Handle attachments and images
                for tag in soup.find_all(['a', 'img']):
                    url_attr = 'href' if tag.name == 'a' else 'src'
                    if url_attr in tag.attrs:
                        url = tag[url_attr]
                        if "pg=pgDownload" in url:
                            # This is an attachment/image
                            try:
                                file_name = url.split("sFileName=")[-1]
                                download_path = os.path.join(config.get('migration', 'download_dir'), file_name)
                                logging.info(f"Downloading attachment: {file_name}")
                                fb_client.download_attachment(url, download_path)
                                logging.info(f"Uploading attachment: {file_name}")
                                conf_client.upload_attachment(confluence_page_id, download_path)

                                # Update the link to point to the Confluence attachment
                                new_url = f"/wiki/download/attachments/{confluence_page_id}/{file_name}"
                                tag[url_attr] = new_url
                            except Exception as e:
                                logging.error(f"Error handling attachment {url}: {e}")

                # Handle internal links
                for link in soup.find_all('a', href=re.compile(r"default.asp\?W(\d+)")):
                        fb_page_id_match = re.search(r"W(\d+)", link['href'])
                        if fb_page_id_match:
                            fb_page_id = fb_page_id_match.group(1)
                            if fb_page_id in page_id_map:
                                conf_page_id_to_link = page_id_map[fb_page_id]
                                space_key = config.get('confluence', 'space_key')
                                link['href'] = f"/wiki/spaces/{space_key}/pages/{conf_page_id_to_link}"


                # Update the page content
                updated_content = str(soup)
                # We need the current version of the page to update it
                # For now, let's assume version 1, but a better approach is to get it from the created page
                new_page_details = conf_client.get_page(confluence_page_id)
                current_version = new_page_details['version']['number']
                logging.info(f"Updating content for page: {page['title']}")
                conf_client.update_page(confluence_page_id, page['title'], updated_content, current_version)
                logging.info(f"Updated page: {page['title']}")
            except Exception as e:
                logging.error(f"Error updating page {page['title']}: {e}")

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    DOWNLOAD_DIR = config.get('migration', 'download_dir')
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    migrate(config)