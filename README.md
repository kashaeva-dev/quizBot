# Quiz Bots

## Overview
This project contains code for two bots: one for Telegram and another for VK (VKontakte), both designed to let people take quizzes and receive feedback on their answers.
Users can interact with the bots by answering quiz questions and receiving immediate responses based on their answers. However, as far the bots do not store user data or track user progress.
Bots just user Redis to 

## Prerequisites
Before you can use this script, you'll need to set up a few things:

### DialogFlow Setup

1. [Create a project](https://cloud.google.com/dialogflow/es/docs/quick/setup), thus you get a `project_id`.
2. [Create a DialogFlow agent](https://cloud.google.com/dialogflow/es/docs/quick/build-agent) for the `project_id` which you got earlier.
3. [Turn on API DialogFlow](https://cloud.google.com/dialogflow/es/docs/quick/setup#api) on your Google-account.
4. Get `GOOGLE_APPLICATION_CREDENTIALS` (`credentials.json`) with the help of [gcloud](https://cloud.google.com/dialogflow/es/docs/quick/setup#sdk).
5. Create DialogFlow token (How you can get it will be described below).

### Getting GOOGLE APPLICATION CREDENTIALS

To get GOOGLE_APPLICATION_CREDENTIALS (often a credentials.json file) for a Google Cloud Platform (GCP) project using the gcloud command-line tool, follow these steps:

**Install the Google Cloud SDK:**
Ensure you have the Google Cloud SDK installed on your machine. You can download and install it from the Google Cloud SDK documentation.

**Initialize the gcloud tool:**
If you haven’t already initialized the gcloud tool, open a terminal and run:

```commandline
gcloud init
```
Follow the on-screen instructions to log in with your Google account and set up your GCP environment, including selecting your project and default compute zone.

**Create a Service Account:**
You need a service account to generate the credentials file. If you don’t have one, create it using the following command:

```commandline
gcloud iam service-accounts create <service-account-name>
```
Replace <service-account-name> with a name for your service account.

**Assign Roles to the Service Account:**
Assign the necessary roles to your service account for the resources it needs to access. For example, to give it admin rights (note: you should limit the permissions to what is necessary for your application):

```commandline
gcloud projects add-iam-policy-binding <PROJECT_ID> --member="serviceAccount:<service-account-name>@<PROJECT_ID>.iam.gserviceaccount.com" --role="roles/owner"
```

Replace <PROJECT_ID> with your Google Cloud project ID and <service-account-name> with your service account name.

**Generate the Service Account Key File:**
Generate the credentials file (JSON) for your service account using the following command:

```commandline
gcloud iam service-accounts keys create ~/credentials.json --iam-account <service-account-name>@<PROJECT_ID>.iam.gserviceaccount.com
```
This command creates a credentials.json file in your home directory. Futher you will need to specify path to the credentials.json file as an enviromental variable in the .env file.

### Bots' Tokens

**Telegram Bot Token**: You'll also need a Telegram bot token.
You can create a new bot and obtain a token by talking to the [BotFather](https://t.me/BotFather) on Telegram.

**Telegram Bot Logger Token**: In addition to your main Telegram bot token,
you will need one more token for a secondary logging bot.
This additional bot dedicated to error notifications. It will receive error tracebacks ensure that
you are promptly informed of any problems.
You can obtain a token by talking to the [BotFather](https://t.me/BotFather) on Telegram.

**Chat ID**: You'll need the Chat ID of the Telegram chat where you want to receive notifications.
You can get your Chat ID by talking to the [userinfobot](https://web.telegram.org/k/#@userinfobot).

**VK API TOKEN**: To interact with a VKontakte (VK) group using the VK API, you first need to obtain a VK_API_TOKEN. Follow these steps to generate the token:

1. **Create a group in VKontakte**:
Go to the [management tab](https://vk.com/groups?tab=admin) on VK and create a new group. This group will be the one your bot interacts with.

2. **Enable message sending to the group**: Navigate to the 'Messages' tab and allow the bot to send messages to the group members.

3. **Generate the API token**: Access the 'Working with API' tab in your group’s settings. Here, you can generate the API token which your bot will use for authentication and interaction with the VK group.
Make sure to keep your VK_API_TOKEN secure and do not share it publicly to prevent unauthorized access to your VK group.


### Python Environment

Make sure you have Python installed on your system. For this project you can use python 3.6 - 3.10. 
The project has been tested with the python 3.9 version.

## Installation
1. Clone this repository:
```
git clone git@github.com:kashaeva-dev/ai_bot.git
```
2. Create virtual environment and activate it:
```bash
python -m venv env
source env/bin/activate
```
The project's functionality has been tested on Python 3.9

3. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

4. Configuration

Create a .env file in the project directory and add the following configuration variables:

```
TG_BOT_TOKEN=<your tg_bot_token>
VK_API_TOKEN=<your vk_api_token>
DF_API_TOKEN=<your api token for DialogFlow>
GOOGLE_APPLICATION_CREDENTIALS=</your/path/to/credentials.json>
TG_BOT_LOGGER_TOKEN=<your tg_bot_logger_token>
TG_CHAT_ID=<your telegram_chat_id>
DF_PROJECT_ID=<your DialogFlow project_id>
```
Replace variables with your actual data.

To obtain <your api token for DialogFlow> you should first specify `GOOGLE_APPLICATION_CREDENTIALS` and `DF_PROJECT_ID` variables. Then you can run:
```commandline
python dialog_flow/get_df_token.py
```

## Training DialogFlow Agent

To equip your bots with the capability to respond accurately to user queries,
you must first configure your DialogFlow agent. 
Follow these steps to ensure your agent can handle various user questions effectively:

1. Create Intents:

Intents are structured groups of user queries that are linked by a common theme,
along with the appropriate responses to those queries. 
For instance, you can create an intent that encompasses various ways users might ask about business hours and the corresponding answers.

Organize your questions and answers into a JSON file (e.g., `intents.json`). This file acts as a repository for the data your DialogFlow agent will use.

2. Train Your DialogFlow Agent:

To upload and process the intents from your JSON file, execute the following command in your terminal:

```commandline
python dialog_flow/dialog_flow.py
```

By default, this script reads the `intents.json` file in the project's root directory and uploads its contents to your DialogFlow agent, allowing the agent to learn and recognize these intents.
Or you can spesify path to your own JSON file when starting the `dialog_flow/dialog_flow.py` script:

```commandline
python dialog_flow/dialog_flow.py <path_to_your_json_file>
```
Specifying path to your json file is optional. By default, the path is `../intents.json`.
After uploading, you can fine-tune your intents manually on the [DialogFlow website](https://dialogflow.cloud.google.com/#/getStarted) under the Intents section to ensure they align perfectly with your desired user interactions.

## Usage

Run the script using Python:

```
python main.py
```

This script initiates two bots that are now equipped to interact with users,
providing them with the necessary information as configured in your DialogFlow agent.

You can run as well only telegram bot with the help of `--only_tg` argument or only vk bot by specifying the `--only_vk` argument.

For exemple:
```commandline
python main.py --only_tg
```

## Examples

You can try example bots:

**TELEGRAM BOT**:

[Telegram Bot with DialogFlow](https://t.me/ai_nat_bot)

User iteraction with the test telegram bot is look like:
![TelegramBot_2.gif](TelegramBot_2.gif)

**VK BOT**:

[VK Bot with DialogFlow](https://vk.com/club225378973)

User iteraction with the test vk bot is look like:
![VKBot.gif](VKBot.gif)
