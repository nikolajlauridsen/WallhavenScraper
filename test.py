from Wallhaven import Wallhaven

wallhaven = Wallhaven()
query = input('Search term: ')
page_count = input('Amount of pages to get: ')

urls = wallhaven.search(query, int(page_count))
direct_urls = wallhaven.download_wallpapers(urls)
print(f"Fetched urls: {urls}")
