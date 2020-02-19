import requests, smtplib, os, time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
email_username = os.getenv("EMAIL_USER")
email_to = os.getenv("EMAIL_TO")
email_pass = os.getenv("EMAIL_PASS")
api_url = os.getenv("API_URL")
graph_url = os.getenv("GRAPH_URL")
item_id = 444  # Game's ItemID

# Gets the price for checking
def getPrice():
    r = requests.get(api_url + str(item_id))
    response = r.json()
    return response["item"]["current"]["price"]


# Text in a human readable format
def getData():
    req = requests.get(api_url + str(item_id))
    response = req.json()
    item_name = response["item"]["name"]
    graph = requests.get(graph_url + str(item_id) + ".json")
    graph_response = graph.json()
    # converts to list to get the last element ("latest")
    daily_prices = list(graph_response["daily"])
    formatted_string = (
        "Yesterday: "
        # Converts epochtime millisecond into readable day/time
        + datetime.fromtimestamp(int(daily_prices[-1]) // 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        + " --- value of "
        + item_name
        + " is: "
        + str(graph_response["daily"][str(daily_prices[-2])])
        + "\nToday's current Value is: "
        + str(response["item"]["current"]["price"])
        + " ("
        + str(graph_response["daily"][str(daily_prices[-1])])
        + ")"
        + "\nToday's difference: "
        + str(response["item"]["today"]["price"])
    )
    return formatted_string


# Infinite loop to run continuously, check every 15 mins
while True:
    if datetime.today().minute % 15 == 0:
        if getPrice() > 350:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(email_username, email_pass)
                subject = "Gold Ore"
                body = getData()
                msg = f"Subject: {subject}\n\n{body}"
                smtp.sendmail(email_username, email_to, msg)
                print("SENT")
        time.sleep(60)

