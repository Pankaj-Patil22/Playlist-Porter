import requests, json, urllib.parse
from mutagen.mp4 import MP4, MP4Cover

TOTAL_SONGS = 1

# only save the important data
def create_playlist_file(input_file_name, output_file_name):
    print("\nSaving the important data in a file")
    with open(input_file_name, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)

    records = {"playlist": []}

    for item in data['list']:
        title = item.get('title','')
        image = item.get('image','')
        artists = ', '.join([artist['name'] for artist in item.get('more_info',{}).get('artistMap',{}).get('artists',[])])
        album = item.get('more_info', {}).get('album', '')
        label = item.get('more_info', {}).get('label', '')
        bitrate = item.get('more_info', {}).get('320kbps', '')
        encrypted_media_url = item.get('more_info', {}).get('encrypted_media_url', '')

        record = {
            'title': title,
            'image': image,
            'artists': artists,
            'album': album,
            'label': label,
            '320kbps': bitrate,
            'encrypted_media_url': encrypted_media_url
        }
        records["playlist"].append(record)

    save_file([json.dumps(records)], output_file_name)  
    print("\nImportant Information Saved")

# Add metadata to the MP4 file
def write_metadata(cover_art, artists, album, label, mp4_file):
    mp4_file['\xa9ART'] = artists # Add artist names
    mp4_file['\xa9alb'] = album # Add album name
    mp4_file['\xa9grp'] = label  # Add label information

    # Load album art image file
    mp4_file['covr'] = [MP4Cover(cover_art)]
    mp4_file.save()

# Get the auth url
def get_auth_url(encrypted_media_url, is320kbps):
    bitrate = '320' if is320kbps else '128'
    encrypted_media_url = urllib.parse.quote(encrypted_media_url)
    url = "https://www.jiosaavn.com/api.php?__call=song.generateAuthToken&url={}&bitrate={}&api_version=4&_format=json&ctx=web6dot0&_marker=0".format(encrypted_media_url, bitrate)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        auth_url = data.get('auth_url')
        return auth_url.replace('\\','')
    else: 
        print("Some error occured while getting auth_url")

def sanitize_name(name):
    unwanted_chars = r'\/:*?"<>|'  # Unwanted characters to remove
    for char in unwanted_chars:
        name = name.replace(char, '')  # Replace unwanted character with an empty string
    return name

def download_song(input_file):
    with open(input_file, 'r') as file:
        playlist_data = json.load(file)

    count = 0
    songs_downloaded = []

    for item in playlist_data['playlist']:
        cover_art = requests.get(item['image'])
        
        auth_url = get_auth_url(item['encrypted_media_url'], item['320kbps'])

        auth_response = requests.get(auth_url)
        if auth_response.status_code == 200:
            file_name = sanitize_name(item['title']+'.mp4')
            file_name = 'songs/'+file_name
            with open(file_name,'wb') as mp4:
                mp4.write(auth_response.content)

            mp4_file = MP4(file_name)
            write_metadata(cover_art.content, item['artists'], item['album'], item['label'], mp4_file)
            songs_downloaded.append(file_name)
            count = count + 1
            print('File name', file_name, 'Count', count)
        else:
            print("Error fetching data from auth URL:", auth_response.status_code)

    if count == TOTAL_SONGS:
        print("\nDownloading Songs Successful. Total songs downloaded", count)
        save_file(songs_downloaded, 'songs_downloaded.txt')
    else:
        Exception("Failed to download all the songs")

# to remove the newline characters which are present not needed in response and make the json valid. 
def remove_newlines(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file_in:
            content = file_in.read()
        # Remove newline characters
        content = content.replace('\n', '')
        save_file(content, output_file)

        print("Newlines removed and content written to", output_file)
    except FileNotFoundError:
        print("File not found.")

# this function will construct the URL needed for the Get request to get all the songs in the playlist for JioSaavn
def construct_url_jiosaavn():
    request_template = "https://www.jiosaavn.com/api.php?__call=webapi.get&token={token}&type=playlist&p={pagination}&n={total_songs}&includeMetaTags=0&ctx=wap6dot0&api_version=4&_format=json&_marker=0"
    playlist_url = input("Enter your playlist URL\n")
    token_value = playlist_url.split('/')[-1]
    pagination_value = 1
    TOTAL_SONGS = int(input("Enter total number of songs in your playlist\n"))
    total_songs_value = TOTAL_SONGS + 100
    print("Constructing URL")
    return request_template.format(token=token_value, pagination=pagination_value, total_songs=total_songs_value)

def save_file(content, file_name): 
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(content)
        print(f"Content saved successfully to {file_name}")
    except Exception as e:
        print(f"Error occurred while saving content to {file_name}: {str(e)}")

def main():
    request_url = construct_url_jiosaavn() 
    print("Request URL is " + request_url)
    response = requests.get(request_url) # get the playlist
    save_file(response.text, "ResponsePlaylistJson.txt") 
    remove_newlines("ResponsePlaylistJson.txt", "RemovedNextLines.txt")
    create_playlist_file("RemovedNextLines.txt", "Playlist.txt")
    download_song('Playlist.txt')

if __name__ == "__main__":
    main()