# import requests
# from bs4 import BeautifulSoup
#
# def find_video_url(url):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
#
#             # Example: Find video URL within <video> tag
#             video_tag = soup.find('video')
#             if video_tag:
#                 video_url = video_tag['src']
#                 return video_url
#
#             # Example: Find video URL within <iframe> tag
#             iframe_tag = soup.find('iframe')
#             if iframe_tag:
#                 iframe_url = iframe_tag['src']
#                 return iframe_url
#
#             # Add more specific parsing based on the website structure
#
#         else:
#             print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error accessing {url}: {e}")
#
#     return None
#
# if __name__ == "__main__":
#     url = "https://fmovies24.to/tv/elementary-5k06j/4-10"
#     video_url = find_video_url(url)
#
#     if video_url:
#         print(f"Found video URL: {video_url}")
#         # Now you can proceed to download or play the video using the extracted URL
#     else:
#         print("Video URL not found or unable to access.")
