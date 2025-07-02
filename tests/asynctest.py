import requests

gamma = "https://gamma-api.polymarket.com/" 

iparams = {
    "series_id": "2",
    "start_date_min": "2023-09-01",
    "limit" : "10000"
}
response = requests.get(gamma+"events", params=iparams)


if response.status_code == 200:
    res = response.json()
    print(f"Total Games: {len(res)}")
    # with open('data.json', 'w') as f:
    #     json.dump(data, f)

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print("Response content:", response.text)