# This is a sample Python script.
import uvicorn
import time
import pyautogui
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/img", StaticFiles(directory="static"), name="static")
config = dotenv_values(".env")


origins = [
    "{}".format(config["CORS_HTTP_URL"]),
    "{}".format(config["CORS_HTTPS_URL"]),
    "{}:{}".format(config["CORS_HTTP_URL"], config["CORS_PORT"]),
    "{}:{}".format(config["CORS_HTTPS_URL"], config["CORS_PORT"]),
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def alive():
    return {"version": config["VERSION"]}


@app.get("/snap")
def screen_capture():
    file_name = "{}{}".format((round(time.time() * 1000)), ".png")
    data_path = config["IMG_PATH"]
    static_path = "{}/{}".format(data_path, file_name)
    image = pyautogui.screenshot()
    image.save(static_path)
    msg = {"file_name": file_name, "link": "http://localhost:{}/img/{}".format(config["SERVER_PORT"], file_name)}
    return msg


def delete_files_older():
    deleted_files_count = 0
    days = int(config["IMG_DAY_TMP"])
    seconds = time.time() - (days * 24 * 60 * 60)
    path = config["IMG_PATH"]

    if os.path.exists(path):
        for root_folder, folders, files in os.walk(path):

            for file in files:
                file_path = os.path.join(root_folder, file)

                if seconds >= get_file_or_folder_age(file_path):
                    remove_file(file_path)
                    deleted_files_count += 1
    return deleted_files_count


def remove_file(path):
    if not os.remove(path):
        print(f"{path} is removed successfully")
    else:
        print(f"Unable to delete the {path}")


def get_file_or_folder_age(path):
    ctime = os.stat(path).st_ctime
    return ctime


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("images older than {} days will be removed".format(config["IMG_DAY_TMP"]))
    print("images is removed: {}".format(delete_files_older()))
    uvicorn.run("main:app", host="127.0.0.1", port=int(config["SERVER_PORT"]), log_level="info")
