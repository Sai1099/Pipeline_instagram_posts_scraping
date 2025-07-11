import requests
import json

url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=marketsbyzerodha"
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "x-ig-app-id": "936619743392459",
}

response = requests.get(url, headers=headers)

o = {}
post = {}
allpost = []
insta_arr = []

if response.status_code == 200:
    allData = response.json()['data']['user']
    o['biography'] = allData['biography']
    o['link_in_bio'] = allData['bio_links'][0]['url'] if allData['bio_links'] else None
    o['followers'] = allData['edge_followed_by']['count']
    o['following'] = allData['edge_follow']['count']
    o['num_posts'] = allData['edge_owner_to_timeline_media']['count']
    o['profile_pic_url'] = allData['profile_pic_url_hd']
    o['verified'] = allData['is_verified']

    allPosts = allData['edge_owner_to_timeline_media']['edges']

    for i in range(len(allPosts)):
        node = allPosts[i]['node']
        post = {
            'display_url': node['display_url'],
            'num_comments': node['edge_media_to_comment']['count'],
            'num_likes': node['edge_liked_by']['count'],
            'is_video': node['is_video']
        }
        if node['is_video']:
            post['video_view_count'] = node.get('video_view_count')
            post['video_url'] = node.get('video_url')

        allpost.append(post)

    insta_arr.append(o)
    insta_arr.append(allpost)

    # Save to file
    with open("output.json", "w") as f:
        json.dump(insta_arr, f, indent=2)

    print("✅ Data saved to output.json")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
