import json

with open('tmdb.json', 'r', encoding="utf-8") as f:
    data = json.load(f)

count = len(data)
print(f"The number of entries is: {count}")
