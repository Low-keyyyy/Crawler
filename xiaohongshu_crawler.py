from DrissionPage import ChromiumOptions, Chromium
from DrissionPage.common import Settings
from datetime import datetime, timedelta
from tqdm import tqdm
from urllib.parse import quote
import time
import random
import pandas as pd
import re


class XiaohongshuScraper:
    '''
        A class for scraping Xiaohongshu using browser.
        Class Variables:
            CONFIG: configuration for the browser
            LOG_ALLOWED: whether to allow logging
            LIKE_LIMIT: whether to limit the number of likes
            MINIMUM_LIKES: minimum number of likes
        Attributes:
            page: current page
            contents: list of contents
            comments: list of comments
        methods:
            crawl: main crawling function
            sign_in: Login to Xiaohongshu using browser
            search: Search for notes based on keyword
            get_info: Extract information from current page
            get_note_detail: Get note detail and comments
            get_comments: Get comments from container
            page_scroll_down: Scroll page down with random delay
            save_to_excel: Save scraped data to Excel
    '''
    CONFIG = {
        'browser_path': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'headless': False, # It is recommended to set to False because there may be some captchas during scraping.
        'language': 'en',
        'load_mode': 'normal',
    }
    LOG_ALLOWED = False
    LIKE_LIMIT = True
    MINIMUM_LIKES = 50
    COMMENT_LOCK = True

    def __init__(self):
        self.page = None
        self.contents = []
        self.comments = []

        Settings.set_language(XiaohongshuScraper.CONFIG['language'])
        self.options = ChromiumOptions()
        self.options.set_browser_path(XiaohongshuScraper.CONFIG['browser_path'])
        self.options.set_load_mode(XiaohongshuScraper.CONFIG['load_mode'])
        self.options.headless(XiaohongshuScraper.CONFIG['headless'])
        self.browser = Chromium(addr_or_opts=self.options)
        

    def sign_in(self):
        """Login to Xiaohongshu using Edge"""
        self.page = self.browser.new_tab(url='https://www.xiaohongshu.com')
        print("Please scan QR code to login")
        # Wait for QR code scan, please log in within 60 seconds
        time.sleep(60)

    def search(self, keyword):
        """Search for notes based on keyword"""
        if not self.page:
            self.page = self.browser.new_tab(url='https://www.xiaohongshu.com')

        # Convert keyword to URL encoding (double encode with utf-8 and gb2312)
        keyword_encode = quote(quote(keyword.encode('utf-8')).encode('gb2312'))

        # Open search results page
        self.page.get(
            f'https://www.xiaohongshu.com/search_result?keyword={keyword_encode}&source=web_search_result_notes'
        )
        time.sleep(5)  # Wait for page load

    def get_info(self):
        """Extract information from current page"""
        page_start_time = time.time()
        try:
            container = self.page.ele('.feeds-page')
            sections = container.eles('.note-item')

            for section in tqdm(sections,
                                desc='Now scraping current page',
                                ascii=False,
                                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
                try:
                    # Get note link
                    note_link = section.ele('tag:div', timeout=0).eles('tag:a', timeout=0)[1]

                    # Get footer info
                    footer = section.ele('.footer', timeout=0)

                    # Get title
                    title = footer.ele('.title', timeout=0).text

                    # Get author info
                    author_wrapper = footer.ele('.author-wrapper')
                    author = author_wrapper.ele('.author').text

                    # Get likes
                    like_text = footer.ele('.like-wrapper like-active').text
                    like = re.search(r'\d+', like_text).group(0)
                    if not like:
                        like = "0"

                    # Like limit check
                    if XiaohongshuScraper.LIKE_LIMIT and int(like) < XiaohongshuScraper.MINIMUM_LIKES:
                        continue
                    
                    # Get note detail
                    text, comments, date = self.get_note_detail(note_link)
                        
                    # Add to contents list & comments list
                    self.contents.append([title, date, author, like, text])
                    print(f"\nNumber of notes scraped: {len(self.contents)}\n")
                    if not XiaohongshuScraper.COMMENT_LOCK:
                        self.comments.extend(comments)
                except Exception as e:
                    if XiaohongshuScraper.LOG_ALLOWED:
                        print(f"Error extracting note info: {e}")
                    continue

            # Calculate and display the time taken for the current page
            page_time = time.time() - page_start_time
            print(f"\nCurrent page scraping completed, time taken: {page_time:.2f} seconds\n")

        except Exception as e:
            if XiaohongshuScraper.LOG_ALLOWED:
                print(f"Error getting page info: {e}")

    def get_note_detail(self, note_link):
        """Get note detail and comments"""
        try:
            text = ""
            comments = []

            # Open the note detail page
            note_link.click()
            time.sleep(3)  # Wait for page load

            # Get container and close button
            container = self.page.ele('.note-container', timeout=0)
            close_button = self.page.ele('.close-circle', timeout=0)
            
            # Get content
            content = container.ele('.note-text', timeout=0).eles('tag:span', timeout=0)
            for piece in content:
                text += piece.text.strip()

            # Get date
            date_description = container.ele('.bottom-container', timeout=0).ele('.date', timeout=0).text
            date = self.date_analysis(date_description)
            
            # Get comments
            if not XiaohongshuScraper.COMMENT_LOCK:
                comments_container = container.ele('.comments-container', timeout=0)
                comments = self.get_comments(comments_container)

            # Close the note detail page
            close_button.click()
            time.sleep(3)
            return (text, comments, date)

        except Exception as e:
            if XiaohongshuScraper.LOG_ALLOWED:
                print(f"Error getting note detail: {e}")
            close_button.click()
            time.sleep(3)
        return None

    def get_comments(self, container):
        """Get comments from container"""
        comments = []
        try:
            parent_comments = container.eles('.parent-comment')
            for parent_comment in tqdm(parent_comments,
                                        desc='Now scraping comments',
                                        ascii=False,
                                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
                comment = parent_comment.ele('.content', timeout=0).ele('.note-text', timeout=0).text
                comments.append(comment)
            return comments
        except Exception as e:
            if XiaohongshuScraper.LOG_ALLOWED:
                print(f"Error getting comments: {e}")
        return None

    def page_scroll_down(self):
        """Scroll page down with random delay"""
        print("********Scrolling down********")
        random_time = random.uniform(0.5, 1.5)
        time.sleep(random_time)
        self.page.scroll.to_bottom()

    def crawl(self, times=20):
        """Main crawling function"""
        start_time = time.time()
        for i in tqdm(range(1, times + 1),
                      desc='Scraping Xiaohongshu',
                      ascii=False,
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
            self.get_info()
            self.page_scroll_down()
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time:.2f} seconds")

    def date_analysis(self, date_description):
        """Analyze date description"""
        date = ""
        now = datetime.now().date()
        if "今天" in date_description:
            date = now.strftime("%Y-%m-%d")
        elif "昨天" in date_description:
            date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif re.search(r'\d+ 天前', date_description):
            days = re.search(r'\d+', date_description).group(0)
            date = (now - timedelta(days=int(days))).strftime("%Y-%m-%d")
        elif re.search(r'\d{4}-\d{2}-\d{2}', date_description):
            date = re.search(r'\d{4}-\d{2}-\d{2}', date_description).group(0)
        elif re.search(r'\d{1}-\d{2}', date_description):
            date = str(now.year) + "-0" + re.search(r'\d{1}-\d{2}', date_description).group(0)
        else:
            print(date_description)
            date = re.search(r'\d{2}-\d{2}', date_description).group(0)
            date = str(now.year) + "-" + date
        return date

    def save_to_excel(self, keyword):
        """Save scraped data to Excel"""
        # Create DataFrame
        columns = [
            'title', 'date', 'author', 'like', 'text'
        ]
        df = pd.DataFrame(self.contents, columns=columns)

        # Convert likes to integer and sort
        df['like'] = pd.to_numeric(df['like'],
                                   errors='coerce').fillna(0).astype(int)
        df = df.drop_duplicates()
        df = df.sort_values(by='like', ascending=False)

        # Save to Excel
        excel_path = f'xiaohongshu_{keyword}.xlsx'
        df.to_excel(excel_path, index=False)

        # Save comments to Excel
        if not XiaohongshuScraper.COMMENT_LOCK:
            comments_df = pd.DataFrame(self.comments, columns=['comments'])
            comments_df.to_excel(f'xiaohongshu_{keyword}_comments.xlsx', index=False)


def main():
    # Initialize scraper
    scraper = XiaohongshuScraper()

    # Login (uncomment for first time use)
    # scraper.sign_in()

    # Set keyword and start scraping
    keyword = input("Enter search keyword: ")
    scraper.search(keyword)
    scraper.crawl(times=50)
    scraper.save_to_excel(keyword)


if __name__ == "__main__":
    main()
