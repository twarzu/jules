# FogBugz to Confluence Migration Script

This script migrates a FogBugz Wiki to Atlassian Confluence. It uses the FogBugz XML API and the Confluence REST API to perform the migration.

## Features

- Migrates all wiki pages
- Preserves the hierarchy of the pages
- Migrates all attachments and images
- Rewrites internal links to point to the new Confluence pages
- Rewrites attachment and image links to point to the new Confluence attachments

## Prerequisites

- Python 3.6+
- Access to a FogBugz instance with API access enabled
- Access to a Confluence instance with API access enabled

## Installation

1.  Clone this repository:
    ```
    git clone <repository-url>
    ```
2.  Create a virtual environment:
    ```
    python3 -m venv venv
    ```
3.  Activate the virtual environment:
    ```
    source venv/bin/activate
    ```
4.  Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Configuration

1.  Rename the `config.ini.example` file to `config.ini`:
    ```
    mv config.ini.example config.ini
    ```
2.  Open the `config.ini` file and fill in the required values:
    - `[fogbugz]`
        - `base_url`: The base URL of your FogBugz instance (e.g., `https://your-company.fogbugz.com`)
        - `token`: The API token of the user with API access
    - `[confluence]`
        - `base_url`: The base URL of your Confluence instance (e.g., `https://your-company.atlassian.net/wiki`)
        - `username`: The username of the user with API access
        - `api_token`: The API token of the user with API access
        - `space_key`: The key of the Confluence space where the pages will be migrated
    - `[migration]`
        - `download_dir`: The directory where the attachments will be downloaded

## Usage

To run the migration, execute the `migrate.py` script:
```
python fogbugz_to_confluence/migrate.py
```

## Testing

To run the tests, execute the following command:
```
python -m unittest discover tests
```