# Crawler for Xiaohongshu(Rednote)

This crawler program is specifically designed for **the web version of Xiaohongshu (Rednote)**. It can crawl the content on Xiaohongshu according to **designated keywords**. You can quickly deploy and use it locally by following the steps below.

## Quick Start

1. **Clone the Repository**  
   Clone this repository to your local machine:

   ```
   git clone https://github.com/Low-keyyyy/Crawler.git
   ```

2. **Install Dependencies**  
   Install the required dependencies using the `requirements.txt` file:

   ```
   pip install -r requirements.txt
   ```

3. **Set Browser Path**  
   Update the `browser_path` variable in the script to the path of your local browser executable (e.g., Chrome or Edge).

4. **Adjust Configuration**  
   Modify the configuration settings in the script according to your needs.

5. **Run the Program**  
   Execute the crawler by running the main script:

   ```
   python xiaohongshu_crawler.py
   ```

6. **Enter the Keyword**

   You can enter the keyword of the content you want to crawl in the terminal. The the script will start crawling automatically.

## Tips

- **First-Time Setup**: If this is your first time running the program, you’ll need to log in to Xiaohongshu via a QR code scan on the web version. Uncomment the login section in the `main` function to enable this step.  
- **Subsequent Runs**: After the initial login, the crawler can run without requiring a QR code scan again.

---

