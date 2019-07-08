import requests
import bs4
import sys
import threading
import queue
import os


class Wallhaven:
    def __init__(self, res=(1920, 1080), ratio=(16,9)):
        self.base_link = "https://wallhaven.cc/search?"
        # Search terms
        self.resolution = res
        self.ratio = ratio
        self.grabbing = False
        self.query = ""

        self.page_queue = queue.Queue()
        self.image_queue = queue.Queue()
        self.search_queue = queue.Queue()
        self.urls = []

    def search(self, query, pages, threads=1):
        self.query = query
        # Add page numbers to queue
        for page in range(1, pages+1):
            self.search_queue.put(page)

        # Create threads and add them to a list
        search_threads = []        
        for i in range(threads):
            thread = threading.Thread(target=self.download_page)
            thread.start()
            search_threads.append(thread)

        # Wait for threads to finish
        for thread in search_threads:
            thread.join()

        # Return urls
        return self.urls


    def download_page(self):
        while True:
            try:
                page_number = self.search_queue.get(block=False)
            except queue.Empty:
                return

            payload = {
                "q": self.query,
                "page": str(page_number),
                "resolutions": f"{self.resolution[0]}x{self.resolution[1]}",
                "categories": "101",  # Categories as follows: general,anime,people
                "purity": "100",      # Purity: sfw,nsfw,null
                "ratios": f"{self.ratio[0]}x{self.ratio[1]}",
                "sorting": "relevance",
                "order": "desc"
            }
            try:
                res = requests.get(self.base_link, params=payload)
                print(f"URL: {res.url}")
                res.raise_for_status()
            except Exception as e:
                sys.exit(f"{type(e)}: {str(e)}\n"
                         f"An error occurred when downloading search page... Quitting")

            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            link_elements = [soup.select('.preview')]
            for link_list in link_elements:
                # Empty page so no more results to fetch
                if len(link_list) < 1:
                    return
                for link_object in link_list:
                    self.urls.append(link_object.get('href'))

    def grab_image_link(self):
        while True:
            # Get link from queue
            try:
                page_link = self.page_queue.get(block=False)
            except queue.Empty:
                return

            res = requests.get(page_link)
            # Parse it
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            _url = soup.select('#wallpaper')[0].get('src')
            print(f"Link fetched {_url}")
            # Add it to download queue
            self.image_queue.put(_url)

    def grab_image(self):
        while True:
            # Get image from queue
            try:
                image_link = self.image_queue.get(block=True, timeout=1)
            except queue.Empty:
                if not self.grabbing:
                    return
                else:
                    continue

            # Request image
            image_link = image_link
            print(f'Downloading image: {image_link}')
            try:
                res = requests.get(image_link, timeout=10)
                res.raise_for_status()
            except Exception as e:
                print(f"Error!\n{type(e)}: {str(e)}")
                continue

            print('Finding image name')
            # Find a name for it
            n = 1
            while True:
                name = str(n) + image_link[-4:]
                if not os.path.isfile(os.path.join("Downloads", name)):
                    break
                n += 1
            print(f"Name found: {name}")

            # Save it
            with open(os.path.join('Downloads', name), 'wb') as image:
                for chunk in res.iter_content(514*1024):
                    image.write(chunk)

    def download_wallpapers(self, urls, thread_count=10):
        grabbing_threads = []
        downloading_threads = []
        for _url in urls:
            self.page_queue.put(_url)

        print("Starting worker threads...")
        self.grabbing = True
        for i in range(thread_count//2):
            thread = threading.Thread(target=self.grab_image_link)
            thread.start()
            grabbing_threads.append(thread)

        for i in range(thread_count//2):
            thread = threading.Thread(target=self.grab_image)
            thread.start()
            downloading_threads.append(thread)

        # Wait for grabbing of image links to finish
        for thread in grabbing_threads:
            thread.join()

        # Set grabbing to false and wait for downloading threads to finish
        self.grabbing = False
        for thread in downloading_threads:
            thread.join()
        print("Done!")
