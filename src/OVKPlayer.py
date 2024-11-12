# Static imports
import api  # OpenVK API wrapper

current_track = None
track_queue = []

def displayCurrentTrack():
    global current_track
    from os import environ
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    import pygame
    pygame.mixer.init()
    
    if current_track and pygame.mixer.music.get_busy():
        from colorama import init, Style
        init()
        print(f"{Style.BRIGHT}Now playing: {current_track['artist']} - {current_track['title']}{Style.RESET_ALL}\n")
    else:
        playNextInQueue()

def playNextInQueue():
    global track_queue, current_track
    from os import environ
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    import pygame
    pygame.mixer.init()
    
    if track_queue:
        current_track = track_queue.pop(0)
        pygame.mixer.music.load(current_track["file_path"])
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
    else:
        current_track = None

def addToQueue(track):
    global track_queue
    import requests
    import tempfile

    request = requests.get(track["url"], stream=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(request.content)
    temp_file.flush()
    temp_file.close()

    track_with_file = track.copy()
    track_with_file["file_path"] = temp_file.name
    track_queue.append(track_with_file)
    print(f"Added {track['artist']} - {track['title']} to queue.")

def viewQueue():
    clear()
    displayCurrentTrack()
    if not track_queue:
        print("The queue is empty.")
    else:
        print("Queued Tracks:")
        for i, track in enumerate(track_queue):
            print(f"{i + 1}. {track['artist']} - {track['title']}")
    input("\nPress ENTER to return to the main screen.")
    mainScreen()

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
    current_track = track
    import requests
    import tempfile
    from os import environ
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    import pygame
    pygame.mixer.init()

    request = requests.get(track["url"], stream=True)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tempFile:
        tempFile.write(request.content)
        tempFile.flush()
        pygame.mixer.music.load(tempFile.name)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

def searchScreen():
    try:
        clear()
        displayCurrentTrack()
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
            displayCurrentTrack()
            for i, track in enumerate(sortedTracks):
                print(f"{i + 1}. {track['artist']} - {track['title']}")
            
            while True:
                print("Specify '-l' to display lyrics or '-q' to add to queue (e.g., '1 -l -q')")
                choice = input(">>> ")

                try:
                    trackNumber = int(choice.split()[0]) - 1
                    
                    if 0 <= trackNumber < len(sortedTracks):
                        track = sortedTracks[trackNumber]
                        
                        show_lyrics = "-l" in choice
                        add_to_queue = "-q" in choice
                        
                        if show_lyrics:
                            try:
                                clear()
                                displayCurrentTrack()
                                lyrics = api.sendPost("Audio.getLyrics", lyrics_id=track["lyrics"])["response"]["text"]
                                print(lyrics)
                            except:
                                print("Lyrics not found.")
                        
                        if add_to_queue:
                            addToQueue(track)
                            print(f"Added {track['artist']} - {track['title']} to queue.")
                        
                        if not add_to_queue:
                            print(f"Playing {track['artist']} - {track['title']}...")
                            playTrack(track)
                            sleep(2)
                            mainScreen()
                        else:
                            getpass("Press ENTER to return to main screen")
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
        displayCurrentTrack()
        from os import _exit
        from getpass import getpass
        print("Welcome to OpenVK CLI music player!\n\n"
              "Select:\n"
              "1. Search for a track in OpenVK\n"
              "2. View Queue\n"
              "3. Exit\n"
        )
        choice = input(">>> ")
        if choice == "1":
            searchScreen()
        elif choice == "2":
            viewQueue()
        elif choice == "3":
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

def handleEvents():
    import pygame
    pygame.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                playNextInQueue()

if __name__ == "__main__":
    import threading
    event_thread = threading.Thread(target=handleEvents, daemon=True)
    event_thread.start()
    mainScreen()
