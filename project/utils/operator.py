import requests
from bs4 import BeautifulSoup as bs


def get_list(id: str):
    url = f"https://www.dnvods.com/index.php/vod/play/id/{id}/sid/1/nid/1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = bs(response.text, 'html.parser')

    # Extract the name from the title
    title = soup.find('title').text
    key_word = ["多瑙影院", "在线播放", "电视剧", "动漫", "综艺", "电影", "在线观看", "高清", "免费", "海外", "热播",
                "最新", "最热", "最全", "最好看", "最新电影", "最新电视剧", "--", "1", "华人影院"]
    for i in key_word:
        title = title.replace(i, "")
    title = title.replace(" ", "")
    # 二分
    l = len(title)
    name = title[:l // 2]
    name = name.strip()
    # Extract cover image url
    cover_div = soup.find('div', class_='play_vlist_thumb vnow lazyload')
    url = cover_div['data-original']

    # Create a dictionary to store the playlists
    # playlists_dict = {"name": name, "cover": url, "response": {}}
    playlists = soup.find_all('ul', class_='content_playlist')

    # Create a dictionary to store the playlists
    playlists_dict = {"name": name, "cover": url, "response": {}}

    for i, playlist in enumerate(playlists):
        playlist_items = playlist.find_all('li')

        for item in playlist_items:
            link = item.find('a')['href']
            link = "https://www.dnvods.com" + link  # prepend the domain to the link
            episode = link.split('/')[-1]  # get the episode number from the link
            # remove the ".html" from the end and only keep the number part
            episode = "episode" + episode.split('.html')[0].replace('nid/', '')

            if episode not in playlists_dict["response"]:
                playlists_dict["response"][episode] = {"links": set()}

            playlists_dict["response"][episode]["links"].add(link)

    # Convert the sets into lists again to allow json serialization
    for episode in playlists_dict["response"].values():
        episode["links"] = list(episode["links"])

    # Convert the final dictionary into JSON
    # playlists_json = json.dumps(playlists_dict, indent=4)
    # print(playlists_json)
    return playlists_dict


def async_task_get_list_list(anime_id_list: list):
    result_list = []
    for i in anime_id_list:
        i_modified = get_list(i)
        result_list.append(i_modified)
    result = {"result": result_list}
    return result
