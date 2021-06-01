# This is a sample Python script.
import uvicorn
import time
import pyautogui
import os
import mss
import base64
from PIL import Image
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from infi.systray import SysTrayIcon

app = FastAPI()
app.mount("/img", StaticFiles(directory="static"), name="static")
config = dotenv_values(".env")
hover_text = "Holistic Snap Short Agent"


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
    with mss.mss() as mss_instance:
        monitor = mss_instance.monitors[0]
        screenshot = mss_instance.grab(monitor)
        mss_instance.shot(mon=-1, output=static_path)
    msg = {"file_name": file_name, "link": "http://localhost:{}/img/{}".format(config["SERVER_PORT"], file_name)}
    return msg


@app.get("/g/{img_name}")
def get_image(img_name: str):
    data_path = config["IMG_PATH"]
    static_path = "{}/{}".format(data_path, img_name)
    return FileResponse(static_path, media_type='image/png')


@app.get("/b64/{img_name}")
def get_image_base64(img_name: str):
    data_path = config["IMG_PATH"]
    static_path = "{}/{}".format(data_path, img_name)
    encode_img = ""
    with open(static_path, 'rb') as image:
        encode_img = base64.b64encode(image.read())

    return {"encode" : encode_img}

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


def bye(self):
    os._exit(0)


if __name__ == '__main__':
    sysTrayIcon = SysTrayIcon("HPCM.ico", hover_text,on_quit=bye)
    sysTrayIcon.start()
    uvicorn.run(app, host="127.0.0.1", port=int(config["SERVER_PORT"]), log_level="info")    
