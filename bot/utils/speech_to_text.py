import datetime
import json

import bot.Database.database as db
import requests
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.audio_summarizer import text_from_file


def gen_new_token(AUTH_DATA, API_SCOPE) -> str:  # returning the token
    new_random_id = uuid.uuid4()
    auth_data = AUTH_DATA
    scope = API_SCOPE
    headers = {
        "Authorization": f"Basic {auth_data}",
        "RqUID": f"{new_random_id}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": f"{scope}"}
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    response = requests.post(url=url, headers=headers, data=data, verify=False)
    token = response.json()["access_token"]
    return token


async def get_new_token(
    AUTH_DATA, API_SCOPE, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # here add the user data, and
    token = ""
    user_Id = update.effective_user.id
    user_Name = update.effective_user.first_name
    username = update.effective_user.username
    if db.checking_user_exits(user_Id):
        if db.checking_last_gen_time(
            user_Id
        ):  # the time is more than 30 min, so we get a token
            token = gen_new_token(API_SCOPE=API_SCOPE, AUTH_DATA=AUTH_DATA)
            # update the token stored
            db.User.update(usertoken=token).where(db.User.userid == user_Id).execute()
        elif not db.checking_last_gen_time(user_Id):  # case when the time to
            token = db.User.get(db.User.userid == user_Id).usertoken
            return token

    else:
        token = gen_new_token(API_SCOPE=API_SCOPE, AUTH_DATA=AUTH_DATA)
        now = datetime.datetime.now()
        # create the user call the token and save it in db
        db.User.create(
            userid=user_Id,
            name=user_Name,
            username=username,
            chromacollection="",
            usertoken=token,
            lastgen=now,
        )

    return token  # getting the token correctly


async def speech_to_text(
    filename, TOKEN
):  # maybe its not getting converted as no file extension?
    filepath = filename  # we have the file
    file = open(filepath, "rb")  # getting the file to read
    url = "https://smartspeech.sber.ru/rest/v1/data:upload"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = file.read()
    response = requests.post(url=url, data=data, headers=headers, verify=False)
    # print(response.json())  working so I am commenting it out
    # print(filepath)
    return str(
        response.json()["result"]["request_file_id"]
    )  # correctly returning the file_id


async def speech_recognition_task(fileId, Token):  # Now to get the task done
    url = "https://smartspeech.sber.ru/rest/v1/speech:async_recognize"
    headers = {"Authorization": f"Bearer {Token}", "Content-Type": "application/json"}

    data = {
        "options": {
            "language": "ru-RU",
            "audio_encoding": "MP3",
            "no_speech_timeout": "8s",
            "max_speech_timeout": "20s",
        },
        "request_file_id": f"{fileId}",
    }

    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, verify=False
    )
    print(json.dumps(data))  # working so commenting it out
    print(response.json())  # working
    return str(response.json()["result"]["id"])  # correctly returning the taskid


async def speech_recognition_task_voice(fileId, Token):  # Now to get the task done
    url = "https://smartspeech.sber.ru/rest/v1/speech:async_recognize"
    headers = {"Authorization": f"Bearer {Token}", "Content-Type": "application/json"}

    data = {
        "options": {
            "language": "ru-RU",
            "audio_encoding": "OPUS",
        },
        "request_file_id": f"{fileId}",
    }

    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, verify=False
    )
    # print(json.dumps(data)) working
    # print(response.json())  working
    return str(response.json()["result"]["id"])  # correctly returning the taskid


# {  sample result for the task creating
#     "status": 200,
#     "result": {
#         "id": "dafaf982-a32a-4e26-ae40-2bb9444906e1",
#         "created_at": "2021-07-15T17:35:17.182454861+03:00",
#         "updated_at": "2021-07-15T17:35:17.18245504+03:00",
#         "status": "NEW"
#     }
# }


async def get_task_status(fileId, Token):  # Now to get the task done
    url = f"https://smartspeech.sber.ru/rest/v1/task:get?id={fileId}"
    headers = {"Authorization": f"Bearer {Token}"}
    response = requests.get(url=url, headers=headers, verify=False)
    print(response.json())  # working
    return response.json()["result"]["response_file_id"]
    # correctly returning the taskid


async def get_the_text(fileId, Token):  # Now to get the task done
    url = f"https://smartspeech.sber.ru/rest/v1/data:download?response_file_id={fileId}"
    headers = {"Authorization": f"Bearer {Token}"}
    response = requests.get(url=url, headers=headers, verify=False)
    print(response.json())  # result will have the
    data = response.json()
    with open("response.json", "w+") as f:
        json.dump(data, f)
    f.close()
    text = await text_from_file(f)
    print(text)
    return str(response.json()[0]["results"][0]["text"])


# TODO: Antiplagiarism detection? Sending result to email? RAG Pipeline?