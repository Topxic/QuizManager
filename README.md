# QuizManager
QuizManager is a Python script that allows users to create quizzes with a limited lifetime. Other users can participate by submitting their answers, choosing from emojis attached to each question. Once the timer finishes, the answers are collected and persisted in a connected database. Using the persisted data, statistics about players and channels can be requested.

![image](https://github.com/Topxic/QuizManager/assets/50781880/dbb6fbe7-d4b0-485a-a19e-22d66213dac2)

## Features
Create quizzes with a limited lifetime.
Participants can submit their answers by selecting emojis.
Automatic collection of answers after the timer expires.
Ability to connect to a database for data persistence.
Retrieve statistics about players and channels from the connected database.

## Installation
Clone the QuizManager repository:
```bash
git clone git@github.com:Topxic/QuizManager.git
```
Change to the project directory:
```bash
cd QuizManager
```
Install the required dependencies:
```bash
pip install -r requirements.txt
```
Create secrets file and fill with database credentials and discord bot token:
```bash
echo "DISCORD_TOKEN=<YOUR_DISCORD_TOKEN>
MYSQL_HOST=<DATABASE_URL>
MYSQL_USER=<DATABASE_USER>
MYSQL_SECRET=<DATABASE_PASSWORD>
MYSQL_DATABASE=<DATABASE_NAME>" > secrets.env
```

## Usage
To create and manage quizzes, follow these steps:

Run the QuizManager script:
```bash
python3 main.py
```
Type the help command to retreive further instructions
```bash
?help
```
Make sure to configure the channel permissions such that only administrators can create quizzes and that no furhter emojies can be added to a QuizManager message.

Once the timer for a quiz expires, the answers will be automatically collected and stored in the connected database (if configured).

If a database connection is established, you can retrieve statistics by running the appropriate commands or using the provided API endpoints.
