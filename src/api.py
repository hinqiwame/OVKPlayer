def readToken():
    import os

    # Define the token file path using the user's home directory
    home_dir = os.path.expanduser("~")
    token_file = os.path.join(home_dir, ".ovkplayer", "token.txt")

    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            return file.read().strip()  # Read and strip any extra whitespace
    return None

def getToken(email, password):
    import requests
    import os

    # Define the directory and token file path using the user's home directory
    home_dir = os.path.expanduser("~")
    token_dir = os.path.join(home_dir, ".ovkplayer")
    token_file = os.path.join(token_dir, "token.txt")

    url = f"https://ovk.to/token?username={email}&password={password}&grant_type=password"
    response = requests.get(url)

    if response.status_code == 200:
        # Check if the directory exists, and create it if not
        if not os.path.exists(token_dir):
            os.mkdir(token_dir)

        # Write the access token to the file
        with open(token_file, "w") as file:
            file.write(response.json()["access_token"])

        return response.json()["access_token"]
    else:
        return None

def sendGet(method):
    import requests

    token = readToken()  # Read token from the file
    if not token:
        return False

    url = f"https://ovk.to/method/{method}?access_token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error sending GET request: {response.status_code} - {response.text}"

def sendPost(method, **kwargs):
    import requests

    token = readToken()  # Read token from the file
    if not token:
        return False

    data = {}
    data.update(kwargs)

    url = f"https://ovk.to/method/{method}?access_token={token}"
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error sending POST request: {response.status_code} - {response.text}"
