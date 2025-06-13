# 📱 Social Media Fetcher
Social Media Fetcher is a Python-based GUI application that allows users to fetch profile information, profile pictures, and recent posts from Facebook, Instagram, and Twitter using web scraping and API techniques. It supports multi-threaded data collection with a user-friendly interface.
## 🚀 Features
•	Fetch profile information and pictures from:

      o	📘 Facebook
      
      o	📸 Instagram
      
      o	🐦 Twitter

•	Extract recent tweets and metadata

•	Multi-threaded support: open multiple fetcher windows concurrently

•	GUI built with Tkinter for easy interaction

•	Automatic display of profile pictures

•	Performance timing for each fetch operation

•	Scrollable, responsive layout per thread

## 🛠️ Tech Stack
| Feature        | Libraries/Tools Used                    |
| -------------- | --------------------------------------- |
| Web Scraping   | `playwright`, `instaloader`, `requests` |
| GUI            | `tkinter`, `PIL` (`Pillow`)             |
| Multithreading | `threading`                             |
| Image Handling | `PIL`, `BytesIO`                        |
## 💡 How It Works
•	For Facebook and Twitter, it uses Playwright to open headless Chromium browsers and scrape visible elements.

•	For Instagram, it uses Instaloader to fetch data from public profiles.

•	Each platform's data fetching logic is encapsulated in separate classes (FacebookFetcher, TwitterFetcher, InstagramFetcher).

•	The app opens a new thread window for each data-fetching task, ensuring smooth and non-blocking performance.
## 📂 Outputs
•	Textual results are displayed in a scrollable label.

•	Profile pictures are rendered inside the GUI per platform.

•	Each fetch operation reports its performance time.

