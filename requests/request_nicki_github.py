import requests
response = requests.get("https://api.github.com/repos/SkafteNicki/dtu_mlops")
#print(response.content)

# Human-readable JSON
json = response.json()
#print(json)


# Use the GET method we can additionally provide a params argument, 
# # that specifies what we want the server to send back for a specific request URL
response = requests.get(
    'https://api.github.com/search/repositories',
    params={'q': 'requests+language:python'},
)

# Download an image
response = requests.get('https://imgs.xkcd.com/comics/making_progress.png')
with open(r'img.png','wb') as f:
    f.write(response.content)
    #print(response.content)

# POST request
pload = {'username':'Olivia','password':'123'}
response = requests.post('https://httpbin.org/post', data = pload)
#print(response.content)