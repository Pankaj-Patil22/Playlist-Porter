import requests, re


def save_each_song_on_next_line(input_file_name, output_file_name):
    print("\nSaving each song on different line")
    # Define the regular expression pattern
    pattern = r'\{"id":"[a-zA-Z0-9_-]{8}","title":'

    # Read data from the file
    output = []
    count = 0
    with open(input_file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            matches = re.findall(pattern, line)
            for match in matches:
                count = count + 1
                line = line.replace(match, '\n\n' + match)
            output.append(line)

    # Write the modified data to the output file
    save_file(output, output_file_name)

    print("Each song saved on next line and content written to", output_file_name)
    print("Total number of songs found", count)


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
    save_file(response.text, "PlaylistJson.txt") 
    remove_newlines("PlaylistJson.txt", "RemovedNextLines.txt")
    save_each_song_on_next_line("RemovedNextLines.txt", "EachSongOnNextLine.txt")

if __name__ == "__main__":
    main()