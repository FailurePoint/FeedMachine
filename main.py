import json
import logging
import rss

logging.basicConfig(filename='feed_curation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_rss_feed(url, prompt, save_dir, use_selenium):
    try:
        logging.info(f"Started processing URL: {url} (Selenium: {use_selenium})")
        html_content = rss.fetch_full_page_html(url, use_selenium=use_selenium)

        if html_content:
            logging.info(f"Web page content fetched successfully for: {url}")
            response = rss.query_openrouter(prompt, html_content)
            logging.info(f"XML content created and evaluated successfully for: {url}")

            rss.update_xml(response, file_path=save_dir)
            logging.info(f"RSS feed created and saved to: {save_dir}")
        else:
            logging.error(f"Error: Could not retrieve the web page content for {url}")
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")

def main():
    # Load the JSON file containing URLs, prompts, save directories, and Selenium usage
    try:
        with open('sites.json', 'r') as f:
            sites_config = json.load(f)
        logging.info("Loaded sites configuration file successfully.")
    except Exception as e:
        logging.error(f"Error loading sites configuration file: {e}")
        return

    # Process each site in the JSON file
    for site in sites_config:
        url = site.get('url')
        prompt = site.get('prompt')
        save_dir = site.get('save_directory')
        use_selenium = site.get('use_selenium', False)  # Default to False if not provided

        if not url or not prompt or not save_dir:
            logging.warning(f"Skipping incomplete site configuration: {site}")
            continue
        
        process_rss_feed(url, prompt, save_dir, use_selenium)

if __name__ == "__main__":
    main()

