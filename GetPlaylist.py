def construct_url():
    # this function will construct the URL needed for the Get request to get all the songs in the playlist
    request_template = "https://www.jiosaavn.com/api.php?__call=webapi.get&token={token}&type=playlist&p={pagination}&n={total_songs}&includeMetaTags=0&ctx=wap6dot0&api_version=4&_format=json&_marker=0"
    playlist_url = input("Enter your playlist URL")
    token_value = playlist_url.split('/')[-1]
    pagination_value = 1
    total_songs = input("Enter total number of songs in your playlist")
    total_songs_value = total_songs + 100
    return request_template.format(token=token_value, pagination=pagination_value, total_songs=total_songs_value)

def main():
    request_url = construct_url()


if __name__ == "__main__":
    main()