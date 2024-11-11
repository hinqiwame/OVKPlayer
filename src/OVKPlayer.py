# Static imports
import api  # OpenVK API wrapper

# Global variable to track the currently playing song
current_track = None

def displayCurrentTrack():
    global current_track
    from os import environ
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  
    from pygame import mixer
    if current_track and mixer.music.get_busy():  # Check if a song is currently playing
        print(f"Now playing: {current_track['artist']} - {current_track['title']}\n")
    else:
        current_track = None  # Clear current track if no song is playing

def clear():
    import platform
    from os import system, _exit
    if platform.system() == "Windows":
        system("cls")
    elif platform.system() == "Linux":
        system("clear")
    else:
        print("Not supported OS")
        _exit(0)

def playTrack(track):
    global current_track
    current_track = track  # Set the currently playing track
    import requests
    import tempfile
    from os import environ
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame message
    from pygame import mixer
    mixer.init()
    request = requests.get(track["url"], stream=True)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tempFile:
        tempFile.write(request.content)
        tempFile.flush()
        mixer.music.load(tempFile.name)
        mixer.music.play()

def searchScreen():
    try:
        clear()
        displayCurrentTrack()  # Display the current track if any
        from getpass import getpass
        from time import sleep
        query = input("Enter your search query: ")
        request = api.sendPost("Audio.search", q=query, lyrics=0, performer_only=0)["response"]
        sortedTracks = [track for track in request["items"] if query in track["artist"] or query in track["title"]]
        
        if not sortedTracks:
            print("No tracks found.")
            getpass("Press ENTER ")
            clear()
            searchScreen()
        else:
            clear()
            displayCurrentTrack()  # Display the current track if any
            for i, track in enumerate(sortedTracks):
                print(f"{i + 1}. {track['artist']} - {track['title']}")
            
            while True:
                print("Specify '-l' in your choice if you want to display the lyrics (e.g. 1 -l)")
                choice = input(">>> ")

                try:
                    trackNumber = int(choice.split()[0]) - 1  # Get the track number
                    
                    if 0 <= trackNumber < len(sortedTracks):
                        track = sortedTracks[trackNumber]
                        
                        if "-l" in choice:
                            try:
                                clear()
                                displayCurrentTrack()  # Display the current track if any
                                lyrics = api.sendPost("Audio.getLyrics", lyrics_id=track["lyrics"])["response"]["text"]
                                print(lyrics)
                                playTrack(track)
                                getpass("Press ENTER ")
                                mainScreen()
                            except:
                                print("Lyrics not found.")
                        
                        print(f"Playing {track['artist']} - {track['title']}...")
                        playTrack(track)
                        sleep(2)
                        mainScreen()
                    else:
                        print("Invalid track number. Please try again.")

                except ValueError:
                    print("Please enter a valid track number.")
    except KeyboardInterrupt:
        clear()
        mainScreen()

def mainScreen():
    try:
        clear()
        displayCurrentTrack()  # Display the current track if any
        from os import _exit
        from getpass import getpass
        print("Welcome to OpenVK CLI music player!\n\n"
              "Select:\n"
              "1. Search for a track in OpenVK\n"
              "2. Exit\n"
        )
        choice = input(">>> ")
        if choice == "1":
            searchScreen()
        elif choice == "2":
            print("Exiting...")
            _exit(0)
        else:
            print("Incorrect argument!")
            getpass("Press ENTER ")
            clear()
            mainScreen()
    except KeyboardInterrupt:
        from os import _exit
        print("\nExiting...")
        _exit(0)

if __name__ == "__main__":
    mainScreen()
