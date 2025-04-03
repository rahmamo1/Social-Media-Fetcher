import requests
import threading
import instaloader
import tkinter as tk
from tkinter import ttk, messagebox
from playwright.sync_api import sync_playwright
from PIL import Image, ImageTk
from io import BytesIO
import time
from threading import Thread

results = {}
results_lock = threading.Lock()


class FacebookFetcher:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

    def get_basic_info(self, user_id):
        context = self.browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the profile page
            page.goto(f"{user_id}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)  # Additional time for page load

            profile_info = {"ID": user_id}

            # Get the name
            name_element = page.query_selector("h1")
            profile_info["Name"] = name_element.inner_text() if name_element else "N/A"
            # Get the profile picture URL
            profile_picture_element = page.query_selector(
                "div.x15sbx0n:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > "
                "svg:nth-child(1) > g:nth-child(2) > image:nth-child(1)"
            )
            profile_info["Profile Picture"] = profile_picture_element.get_attribute(
                "xlink:href") if profile_picture_element else "N/A"

            return profile_info

        except Exception as e:
            return {"error": str(e)}
        finally:
            context.close()

    def close(self):
        self.browser.close()
        self.playwright.stop()


class TwitterFetcher:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)  # Headless browser

    def get_tweets(self, username, count=5):
        context = self.browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the Twitter profile page
            page.goto(f"https://twitter.com/{username}")

            # Wait for tweets to load
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)  # Extra time for full content to load

            # Initialize the list to store tweets
            tweets = []

            # Get profile picture URL
            profile_picture_element = page.query_selector("img[src*='profile_images']")
            profile_picture_url = profile_picture_element.get_attribute("src") if profile_picture_element else "N/A"

            # Get the username display name
            user_name_element = page.query_selector("div[data-testid='UserName'] span")
            user_name = user_name_element.inner_text() if user_name_element else "N/A"

            # Get tweets
            tweet_elements = page.query_selector_all("article div[lang]")
            created_at_elements = page.query_selector_all("article time")
            image_elements = page.query_selector_all("article img[src]")

            # Extract tweets and associated data
            for i, tweet_element in enumerate(tweet_elements[:count]):
                text = tweet_element.inner_text()

                # Extract images (if available)
                image_url = image_elements[i].get_attribute("src") if i < len(image_elements) else "N/A"

                # Extract tweet creation time
                created_at = created_at_elements[i].get_attribute("datetime") if i < len(created_at_elements) else "N/A"

                # Append the tweet data to the list
                tweets.append({
                    "user_name": user_name,
                    "text": text,
                    "image": image_url,
                    "created_at": created_at,
                    "profile_picture": profile_picture_url
                })

            return tweets

        except Exception as e:
            return [{"error": f"Failed to fetch data: {e}"}]

        finally:
            # Clean up the context and browser
            context.close()

    def close(self):
        """Closes the browser and stops Playwright."""
        self.browser.close()
        self.playwright.stop()


class InstagramFetcher:
    def __init__(self):
        self.loader = instaloader.Instaloader()

    def get_basic_info(self, username):
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            return {
                "Username": profile.username,
                "Full Name": profile.full_name,
                "Bio": profile.biography,
                "Followers Count": profile.followers,
                "Following Count": profile.followees,
                "Posts Count": profile.mediacount,
                "Profile Picture": profile.profile_pic_url,
            }
        except Exception as e:
            return {"error": str(e)}


