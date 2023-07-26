import datetime
import time

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.responses import HTMLResponse

from startup import startup_event_handler

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_event_handler("startup", startup_event_handler())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            message = await websocket.receive_bytes()
            if message == b"stop":
                await websocket.close()
                print("Connection disconnected")
                break
            # import pdb;pdb.set_trace()
            # r = sr.Recognizer()
            # with sr.AudioFile("audio.wav") as source:
            #     audio = r.listen(source)

            # google_output = recognizer.recognize_google(audio, language='en')
            google_end_time = datetime.datetime.now()
            with open("audio.wav", "wb") as file:
                file.write(message)
            # Perform transcription using the Whisper model
            whisper_output = app.model.transcribe(
                "audio.wav", task="translate"
            )
            whisper_end_time = datetime.datetime.now()
            from googletrans import Translator

            translator = Translator()
            result_hindi = translator.translate(
                whisper_output["text"], dest="hi"
            )
            result_tamil = translator.translate(
                whisper_output["text"], dest="ta"
            )
            result_chinese = translator.translate(
                whisper_output["text"], dest="zh-cn"
            )
            # Prepare the response string

            response_string = (
                f"The Whisper Model Output:\tTime Taken: {whisper_end_time - google_end_time}\n\n"
                f"{whisper_output['text']}\n\n"
                f"The Google API Output:\n"
                f"Hindi: {result_hindi.text}\n\n"
                f"Tamil: {result_tamil.text}\n\n"
                f"Chinese: {result_chinese.text}\n"
                # f"Time Taken: {google_end_time - google_start_time}\n"
            )
            import pyttsx3

            engine = pyttsx3.init()
            engine.save_to_file(whisper_output["text"], "output_speak.wav")
            engine.runAndWait()

            # Add a delay to allow time for the file to be fully saved
            time.sleep(1)
            # Send the response string through the WebSocket connection
            with open("output_speak.wav", "rb") as file:
                readfilebytes = file.read()
            import base64

            readfilebytes = base64.b64encode(readfilebytes).decode("utf-8")
            import json

            data = json.dumps(
                {"text": response_string, "audiobytes": readfilebytes}
            )
            await websocket.send_text(data)
        except KeyError:
            continue
        except Exception as e:
            await websocket.send_text(f"Unable to trancribe data, {e}")
            continue


@app.get("/")
async def get():
    return HTMLResponse(
        """
        <html>
            <body>
                <h1>WebSocket server</h1>
            </body>
        </html>
        """
    )


@app.get("/audio")
def get_audio():
    # Path to the audio file
    audio_file_path = "output.mp3"

    # Return the audio file as bytes
    return FileResponse(audio_file_path, media_type="audio/mpeg")
