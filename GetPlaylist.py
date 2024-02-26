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
        primary_artists = '. '.join([primary_artist['name'] for primary_artist in item.get('more_info',{}).get('artistMap',{}).get('primary_artists',[])])
        featured_artists = '. '.join([featured_artist['name'] for featured_artist in item.get('more_info',{}).get('artistMap',{}).get('featured_artists',[])])
        album = item.get('more_info', {}).get('album', '')
        label = item.get('more_info', {}).get('label', '')
        bitrate = item.get('more_info', {}).get('320kbps', '')
        encrypted_media_url = item.get('more_info', {}).get('encrypted_media_url', '')

        record = {
            'title': title,
            'image': image,
            'artists': artists,
            'primary_artists': primary_artists,
            'featured_artists': featured_artists,
            'album': album,
            'label': label,
            '320kbps': bitrate,
            'encrypted_media_url': encrypted_media_url
        }
        records["playlist"].append(record)

    save_file([json.dumps(records)], output_file_name)  
    print("\nImportant Information Saved")

# Add metadata to the MP4 file
def write_metadata(cover_art, primary_artists, featured_artists, artists, album, label, mp4_file):
    mp4_file['\xa9ART'] = ["Primary Artist"]  # Primary artist
    mp4_file['aART'] = ["Featured Artist"]  # Featured artist
    mp4_file['\xa9wrt'] = artists # Add artist names
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
        name = name.replace(char, '')
    return name

def fix_file_name(name):
    if '\u2019' in name or '&quot;' in name:
        name = name.replace('\u2019',"'")
    return name

def get_song_name(name):
    file_name = fix_file_name(name+'.mp4')
    file_name = sanitize_name(file_name)
    return 'songs/'+file_name

def download_song(input_file):
    with open(input_file, 'r') as file:
        playlist_data = json.load(file)

    count = 0
    songs_downloaded = []
    songs_not_downloaded = []

    for item in playlist_data['playlist']:
        try: 
            cover_art = requests.get(item['image'])
            
            auth_url = get_auth_url(item['encrypted_media_url'], item['320kbps'])

            auth_response = requests.get(auth_url)
            if auth_response.status_code == 200:
                file_name = get_song_name(item['title'])
                with open(file_name,'wb') as mp4:
                    mp4.write(auth_response.content)

                mp4_file = MP4(file_name)
                write_metadata(cover_art.content, item['artists'], item['album'], item['label'], mp4_file)
                songs_downloaded.append(item['title'])
                count = count + 1
                print('File name', file_name, 'Count', count)
            else:
                songs_not_downloaded.append(item['title'])
                print("Error fetching data from auth URL:", auth_response.status_code)
        except:
            print('could not download this song', item['title'])
            songs_not_downloaded.append(item['title'])

    if count == TOTAL_SONGS:
        print("\nDownloading Songs Successful. Total songs downloaded", count)
        save_file(songs_downloaded, 'songs_downloaded.txt')
        save_file(songs_not_downloaded, 'songs_not_downloaded.txt')
    else:
        Exception("Failed to download all the songs")
        save_file(songs_downloaded, 'songs_downloaded.txt')
        save_file(songs_not_downloaded, 'songs_not_downloaded.txt')

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