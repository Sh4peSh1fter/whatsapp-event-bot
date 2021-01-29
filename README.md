# whatsapp-event-bot
A Flask api that sits on Heroku and integrates with Twilio, to create a bot for getting data such
as this weeks events related to DevOps or Cloud.

## Installation and Usage
No need to install, nor clone any file or repo.
Just send a WhatsApp message to +1 415 523 8886 with code "join through-clean":
https://wa.me/14155238886?text=join%20through-clean

After that you should get a "Twilio Sandbox: ✅ You are all set!" message from the bot.

Next, send "help" or "?" message to see what the bot is offering: 
https://wa.me/14155238886?text=help

For example, if you type "events", the bot will send you the events that take place this week in
a nice list.

## Deploy & Setup Your Own Bot
If you want to deploy your own bot, you should do the following steps:
* Clone this repo.
```
git clone https://github.com/Sh4peSh1fter/whatsapp-event-bot.git
```
* Next step is to decide if you want to run the flask api on your computer or to run it on heroku.

To deploy this on heroku, install the Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli),
and run the following commands one by one in the repo folder:
```
pip freeze > requirements.txt
heroku login
heroku create your-app-name
git push heroku your-main-branch:main
```
Else, you can use ngrok to run it locally - after you install it of course (https://ngrok.com/download).
instead of "5000", type your flask port:
```
ngrok http 5000
```

* Last step is to involve twilio. In your twilio project, go to "Twilio Sandbox for WhatsApp" under
"Settings". There enter the URL to webhook to when messages are coming (The field called "WHEN A MESSAGE COMES IN
"). For me it was:
```
https://whatsapp-event-bot.herokuapp.com//msg
```

Thats it! Have fun :)

