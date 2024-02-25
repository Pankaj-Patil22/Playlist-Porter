import requests 


# this function will construct the URL needed for the Get request to get all the songs in the playlist for JioSaavn
def construct_url_jiosaavn():
    request_template = "https://www.jiosaavn.com/api.php?__call=webapi.get&token={token}&type=playlist&p={pagination}&n={total_songs}&includeMetaTags=0&ctx=wap6dot0&api_version=4&_format=json&_marker=0"
    playlist_url = input("Enter your playlist URL\n")
    token_value = playlist_url.split('/')[-1]
    pagination_value = 1
    total_songs = input("Enter total number of songs in your playlist\n")
    total_songs_value = int(total_songs) + 100
    return request_template.format(token=token_value, pagination=pagination_value, total_songs=total_songs_value)

def save_file(content, file_name): 
    try:
        with open(file_name, 'w') as file:
            file.write(content)
        print(f"Content saved successfully to {file_name}")
    except Exception as e:
        print(f"Error occurred while saving content to {file_name}: {str(e)}")

def main():
    request_url = construct_url_jiosaavn() 
    response = requests.get(request_url) # get the playlist
    save_file(response.text, "playlist_json.txt") 
    



if __name__ == "__main__":
    main()