import requests, json, urllib.parse, os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TPE2, TPE3, TPUB, TCOP,TCOM, TEXT, TYER, TDRC, TLAN, TSIZ, TIME, TDAT, TDRC, TIPL, COMM, APIC

TOTAL_SONGS = 1

def sanitize_name(name):
    unwanted_chars = r'\/:*?"<>|'  # Unwanted characters to remove
    for char in unwanted_chars:
        name = name.replace(char, '')
    return name

def fix_file_name(name):
    quotes = ['\u2019','&quot;','&#039;', '\u2018']
    for quote in quotes:
        if quote in name:
            name = name.replace(quote, "'")
    return name

def get_song_name(name):
    file_name = fix_file_name(name+'.mp3')
    file_name = sanitize_name(file_name)
    return 'songs/'+file_name

def generate_unique_file_name(base_name, existing_file_names):
    suffix = 1
    for file_name in existing_file_names:
        if base_name in file_name:
            base_name = base_name + str(suffix)
            suffix += 1
    
    return get_song_name(base_name)

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


# Add mp4_file to the MP4 file
def write_metadata(cover_art, item, mp3_file):
    mp3_file.tags.add(
        APIC(
            encoding=3,  # utf-8
            mime='image/jpeg',  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc=u'Cover',
            data=cover_art
        )
    )
    mp3_file.tags.add(TIT2(encoding=3, text = item["title"]))
    mp3_file.tags.add(TALB(encoding=3, text = item["album"]))
    mp3_file.tags.add(TPE1(encoding=3, text = item["primary_artists"]))
    mp3_file.tags.add(TPE2(encoding=3, text = item["featured_artists"]))
    mp3_file.tags.add(TPE3(encoding=3, text = item["artists"]))
    mp3_file.tags.add(TPUB(encoding=3, text = item["label"]))
    mp3_file.tags.add(COMM(encoding=3, lang = item["language"], text= item["primary_artists"] + ', ' + item["featured_artists"] + ', ' + item["artists"] ))
    mp3_file.save()
    
    # mp4_file['\xa9ART'] = primary_artists  # Primary artist
    # mp4_file['aART'] = featured_artists  # Featured artist
    # mp4_file['\xa9grp'] = label # Add label information
    # mp4_file['\xa9wrt'] = primary_artists + ', '+ featured_artists + ', ' + artists  # All artists
    # mp4_file['covr'] = [MP4Cover(cover_art)]
    # mp4_file['\xa9alb'] = album # Add album info
    # mp4_file['\xa9nam'] = title # Add title
    # mp4_file.save()

def download_song(input_file):
    with open(input_file, 'r') as file:
        playlist_data = json.load(file)

    count = 0
    songs_downloaded = []
    songs_not_downloaded = []

    for song in playlist_data['list']:
        try: 
            cover_art = requests.get(song['image'].replace('150x150','500x500'))
            
            auth_url = get_auth_url(song.get('more_info', {}).get('encrypted_media_url', ''), song.get('more_info', {}).get('320kbps', ''))

            auth_response = requests.get(auth_url)
            if auth_response.status_code == 200:
                file_name = generate_unique_file_name(song['title'], songs_downloaded)
                with open(file_name,'wb') as mp3:
                    mp3.write(auth_response.content)

                mp3_file = MP3(file_name, ID3=ID3)
                write_metadata(cover_art.content, song , mp3_file)
                songs_downloaded.append(file_name + '\n')
                count = count + 1
                print('File name', file_name, 'Count', count)
            else:
                songs_not_downloaded.append(song['title'] + '\n')
                print("Error fetching data from auth URL:", auth_response.status_code)
        except:
            print('could not download this song', song['title'])
            songs_not_downloaded.append(song['title'] + '\n' )

    if count == TOTAL_SONGS:
        print("\nDownloading Songs Successful. Total songs downloaded", count)
        save_file(songs_downloaded, 'songs_downloaded.txt')
        save_file(songs_not_downloaded, 'songs_not_downloaded.txt')
    else:
        Exception("Failed to download all the songs")
        save_file(songs_downloaded, 'songs_downloaded.txt')
        save_file(songs_not_downloaded, 'songs_not_downloaded.txt')

def verify_downloads(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        intended_downloads = file.read().splitlines()

    downloaded_song_count = 0
    songs_downloaded = []
    songs_not_downloaded = []

    downloaded_files = os.listdir("songs")

    for title in intended_downloads:
        file_name = title.replace('songs/','')
        if file_name in downloaded_files:
            downloaded_song_count += 1
            songs_downloaded.append(file_name + '\n')
        else:
            songs_not_downloaded.append(file_name + '\n')

    print("Total songs downloaded", downloaded_song_count)
    save_file(songs_downloaded,'songs_downloaded_verify.txt')
    save_file(songs_not_downloaded,'songs_not_downloaded_verify.txt')

    if downloaded_song_count < TOTAL_SONGS:
        print("All songs not downloaded")

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
    remove_newlines("ResponsePlaylistJson.txt", "Playlist.json")
    download_song('Playlist.json')
    # verify_downloads('songs_downloaded.txt')

if __name__ == "__main__":
    main()