def display_twitter_profile_image(profile_picture_url, image_label):
    if profile_picture_url and profile_picture_url != "N/A":
        try:
            # Download the image from the URL
            img_data = requests.get(profile_picture_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((100, 100))  # Resize to fit the interface
            img_tk = ImageTk.PhotoImage(img)

            # Update image_label to display the image
            image_label.config(image=img_tk)
            image_label.image = img_tk  # Keep the reference to avoid garbage collection
        except Exception as e:
            image_label.config(text=f"Error loading image: {e}")
            image_label.image = None
    else:
        image_label.config(text="No image available")


def display_facebook_profile_image(profile_picture_url, image_label):
    if profile_picture_url and profile_picture_url != "N/A":
        try:
            # Download the image from the URL
            img_data = requests.get(profile_picture_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((100, 100))  # Resize to fit the interface
            img_tk = ImageTk.PhotoImage(img)

            # Update image_label to display the image
            image_label.config(image=img_tk)
            image_label.image = img_tk  # Keep the reference to avoid garbage collection
        except Exception as e:
            image_label.config(text=f"Error loading image: {e}")
            image_label.image = None
    else:
        image_label.config(text="No image available")


def display_instagram_profile_image(profile_picture_url, image_label):
    if profile_picture_url and profile_picture_url != "N/A":
        try:
            # Download the image from the URL
            img_data = requests.get(profile_picture_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((100, 100))  # Resize to fit the interface
            img_tk = ImageTk.PhotoImage(img)

            # Update image_label to display the image
            image_label.config(image=img_tk)
            image_label.image = img_tk  # Keep the reference to avoid garbage collection
        except Exception as e:
            image_label.config(text=f"Error loading image: {e}")
            image_label.image = None
    else:
        image_label.config(text="No image available")


def fetch_data_from_platform(platform_name, user_input, result_label, image_label):
    start_time = time.time()  # Capture the start time
    global results
    try:
        if platform_name == "Facebook":
            fetcher = FacebookFetcher()
            user_id = user_input.get("facebook_user_id", "")
            data = fetcher.get_basic_info(user_id)
            fetcher.close()
            # When retrieving Facebook data, show the profile picture
            profile_picture_url = data.get("Profile Picture", "N/A")
            display_facebook_profile_image(profile_picture_url, image_label)

        elif platform_name == "Instagram":
            fetcher = InstagramFetcher()
            username = user_input.get("instagram_username", "")
            data = fetcher.get_basic_info(username)
            profile_picture_url = data.get("Profile Picture", "N/A")
            display_instagram_profile_image(profile_picture_url, image_label)

        elif platform_name == "Twitter":
            fetcher = TwitterFetcher()
            username = user_input.get("twitter_username", "")
            data = fetcher.get_tweets(username)
            fetcher.close()
            # When retrieving Twitter data, pass the profile picture URL to the function
            if data and isinstance(data, list):
                profile_picture_url = data[0].get("profile_picture", "N/A")  # Retrieve the profile picture URL
                display_twitter_profile_image(profile_picture_url, image_label)  # Display the image
            else:
                data = {"error": "Unknown Platform"}
        else:
            data = {"error": "Unknown Platform"}

        end_time = time.time()  # Capture the end time
        elapsed_time = round(end_time - start_time, 2)  # Calculate elapsed time

        # Format the result text with the performance time
        if platform_name == "Twitter" and isinstance(data, list):
            for tweet in data:
                tweet["Performance"] = f"Time Taken: {elapsed_time} seconds"
            result_text = "\n\n".join(
                [f"Tweet {i + 1}:\n" + "\n".join([f"{k}: {v}" for k, v in tweet.items()]) for i, tweet in
                 enumerate(data)]
            )
        else:
            data["Performance"] = f"Time Taken: {elapsed_time} seconds"
            result_text = "\n".join([f"{k}: {v}" for k, v in data.items()])

            # Handle displaying the profile image
            image_url = data.get("Profile Picture") or None
            if image_url:
                try:
                    # Download the image using requests
                    img_data = requests.get(image_url).content
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((100, 100))  # Resize to fit the interface
                    img_tk = ImageTk.PhotoImage(img)

                    # Update image_label to display the image
                    image_label.config(image=img_tk)
                    image_label.image = img_tk  # Keep the reference to avoid garbage collection
                except Exception as e:
                    image_label.config(text=f"Error loading image: {e}")
                    image_label.image = None
            else:
                image_label.config(text="No image available")

        # Update the result interface with the retrieved data
        with results_lock:
            results[platform_name] = data
        result_label.config(text=result_text)

    except Exception as e:
        with results_lock:
            results[platform_name] = {"error": str(e)}
        result_label.config(text=f"Error fetching data: {e}")
        print(f"Error fetching {platform_name} data: {e}")


# Open a window for each thread with input fields and results display
def open_thread_windows():
    try:
        num_threads = int(thread_count_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number")
        return

    def create_fetch_window(thread_index):
        # Create a new window
        window = tk.Toplevel(root)
        window.title(f"Thread {thread_index + 1}")
        window.geometry("400x500")

        # Frame for Canvas and Scrollbar
        container = tk.Frame(window)
        container.pack(fill="both", expand=True)

        # Canvas for adding content
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar for the canvas
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Internal content frame
        content_frame = tk.Frame(canvas)

        # Link the content frame to the canvas
        canvas.create_window((0, 0), window=content_frame, anchor="n")  # Anchor to keep the content aligned

        # Add scroll region
        def on_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", on_configure)

        # Align content to center
        center_frame = tk.Frame(content_frame)
        center_frame.pack(pady=20, padx=100, anchor="center", fill="both", expand=True)

        # Main title label
        tk.Label(
            center_frame,
            text=f"Thread {thread_index + 1}",
            font=("Arial", 18, "bold"),
            anchor="center",
        ).grid(row=0, pady=10, padx=0)

        # Platform selection label
        tk.Label(
            center_frame,
            text="Select Platform:",
            font=("Arial", 14),
            anchor="center",
        ).grid(row=1, pady=5)

        platform_var = ttk.Combobox(
            center_frame,
            values=["Facebook", "Instagram", "Twitter"],
            state="readonly",
            font=("Arial", 12)
        )
        platform_var.grid(row=2, pady=10, padx=5)
        platform_var.set("Facebook")

        # Username/ID input label
        tk.Label(
            center_frame,
            text="Enter Username/ID:",
            font=("Arial", 14),
            anchor="center",
        ).grid(row=3, pady=5)

        username_entry = tk.Entry(center_frame, font=("Arial", 12), justify="center")
        username_entry.grid(row=4, pady=10)

        # Results label
        result_label = tk.Label(
            center_frame,
            text="Results will appear here",
            wraplength=350,
            anchor="center",
            font=("Arial", 12),
        )
        result_label.grid(row=5, pady=10)

        # Image label
        image_label = tk.Label(
            center_frame,
            text="Profile image will appear here",
            font=("Arial", 12),
            anchor="center",
        )
        image_label.grid(row=6, pady=10)

        # Fetch Data button
        fetch_button = tk.Button(
            center_frame,
            text="Fetch Data",
            font=("Arial", 12, "bold"),
            command=lambda: Thread(
                target=fetch_data_from_platform,
                args=(
                    platform_var.get(),
                    {
                        "facebook_user_id": username_entry.get(),
                        "instagram_username": username_entry.get(),
                        "twitter_username": username_entry.get(),
                    },
                    result_label,
                    image_label,
                ),
            ).start(),
        )
        fetch_button.grid(row=7, pady=15)

    # Create the specified number of threads
    for i in range(num_threads):
        create_fetch_window(i)

    # Main window to input number of threads


root = tk.Tk()
root.title("Social Media Fetcher")
root.geometry("400x300")

tk.Label(root, text="Enter Number of Threads:", font=("Arial", 12)).pack(pady=10)
thread_count_entry = tk.Entry(root, font=("Arial", 12))
thread_count_entry.pack(pady=5)

open_windows_button = tk.Button(root, text="Open Threads", font=("Arial", 12, "bold"), command=open_thread_windows)
open_windows_button.pack(pady=20)

root.mainloop()
