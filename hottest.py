import logging
import random
import requests
import hashlib
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Function to interact with the game API and get the user's rank
def get_user_rank(Game_Url, score):
    session = requests.session()
    session.headers = {
        "Referer": "https://prizes.gamee.com/"
    }

    Game_Hash = ((Game_Url.split("#")[0]).split("/")[3:])[1]

    data = session.post("https://api.service.gameeapp.com/", json={
        "jsonrpc": "2.0",
        "id": "game.getWebGameplayDetails",
        "method": "game.getWebGameplayDetails",
        "params": {
            "gameUrl": f"/game-bot/{Game_Hash}"
        }
    }).json()

    gameid = data['result']['game']['id']
    release = data['result']['game']['release']['number']

    auth_load = {
        "jsonrpc": "2.0",
        "id": "user.authentication.botLogin",
        "method": "user.authentication.botLogin",
        "params": {
            "botName": "telegram",
            "botGameUrl": f"/game-bot/{Game_Hash}",
            "botUserIdentifier": None
        }
    }

    auth_r = requests.post("https://api.service.gameeapp.com/", headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45",
        "X-Install-Uuid": "23ce11ca-a85d-4540-a4b2-89d32d76623a"
    }, json=auth_load).json()

    authni = auth_r['result']['tokens']['refresh']

    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        "authorization": "Bearer %s" % authni,
        "Content-Type": "application/json"
    }

    time = data['time']
    playtime = random.randint(300, 2000)

    gameStateData = ''
    hashs1 = hashlib.md5(
        f'{str(score)}:{str(playtime)}:/game-bot/{Game_Hash}:{gameStateData}:crmjbjm3lczhlgnek9uaxz2l9svlfjw14npauhen'.encode()).hexdigest()

    result = session.post("https://api.service.gameeapp.com/", json={
        "jsonrpc": "2.0",
        "id": "game.saveWebGameplay",
        "method": "game.saveWebGameplay",
        "params": {
            "gameplayData": {
                "gameId": int(gameid),
                "score": int(score),
                "playTime": int(playtime),
                "gameUrl": f"/game-bot/{Game_Hash}",
                "metadata": {"gameplayId": 3},
                "releaseNumber": int(release),
                "gameStateData": None,
                "createdTime": "%s" % time,
                "checksum": hashs1,
                "replayVariant": None,
                "replayData": None,
                "replayDataChecksum": None,
                "isSaveState": False,
                "gameplayOrigin": "game"
            }
        }
    }).json()

    main = result['result']['surroundingRankings'][0]['ranking']

    user_ranks = []
    for user in main[::-1]:
        user_info = {
            'NumId': user['user']['id'],
            'FirstName': user['user']['firstname'],
            'LastName': user['user']['lastname'],
            'NickName': user['user']['nickname'],
            'Score': user['score']
        }
        user_ranks.append(user_info)

    return user_ranks

# Command handler for the /start command
def start(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f"Hi {user.first_name}!\nI am your FoxCheat bot. Send me your Game URL and score, and I'll show you the ranks!")

# Message handler for regular text messages
def process_game_info(update: Update, _: CallbackContext) -> None:
    user_input = update.message.text.strip().split("\n")

    if len(user_input) == 2:
        Game_Url, score = user_input
        try:
            score = int(score)
            ranks = get_user_rank(Game_Url, score)
            response = "\n\n".join([f"{rank['FirstName']} {rank['LastName']} | Score: {rank['Score']}" for rank in ranks])
        except ValueError:
            response = "Invalid score format. Please provide an integer value."
    else:
        response = "Invalid input format. Please provide the Game URL and score in separate lines."

    update.message.reply_text(response)


def main() -> None:
    # Replace 'YOUR_API_TOKEN' with your actual API token here
    updater = Updater("6032026152:AAGvoKfOCrhgJyV3JCMLn_bDvuXzqvcvfRg")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_game_info))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
  
