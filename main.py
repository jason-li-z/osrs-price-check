import requests, smtplib, os, time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
email_username = os.getenv("EMAIL_USER")
email_to = os.getenv("EMAIL_TO")
email_me = os.getenv("EMAIL_ME")
email_pass = os.getenv("EMAIL_PASS")
api_url = os.getenv("API_URL")
graph_url = os.getenv("GRAPH_URL")
item_id = 444  # Game's ItemID

# Gets the price for checking
def getPrice():
    r = requests.get(api_url + str(item_id))
    response = r.json()
    return response["item"]["current"]["price"]


def sendEmail(initial_price):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_username, email_pass)
        subject = "Gold Ore"
        body = getData()
        alt = "Will send another update once price reaches " + str(initial_price + 5)
        msg = f"Subject: {subject}\n\n{body}\n{alt}"
        smtp.sendmail(email_username, email_to, msg)
        smtp.sendmail(email_username, email_me, msg)


def sendEmailAfter(initial_price):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_username, email_pass)
        subject = "Gold Ore"
        body = getData()
        alt = (
            "Will send another update once price reaches "
            + str(initial_price + 5)
            + " or "
            + str(initial_price - 5)
        )
        msg = f"Subject: {subject}\n\n{body}\n{alt}"
        smtp.sendmail(email_username, email_to, msg)
        smtp.sendmail(email_username, email_me, msg)


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
initial_price = 350
reached = False
reached_price = 0
sub_price = 0
while True:
    if datetime.today().minute % 15 == 0:
        if reached and getPrice() % 5 == 0:
            if getPrice() == reached_price:
                sendEmailAfter(reached_price)
                sub_price = reached_price - 5
                reached_price += 5
            elif getPrice() == sub_price:
                sendEmailAfter(sub_price)
                reached_price = sub_price + 5
                sub_price -= 5

        elif getPrice() >= 350:
            reached = True
            reached_price = getPrice() + 5  # 355
            sub_price = getPrice() - 5  # 345
            sendEmailAfter(350)
        time.sleep(60)
