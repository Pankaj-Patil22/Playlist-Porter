import requests, json

# only save the important data
def create_playlist_file(input_file_name, output_file_name):
    print("\nSaving the important data in a file")
    with open(input_file_name, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)

    records = []

    for item in data['list']:
        title = item.get('title','')
        image = item.get('image','')
        artists = ', '.join([artist['name'] for artist in item.get('more_info',{}).get('artistMap',{}).get('artists',[])])
        encrypted_media_url = item.get('more_info', {}).get('encrypted_media_url', '')
        record_str = json.dumps({'title': title, 'image': image, 'artists': artists, 'encrypted_media_url': encrypted_media_url}) + '\n'
        records.append(record_str)

    save_file(records, output_file_name)   

def download_song(input_file):
    #encrypted_media_url use this
    url = "https://www.jiosaavn.com/api.php?__call=song.generateAuthToken&url={encrypted_media_url}&bitrate=128&api_version=4&_format=json&ctx=wap6dot0&_marker=0"


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
    total_songs = input("Enter total number of songs in your playlist\n")
    total_songs_value = int(total_songs) + 100
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

if __name__ == "__main__":
    main()