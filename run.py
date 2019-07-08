from Wallhaven import Wallhaven

wallhaven = Wallhaven()
query = input('Search term: ')
page_count = input('Amount of pages to get: ')
search_count = int(input('Amount of threads to use for searching: '))
thread_count = int(input('Amount of threads to use for downloading: '))

urls = wallhaven.search(query, int(page_count), threads=search_count)
wallhaven.download_wallpapers(urls, thread_count=thread_count)
print(f"Fetched urls: {urls}")
print(f"Count: {len(urls)}")
