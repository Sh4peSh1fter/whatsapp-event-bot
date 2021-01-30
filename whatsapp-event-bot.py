# Imports
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from difflib import SequenceMatcher


# Constants
MANUAL = "help / ? - prints this manual.\n" \
         "bitcoin - get the current value of bitcoin.\n" \
         "events - get this weeks DevOps and Cloud events.\n" \
         "meme - get random meme." \
         "Have Fun!"
BITCOIN_API = "https://api.coindesk.com/v1/bpi/currentprice.json"
HEBREW_TO_ENGLISH_MONTHS = {"ינואר": "January", "פברואר": "February", "מרץ": "March", "אפריל": "April", "מאי": "May", "יוני" : "June", "יולי": "July", "אוגוסט": "August", "ספטמבר": "September", "אוקטובר": "October", "נובמבר": "November", "דצמבר": "December"}
MIN_DIFF_RATIO = 0.75


# Globals
app = Flask(__name__)
event_sources = {"eventbrite": "https://www.eventbrite.com/d/online/free--events--next-week/devops/?page=1&lang=en",
                 "geektime": "https://geeklist.geektime.co.il/index_events.php"}
schedule = {"Sunday": [], "Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": []}


def get_manual():
    return MANUAL


def get_curr_bitcoin_value():
    response = requests.get(BITCOIN_API)
    response_json = response.json()

    return "The current price of Bitcoin in Dollars is {0}$".format(str(response_json['bpi']['USD']['rate']))


def next_weekday(curr_date, weekday):
    days_ahead = weekday - curr_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (curr_date + datetime.timedelta(days_ahead)).strftime("%b %d")


def find_weekday(date):
    year = datetime.datetime.now().year
    day, month = date.split(' ')
    month = datetime.datetime.strptime(month, "%B").month
    weekday = datetime.date(year, month, int(day))
    return weekday.strftime("%A")


def get_eventbrite():
    global schedule
    eventbrite_page = requests.get(event_sources["eventbrite"])
    soup = BeautifulSoup(eventbrite_page.content, 'html.parser')

    events_list = soup.find_all("div", {"class": "search-event-card-wrapper"})

    for div in events_list:
        name = div.find("div", {
            "class": "eds-event-card__formatted-name--is-clamped eds-event-card__formatted-name--is-clamped-three eds-text-weight--heavy"}).text
        date = div.find("div", {
            "class": "eds-text-color--primary-brand eds-l-pad-bot-1 eds-text-weight--heavy eds-text-bs"}).text
        print("{0}: {1}\n".format(name, date))

        date = date.split(", ")
        if date[0] == "Sun" and date[1] == next_weekday(datetime.date.today(), 6):
            schedule["Sunday"].append(name)
        elif date[0] == "Mon" and date[1] == next_weekday(datetime.date.today(), 0):
            schedule["Monday"].append(name)
        elif date[0] == "Tue" and date[1] == next_weekday(datetime.date.today(), 1):
            schedule["Tuesday"].append(name)
        elif date[0] == "Wed" and date[1] == next_weekday(datetime.date.today(), 2):
            schedule["Wednesday"].append(name)
        elif date[0] == "Thu" and date[1] == next_weekday(datetime.date.today(), 3):
            schedule["Thursday"].append(name)
        elif date[0] == "Fri" and date[1] == next_weekday(datetime.date.today(), 4):
            schedule["Friday"].append(name)
        elif date[0] == "Sat" and date[1] == next_weekday(datetime.date.today(), 5):
            schedule["Saturday"].append(name)


def get_geektime():
    global schedule

    opts = Options()
    opts.headless = True
    driver = webdriver.Chrome(options=opts, executable_path=ChromeDriverManager().install())

    try:
        driver.get(event_sources["geektime"])
        text = driver.page_source
    except Exception as e:
        raise e
    finally:
        driver.close()

    # geektime_page = requests.get(event_sources["geektime"])
    soup = BeautifulSoup(text, 'html.parser')

    data = []
    table = soup.find('table')
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    count = 0
    for row in rows:
        if count % 2 == 0 and count != 0:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
        count += 1

    for event in data:
        print(event)
        print("---")
        date = event[0] + " " + HEBREW_TO_ENGLISH_MONTHS["ינואר"]
        if find_weekday(date) == "Sunday" and date == next_weekday(datetime.date.today(), 6):
            schedule["Sunday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Monday" and date[1] == next_weekday(datetime.date.today(), 0):
            schedule["Monday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Tuesday" and date[1] == next_weekday(datetime.date.today(), 1):
            schedule["Tuesday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Wednesday" and date[1] == next_weekday(datetime.date.today(), 2):
            schedule["Wednesday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Thursday" and date[1] == next_weekday(datetime.date.today(), 3):
            schedule["Thursday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Friday" and date[1] == next_weekday(datetime.date.today(), 4):
            schedule["Friday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])
        elif date[0] == "Saturday" and date[1] == next_weekday(datetime.date.today(), 5):
            schedule["Saturday"].append(event[-2] + " (" + event[-1] + ") - " + event[-3])


def get_event():
    msg = ""
    count = 0

    get_eventbrite()
    # get_geektime()

    for day in schedule.keys():
        msg = msg + day

        if day == "Sunday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 6) + ")"
        elif day == "Monday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 0) + ")"
        elif day == "Tuesday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 1) + ")"
        elif day == "Wednesday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 2) + ")"
        elif day == "Thursday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 3) + ")"
        elif day == "Friday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 4) + ")"
        elif day == "Saturday":
            msg = msg + " (" + next_weekday(datetime.date.today(), 5) + ")"

        msg = msg + "\n------------\n"

        for event in schedule[day]:
            count += 1
            msg = msg + str(count) + ".    " + event + "\n"
        msg = msg + "\n"

    return msg


def get_meme():
    return "Coming Soon"


@app.route("/")
def home():
    return "The bot is working! try sending WhatsApp messages to /msg."


@app.route("/msg", methods=['POST'])
def reply():
    global schedule
    send_msg = "?"
    options = {"help": get_manual,
               "?": get_manual,
               "bitcoin": get_curr_bitcoin_value,
               "events": get_event,
               "meme": get_meme}

    for key in schedule:
        schedule[key].clear()

    rec_msg = request.form.get('Body').lower()
    resp = MessagingResponse()

    if rec_msg in options:
        send_msg = options[rec_msg]()
    else:
        for op in options:
            if SequenceMatcher(None, rec_msg, op).ratio() >= MIN_DIFF_RATIO:
                send_msg = "Did you mean {0}?".format(op)
                break

    # if rec_msg == "help" or rec_msg == "?":
    #     send_msg = get_manual()
    # elif rec_msg == "bitcoin":
    #     send_msg = get_curr_bitcoin_value()
    # elif rec_msg == "events":
    #     send_msg = get_event()

    resp.message(send_msg)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
