"""
SeaVoice Speech SDK

Descriptions:
To connect to SeaVoice STT & TTS server to finish speech recognizing and synthesizing work.
"""


from typing import (
    Optional,
    Dict,
    Callable,
    Text
)
import websockets
from ws4py.client.threadedclient import WebSocketClient
import websocket
import urllib
import asyncio
from seavoice_sdk import audio
import threading
import json
import warnings
from seavoice_sdk import logger

import base64
import hashlib
import hmac
import os
import ssl
import time
import _thread as thread
import enum
import io
from seavoice_sdk.utils import Wave
import requests

# used by SlothWebsocketParam
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode
from datetime import datetime
from time import mktime

svc_logger = logger.get_SVCLogger(__name__)

API_SERVER_LOGIN_URL = "https://suite.seasalt.ai/api/v1/user/login"
API_SERVER_TTS_SERVICE_URL = "https://suite.seasalt.ai/api/v1/speech/text_to_speech"
API_SERVER_STT_SERVICE_URL = "https://suite.seasalt.ai/api/v1/speech/stt_server_url"
API_SERVER_STT_SERVICE_URL_TOKEN = "https://suite.seasalt.ai/api/v1/speech/speech_to_text"

SUPPORTED_AUDIO_FORMAT = {
    'riff-8khz-16bit-mono-pcm': {
        "sample_rate": 8000,
        "sample_width": 2,
        "channels": 1
    },
    'riff-16khz-16bit-mono-pcm': {
        "sample_rate": 16000,
        "sample_width": 2,
        "channels": 1
    },
    'riff-22khz-16bit-mono-pcm': {
        "sample_rate": 22050,
        "sample_width": 2,
        "channels": 1
    }
}
ERROR_IN_SEND_THREAD = 11000


class SpeechConfig():
    """ Setup speech arguments """

    def __init__(
        self,
        host: Optional[Text] = '',
        account_id: Text = '',
        password: Text = '',
        apikey: Text = '',
        speech_recognition_language: Text = 'zh-TW',
        speech_recognition_punctuation: bool = False,
        speech_synthesis_language: Text = 'zh-TW',
        speech_synthesis_voice_name: Text = 'Lin_Xiaomei',
        speech_synthesis_output_format_id: Text = 'riff-16khz-16bit-mono-pcm',
        speech_synthesis_output_pitch: int = 0.0,
        speech_synthesis_output_speed: int = 1.0
    ):
        """Init speech arguments"""
        self.__host = host
        self.__account_id = account_id
        self.__password = password
        self.__apikey = apikey
        self.__speech_recognition_language = speech_recognition_language
        self.__speech_recognition_punctuation = speech_recognition_punctuation
        self.__speech_synthesis_language = speech_synthesis_language
        self.__speech_synthesis_voice_name = speech_synthesis_voice_name
        try:
            self.__speech_synthesis_output_format = SUPPORTED_AUDIO_FORMAT[speech_synthesis_output_format_id]
        except KeyError:
            raise ValueError("Unavailable format id")
        self.__speech_synthesis_output_format_id = speech_synthesis_output_format_id
        self.__speech_synthesis_format_label = 'X-SeasaltAI-OutputFormat'
        self.__speech_synthesis_output_pitch = speech_synthesis_output_pitch
        self.__speech_synthesis_output_speed = speech_synthesis_output_speed

    @property
    def host(self) -> Text:
        """Return host"""
        return self.__host

    @property
    def account_id(self) -> Text:
        """Return account_id"""
        return self.__account_id

    @property
    def password(self) -> Text:
        """Return password"""
        return self.__password

    @property
    def apikey(self) -> Text:
        """Return apikey"""
        return self.__apikey

    @property
    def format_label(self) -> Text:
        """Return format label"""
        return self.__speech_synthesis_format_label

    @property
    def seavoice_format_label(self) -> Text:
        """Return format lable"""
        return self.__speech_synthesis_format_label

    @property
    def speech_synthesis_output_format(self) -> Dict:
        """Return speech synthesis output format"""
        return self.__speech_synthesis_output_format

    @property
    def speech_recognition_language(self) -> Optional[Text]:
        """Return recognition language"""
        return self.__speech_recognition_language

    @speech_recognition_language.setter
    def speech_recognition_language(self, language: Text) -> None:
        """Set recognition language"""
        self.__speech_recognition_language = language

    @property
    def speech_recognition_punctuation(self) -> Optional[Text]:
        """Return recognition punctuation"""
        return self.__speech_recognition_punctuation

    @speech_recognition_punctuation.setter
    def speech_recognition_punctuation(self, punctuation: bool) -> None:
        """Set recognition punctuation"""
        self.__speech_recognition_punctuation = punctuation

    @property
    def speech_synthesis_language(self) -> Optional[Text]:
        """Return synthesis language"""
        return self.__speech_synthesis_language

    @speech_synthesis_language.setter
    def speech_synthesis_language(self, language: Text) -> None:
        """Set synthesis language"""
        self.__speech_synthesis_language = language

    @property
    def speech_synthesis_voice_name(self) -> Optional[Text]:
        """Return voice name"""
        return self.__speech_synthesis_voice_name

    @speech_synthesis_voice_name.setter
    def speech_synthesis_voice_name(self, voice_name: Text) -> None:
        """Set voice name"""
        self.__speech_synthesis_voice_name = voice_name

    @property
    def speech_synthesis_output_format_id(self) -> Text:
        """Return output format id"""
        return self.__speech_synthesis_output_format_id

    @speech_synthesis_output_format_id.setter
    def speech_synthesis_output_format_id(self, format_id: Text) -> None:
        """Set output format id"""
        try:
            self.__speech_synthesis_output_format = SUPPORTED_AUDIO_FORMAT[format_id]
        except KeyError:
            raise ValueError("Unavailable format id")
        self.__speech_synthesis_output_format_id = format_id

    @property
    def speech_synthesis_output_pitch(self) -> int:
        """Return output pitch"""
        return self.__speech_synthesis_output_pitch

    @speech_synthesis_output_pitch.setter
    def speech_synthesis_output_pitch(self, pitch: int) -> None:
        """Set output pitch"""
        self.__speech_synthesis_output_pitch = pitch

    @property
    def speech_synthesis_output_speed(self) -> int:
        """Return output speed"""
        return self.__speech_synthesis_output_speed

    @speech_synthesis_output_speed.setter
    def speech_synthesis_output_speed(self, speed: int) -> None:
        """Set output speed"""
        self.__speech_synthesis_output_speed = speed

    def get_login_token(self) -> bool:
        """login on api server, get login token"""
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(API_SERVER_LOGIN_URL, headers=headers, json={'account_id': self.__account_id, 'password': self.__password})
        if response.status_code == 200:
            self.login_token = response.json()['token']
            return True
        else:
            svc_logger.error(f"Login error: {response.status_code} for account_id: {self.__account_id}")
            return False

    def enable_audio_logging(self):
        """Enable audio loggin"""
        pass


class Recognizer(WebSocketClient):
    """Base class of recognizer"""

    def __init__(
        self,
        speech_config: SpeechConfig,
        audio_config: Optional[audio.AudioConfig] = None
    ):
        """Initialize speech recognizer"""
        # load speech_config
        self.__speech_config = speech_config
        self.__account_id = speech_config.account_id
        self.__format_label = speech_config.format_label
        self.__speech_recognition_language = speech_config.speech_recognition_language
        self.__speech_recognition_punctuation = speech_config.speech_recognition_punctuation
        self.__recognizer_semaphore = threading.Semaphore(0)

        if not speech_config.apikey:
            if speech_config.get_login_token() is False:
                svc_logger.error(f"Failed to login API server for {self.__account_id}, please make sure account_id and password are right.")
                return None
            self.__login_token = speech_config.login_token

            # get an available stt server url and speech token
            if self.get_server_url_token() is False:
                svc_logger.error(f"Can't get an available stt server and speech token, please confirm language setting, then try again.")
                return None
        else:
            self.__token = speech_config.apikey
            if self.get_server_url() is False:
                svc_logger.error(f"Can't get an available stt server, please confirm language setting, then try again.")
                return None
        self.__ws_uri = f"{self.__host}?token={self.__token}&punctuation={self.__speech_recognition_punctuation}"

        # load audio_config
        self.__input_stream = None
        self.__content_type = None
        self.__audio_config = audio_config
        self.__input_filename = None
        self.__recognize_once = False
        if audio_config is not None:
            if audio_config.stream is not None:
                self.__input_stream = audio_config.stream
                self.__content_type = urllib.parse.urlencode(
                    [
                        ("content-type", self.__input_stream.stream_format.content_type)
                    ]
                )
            elif audio_config.filename is not None:
                self.__input_filename = audio_config.filename
        if self.__content_type is not None:
            self.__ws_uri += f"&{self.__content_type}"
        self.is_running = False

        # create events
        self.__session_started_event = EventSignal()
        self.__session_stopped_event = EventSignal()
        self.__recognizing_event = EventSignal()
        self.__recognized_event = EventSignal()
        self.__canceled_event = EventSignal()
        self.session_id = None

        # init websocket client
        super().__init__(url=self.__ws_uri)

    def get_server_url_token(self) -> bool:
        """get stt server url and speech token by login token"""
        headers = {'Content-Type': 'text/plain', 'token': self.__login_token}
        response = requests.post(API_SERVER_STT_SERVICE_URL_TOKEN, headers=headers,
                                 json={'language': self.__speech_recognition_language})
        if response.status_code == 200:
            response_json = response.json()
            self.__host = response_json['server_url']
            self.__token = response_json['token']
            return True
        else:
            svc_logger.error(f"Error while getting stt server url and token: {response.status_code} for account_id: {self.__account_id}")
            return False

    def get_server_url(self) -> bool:
        """get stt server url by apikey"""
        headers = {'Content-Type': 'text/plain', 'speech_token': self.__token}
        url = f"{API_SERVER_STT_SERVICE_URL}?language={self.__speech_recognition_language}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            self.__host = response_json['server_url']
            return True
        else:
            svc_logger.error(f"Error while getting stt server url: {response.status_code} for account_id: {self.__account_id}")
            return False

    def recognize_once(self):
        """recognize once"""
        self.connect()
        if self.__input_filename is None:
            raise RuntimeError("No filename provided!")
        self.__recognize_once = True
        with open(self.__input_filename, "rb") as wav:
            while True:
                frame = 4000
                frame_data = wav.read(frame)
                if len(frame_data) == 0:
                    break
                self.send(frame_data, binary=True)
            self.send("EOS")

    def start_continuous_recognition_async(self):
        """Start continuous speech recognition in asynchronized way"""
        self.is_running = True
        self.connect()
        recognition_thread = threading.Thread(
            target=self.send_thread,
        )
        recognition_thread.daemon = True
        recognition_thread.start()

    def start_continuous_recognition(self):
        """Start continuous speech recognition in synchronized way"""
        self.start_continuous_recognition_async()
        self.__recognizer_semaphore.acquire()

    def thread_start_continuous_recognition_async(self):
        """
        Start a thread to start continuous recognition

        Deprecated: this is used for websockets, but since it has the issue of ws.send(), we changed to use ws4py.
        See coninuous_recognition_async for more info.
        """
        warnings.warn("Deprecated: websockets has the issue of sending data", DeprecationWarning)
        self.seavoice_stt_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.seavoice_stt_loop)
        try:
            self.seavoice_stt_loop.run_until_complete(
                self.await_continuous_recognition_async()
            )
        except Exception as e:
            svc_logger.error(
                f"Exception in thread_start_continuous_recognition_async: {e}"
            )
        finally:
            self.seavoice_stt_loop.close()

    async def await_continuous_recognition_async(self):
        """
        Wait results of continuous recognition

        Deprecated: this is used for websockets, but since it has the issue of ws.send(), we changed to use ws4py.
        See coninuous_recognition_async for more info.
        """
        warnings.warn("Deprecated: websockets has the issue of sending data", DeprecationWarning)
        await self.continuous_recognition_async()

    async def continuous_recognition_async(self):
        """
        Connect seavoice stt server by websocket

        Start a thread to send data to seavoice stt server
        Wait recognized results

        Deprecated: this is used for websockets, but when test, if started a new thread running coninuous_recognition_async
        in on_event_start in twilio_voice.py, from logs of seavoice stt server, ws.send() doesn't send package in real time.
        It sent the first package after about 2 seconds, then sent other packages continuously.
        After changed to use ws4py client, logs of stt server show sending packages is right. So we changed to use ws4py.

        """
        warnings.warn("Deprecated: websockets has the issue of sending data", DeprecationWarning)
        try:
            async with websockets.client.connect(self.__ws_uri) as ws:
                if self.__session_started_event.is_set:
                    # Not sure how to get session id on websocket starting
                    # the handshake response header is set in evt id
                    evt = {"id": f"{ws.response_headers}"}
                    evt_res = EventResults(evt)
                    self.__session_started_event.callback(evt_res)
                if self.__input_stream is not None:
                    thread_send = threading.Thread(target=self.send, args=(ws,))
                    thread_send.start()
                    await self.receive(ws)
            if self.__session_stopped_event.is_set:
                evt = {"session_id": self.session_id}
                evt_res = EventResults(evt)
                self.__session_stopped_event.callback(evt_res)
        except Exception as e:
            svc_logger.error(f"Exception in continuous_recognition_async: {e}")

    def opened(self):
        """Open websocket"""
        svc_logger.info("websocket opened")
        if self.__session_started_event.is_set:
            evt = {"session_id": self.session_id, "status": 0, "message": "recognition started"}
            evt_res = EventResults(evt)
            self.__session_started_event.callback(evt_res)

    def closed(self, code, reason):
        """Close websocket"""
        svc_logger.info(f"Closed down: {code}, {reason}")
        if self.__session_stopped_event.is_set:
            evt = {"session_id": self.session_id, "status": code, "messge": reason}
            evt_res = EventResults(evt)
            self.__session_stopped_event.callback(evt_res)
        self.close()

    def send_thread(self):
        """Send data to websocket"""
        error_flag = False
        while self.is_running:
            try:
                if self.__input_stream is not None:
                    buf = self.__input_stream.read_wait()
                    if buf is not None and len(buf) > 0:
                        self.send(buf, binary=True)
            except KeyboardInterrupt:
                error_flag = True
                self.stop_continuous_recognition_async()
            except Exception as e:
                svc_logger.error(f"Exception in send_thread: {e}")
                error_flag = True
                self.stop_continuous_recognition_async()
        try:
            # inform server that client has finished sending all audio data
            self.send("EOS")
        except Exception:
            # if can't send 'EOS' to server, actively close websocket connection with server
            error_flag = True
            self.close()
        finally:
            if error_flag:
                if self.__canceled_event.is_set:
                    evt = {"session_id": self.session_id, "status": ERROR_IN_SEND_THREAD, "messge": "Error while sending data to server"}
                    evt_res = EventResults(evt)
                    self.__canceled_event.callback(evt_res)

    def received_message(self, message) -> None:
        """Receive result from websocket"""
        try:
            evt = json.loads(str(message))
            if 'id' in evt:
                self.session_id = evt['id']
            if evt['status'] == 0:
                if 'result' in evt:
                    if evt['result']['final']:
                        if self.__recognized_event.is_set:
                            evt_res = EventResults(evt)
                            self.__recognized_event.callback(evt_res)
                            if self.__recognize_once is True:
                                self.__recognize_once = False
                                self.close()
                    else:
                        if self.__recognizing_event.is_set:
                            evt_res = EventResults(evt)
                            self.__recognizing_event.callback(evt_res)
            else:
                if 'message' in evt:
                    evt['message'] = "Received error from server: " + f"{evt['message']}"
                else:
                    evt['message'] = "Got error from server."
                raise RuntimeError(evt)
        except Exception as e:
            svc_logger.error(f"Exception in receive_message: {evt}")
            if self.__canceled_event.is_set:
                evt_res = EventResults(evt)
                self.__canceled_event.callback(evt_res)
            self.stop_continuous_recognition_async()

    def stop_continuous_recognition_async(self):
        """Stop recognition"""
        self.is_running = False
        self.__input_stream.close()

    def stop_continuous_recognition(self):
        """Stop recognition"""
        self.stop_continuous_recognition_async()
        self.__recognizer_semaphore.release()

    @property
    def speech_config(self) -> SpeechConfig:
        """Return speech config"""
        return self.__speech_config

    @property
    def audio_config(self) -> Optional[audio.AudioConfig]:
        """Return audio config"""
        return self.__audio_config

    @property
    def format_label(self) -> Text:
        """Return format lable"""
        return self.__format_label

    @property
    def myhost(self) -> Text:
        """Return host"""
        return self.__host

    @property
    def speech_recognition_language(self) -> Optional[Text]:
        """Return recognition language"""
        return self.__speech_recognition_language

    @property
    def session_started(self):
        """Return session started event"""
        return self.__session_started_event

    @property
    def session_stopped(self):
        """Return session stopped event"""
        return self.__session_stopped_event

    @property
    def speech_start_detected(self):
        """Return start detected"""
        raise NotImplementedError

    @property
    def speech_end_detected(self):
        """Return end detected"""
        raise NotImplementedError

    @property
    def recognizing(self):
        """Return Recognizing event"""
        return self.__recognizing_event

    @property
    def recognized(self):
        """Return recognized event"""
        return self.__recognized_event

    @property
    def canceled(self):
        """Return canceled event"""
        return self.__canceled_event


class SpeechRecognizer(Recognizer):
    """Speech recognize"""

    def __init__(
        self,
        speech_config: SpeechConfig,
        audio_config: Optional[audio.AudioConfig] = None
    ):
        """Initialze speech recognizer"""
        super().__init__(
            speech_config=speech_config,
            audio_config=audio_config
        )


class EventBase():
    """Base class for events"""

    def __init__(self):
        """Init event base"""
        self.callback = None
        self.__is_set = False

    def connect(self, callback: Callable):
        """
        Connects given callback function to the event signal, to be invoked when the
        event is signalled.
        """
        self.callback = callback
        self.__is_set = True

    @property
    def is_set(self):
        """Return if a callback is set"""
        return self.__is_set


class EventSignal(EventBase):
    """
    Clients can connect to the event signal to receive events, or disconnect from
    the event signal to stop receiving events.
    """

    def __init__(self):
        """Initialze the event"""
        super().__init__()


class EventResults():
    """Simulate MS SessionEventArgs class"""

    def __init__(self, evt):
        """Init event results"""
        self.status = None
        self.segment = None
        self.result = None
        self.session_id = None
        self.segment_start = None
        self.segment_length = None
        self.total_length = None
        self.message = None

        if "status" in evt:
            self.status = evt.get("status")
        if "segment" in evt:
            self.segment = evt.get("segment")
        if "result" in evt:
            self.result = Results(evt.get("result"))
        if "id" in evt:
            self.session_id = evt.get("id")
        if 'segment-start' in evt:
            self.segment_start = evt.get("segment-start")
        if 'segment-length' in evt:
            self.segment_length = evt.get("segment-length")
        if 'total-length' in evt:
            self.total_length = evt.get("total-length")
        if 'message' in evt:
            self.message = evt.get("message")

    def __str__(self):
        """Return event info"""
        return (
            f"status={self.status}, "
            f"segment={self.segment}, "
            f"result=({self.result}), "
            f"session_id={self.session_id}, "
            f"message={self.message}"
        )


class Results():
    """Simulate MS SpeechRecognitionEventArgs class"""

    def __init__(self, results):
        """Initialize results"""
        self.result_id = None
        self.text = None
        self.displaytext = None
        self.reason = None
        self.final = None
        self.word_alignment = None

        if 'result_id' in results:
            self.result_id = None
        if 'hypotheses' in results:
            self.text = results['hypotheses'][0]['transcript']
            if 'word-alignment' in results['hypotheses'][0]:
                self.word_alignment = results['hypotheses'][0]['word-alignment']
            if 'displaytext' in results['hypotheses'][0]:
                self.displaytext = results['hypotheses'][0]['displaytext']
        if 'reason' in results:
            self.reason = None
        if 'final' in results:
            self.final = results['final']

    def __str__(self):
        """Return result info"""
        return (
            f"result_id={self.result_id}, "
            f"text={self.text}, "
            f"reason={self.reason}, "
            f"final={self.final}"
        )


class ResultReason(enum.Enum):
    ResultReason_Canceled = 9
    ResultReason_SynthesizingAudioStarted = 10
    ResultReason_SynthesizingAudio = 11
    ResultReason_SynthesizingAudioCompleted = 12


class SpeechSynthesisResult():
    """
    Result of a speech synthesis operation.
    """

    def __init__(
            self,
            audio,
            reason,
            result_id=None,
            cancellation_details=None
    ):
        """
        Constructor for SpeechSynthesisResult.
        """
        self._cancellation_details = cancellation_details
        self._result_id = result_id
        self._reason = reason
        self._audio_data = audio

    @property
    def cancellation_details(self) -> str:
        """
        The reason why speech synthesis was cancelled.

        Returns `None` if there was no cancellation.
        """
        return self._cancellation_details

    @property
    def result_id(self) -> str:
        """
        Synthesis result unique ID.
        """
        return self._result_id

    @property
    def reason(self) -> ResultReason:
        """
        Synthesis reason.
        """
        return self._reason

    @property
    def audio_data(self) -> bytes:
        """
        The output audio data from the TTS.
        """
        return self._audio_data

    def __str__(self):
        return u'{}(result_id={}, reason={}, audio_length={})'.format(
            type(self).__name__, self._result_id, self._reason, len(self._audio_data))


class ResultFuture():
    """
    The result of an asynchronous operation.
    """
    def __init__(self, client):
        """
        constructor
        """
        self.__client = client

    def get(self) -> SpeechSynthesisResult:
        """
        Waits until the result is available, and returns it.
        """
        self.__client.semaphore.acquire()
        return self.__client.speech_synthesis_result


class SlothWebsocketParam(object):
    def __init__(self, speech_config: SpeechConfig, token, text, is_ssml):
        self.business_args = {
            "language": speech_config.speech_synthesis_language,
            "voice": speech_config.speech_synthesis_voice_name,
            "token": token
        }
        self.settings_args = {
            "pitch": speech_config.speech_synthesis_output_pitch,
            "speed": speech_config.speech_synthesis_output_speed,
            "sample_rate": speech_config.speech_synthesis_output_format['sample_rate'],
        }
        self.data = {"text": str(base64.b64encode(text.encode('utf-8')), "UTF8"),
                     "ssml": is_ssml}


class SlothWebsocketClient():
    def __init__(
            self,
            speech_config: SpeechConfig,
            output_stream=None,
            output_filename=None
    ):
        websocket.enableTrace(False)
        self.__speech_config = speech_config
        ws = websocket.WebSocketApp("",
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws = ws
        self.ws.on_open = self.on_open
        self.__audio_buf = io.BytesIO()
        self.__running = True
        self.speech_synthesis_result = None
        self.semaphore = threading.Semaphore(0)
        self.__output_stream = output_stream
        self.__output_filename = output_filename

    def save_wav_file(self, audio_pcm, filename):
        audio = Wave(filename, 'wb')
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(self.__speech_config.speech_synthesis_output_format['sample_rate'])
        audio.writeframes(audio_pcm)
        audio.close()

    def sloth_speak_text(self,
                         host: str,
                         token: str,
                         input_text: str,
                         is_ssml='False'):
        self.ws_param = SlothWebsocketParam(speech_config=self.__speech_config,
                                            token=token,
                                            text=input_text, is_ssml=is_ssml)
        self.ws.url=host
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.__audio_buf.seek(0)
        audio_data = self.__audio_buf.read()
        self.speech_synthesis_result = SpeechSynthesisResult(
            audio_data,
            ResultReason.ResultReason_SynthesizingAudioCompleted
        )
        if self.__output_stream is not None:
            self.__output_stream.write(audio_data)
        if self.__output_filename is not None:
            self.save_wav_file(audio_data, self.__output_filename)
        self.semaphore.release()
        return self.speech_synthesis_result

    def sloth_speak_text_async(self,
                               host: str,
                               token: str,
                               input_text: str,
                               is_ssml='False'):
        task_speak = threading.Thread(
            target=self.sloth_speak_text,
            args=(host, token, input_text, is_ssml)
        )
        task_speak.daemon = True
        task_speak.start()
        return ResultFuture(self)

    def on_message(self, message):
        try:
            message = json.loads(message)
            status = message["status"]
            progress = message["progress"]
            sid = message["sid"]
            if status is not "ok":
                svc_logger.info(f"Sloth websocket: sid: {sid}; status: {status}; progress:{progress}.")

            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            ending_status = message["data"]["status"]
            if ending_status == 2:
                self.__audio_buf.write(audio)
                self.ws.close()
                #self.__running = False # comment out on 2021/7/27, to support calling speak_text multiple times, with this, sdk will only call synthesizing callback for the first text

                if self.synthesis_completed is not None:
                    if self.synthesis_completed.is_set is True:
                        self.synthesis_completed.callback(audio)

                svc_logger.info("Sloth websocket: ws is closed")
            else:
                if self.__running is True:
                    self.__audio_buf.write(audio)

                    if self.synthesizing is not None:
                        if self.synthesizing.is_set is True:
                            self.synthesizing.callback(audio)

        except Exception as e:
            svc_logger.error(f"Sloth websocket exception: {e}")

    def on_error(self, error):
        if self.synthesis_canceled is not None:
            if self.synthesis_canceled.is_set is True:
                self.synthesis_canceled.callback()
        svc_logger.error(f"Sloth websocket error: {error}")

    def on_close(self):
        svc_logger.info("Sloth websocket: closed.")

    def on_open(self):
        def run(*args):
            data = {"business": self.ws_param.business_args,
                    "settings": self.ws_param.settings_args,
                    "data": self.ws_param.data,
            }
            data = json.dumps(data)
            svc_logger.info(f"Sloth websocket: start sending data: {data}")
            self.ws.send(data)

        if self.synthesis_started is not None:
            if self.synthesis_started.is_set is True:
                self.synthesis_started.callback()

        thread.start_new_thread(run, ())


class SpeechSynthesizer(SlothWebsocketClient):
    """
    A speech synthesizer.

    :param speech_config: The config for the speech synthesizer
    :param audio_config: The config for the audio output.
        This parameter is optional.
        If it is not provided, the default speaker device will be used for audio output.
        If it is None, the output audio will be dropped.
        None can be used for scenarios like performance test.
    """
    def __init__(
            self,
            speech_config: SpeechConfig,
            audio_config: Optional[audio.AudioOutputConfig] = None
    ):
        """Initialize speech recognizer"""
        if not isinstance(speech_config, SpeechConfig):
            raise ValueError('speech_config must be a SpeechConfig instance')

        # load speech_config
        self.__speech_config = speech_config
        self.__format_label = speech_config.format_label
        self.__account_id = speech_config.account_id
        if speech_config.get_login_token() is False:
            svc_logger.error(f"Failed to login API server for {self.__account_id}, please make sure account_id and password are right.")
            return None
        self.__login_token = speech_config.login_token
        self.__speech_synthesis_language = speech_config.speech_synthesis_language
        self.__speech_synthesis_voice_name = speech_config.speech_synthesis_voice_name
        self.__speech_synthesis_output_format_id = speech_config.speech_synthesis_output_format_id

        # load audio_output_config
        self.__output_stream = None
        self.__audio_config = audio_config
        self.__output_filename = None
        if audio_config is not None:
            if audio_config.stream is not None:
                self.__output_stream = audio_config.stream
            elif audio_config.filename is not None:
                self.__output_filename = audio_config.filename
        self.is_running = False

        # create events
        self.__synthesis_started_event = EventSignal()
        self.__synthesizing_event = EventSignal()
        self.__synthesis_completed_event = EventSignal()
        self.__synthesis_canceled_event = EventSignal()
        self.session_id = None

        # init sloth websocket client
        super().__init__(self.__speech_config, self.__output_stream, self.__output_filename)

    def get_server_url_token(self) -> bool:
        """get tts server url and speech token by login token"""
        headers = {'Content-Type': 'text/plain', 'token': self.__login_token}
        response = requests.post(API_SERVER_TTS_SERVICE_URL, headers=headers,
                                 json={'language': self.__speech_synthesis_language, 'voice': self.__speech_synthesis_voice_name})
        if response.status_code == 200:
            response_json = response.json()
            self.__host = response_json['server_url']
            self.__token = response_json['token']
            return True
        else:
            svc_logger.error(f"Error while getting tts server and token: {response.status_code} for account_id: {self.__account_id}")
            return False

    def speak_text(self, text: str) -> Optional[SpeechSynthesisResult]:
        """
        Performs synthesis on plain text in a blocking (synchronous) mode.

        :return: A SpeechSynthesisResult.
        """
        if self.get_server_url_token() is True:
            return super().sloth_speak_text(self.__host, self.__token, text, is_ssml='False')
        else:
            svc_logger.error(f"Can't get an available tts server, please confirm language and voice settings, then try again.")
            return None

    def speak_ssml(self, ssml: str) -> Optional[SpeechSynthesisResult]:
        """
        Performs synthesis on ssml in a blocking (synchronous) mode.

        :return: A SpeechSynthesisResult.
        """
        if self.get_server_url_token() is True:
            return super().sloth_speak_text(self.__host, self.__token, ssml, is_ssml='True')
        else:
            svc_logger.error(f"Can't get an available tts server, please confirm language and voice settings, then try again.")
            return None

    def speak_text_async(self, text: str) -> Optional[ResultFuture]:
        """
        Performs synthesis on plain text in a non-blocking (asynchronous) mode.

        :return: A future with SpeechSynthesisResult.
        """
        if self.get_server_url_token() is True:
            return super().sloth_speak_text_async(self.__host, self.__token, text, is_ssml='False')
        else:
            svc_logger.error(f"Can't get an available tts server, please confirm language and voice settings, then try again.")
            return None

    def speak_ssml_async(self, ssml: str) -> Optional[ResultFuture]:
        """
        Performs synthesis on ssml in a non-blocking (asynchronous) mode.

        :return: A future with SpeechSynthesisResult.
        """
        if self.get_server_url_token() is True:
            return super().sloth_speak_text_async(self.__host, self.__token, ssml, is_ssml='True')
        else:
            svc_logger.error(f"Can't get an available tts server, please confirm language and voice settings, then try again.")
            return None

    def start_speaking_text(self, text: str) -> SpeechSynthesisResult:
        """
        Starts synthesis on plain text in a blocking (synchronous) mode.

        :return: A SpeechSynthesisResult.
        """
        raise NotImplementedError

    def start_speaking_ssml(self, ssml: str) -> SpeechSynthesisResult:
        """
        Starts synthesis on ssml in a blocking (synchronous) mode.

        :return: A SpeechSynthesisResult.
        """
        raise NotImplementedError

    def start_speaking_text_async(self, text: str) -> ResultFuture:
        """
        Starts synthesis on plain text in a non-blocking (asynchronous) mode.

        :return: A future with SpeechSynthesisResult.
        """
        raise NotImplementedError

    def start_speaking_ssml_async(self, ssml: str) -> ResultFuture:
        """
        Starts synthesis on ssml in a non-blocking (asynchronous) mode.

        :return: A future with SpeechSynthesisResult.
        """
        raise NotImplementedError

    @property
    def properties(self):
        """
        A collection of properties and their values defined for this SpeechSynthesizer.
        """
        raise NotImplementedError

    @property
    def authorization_token(self) -> str:
        """
        The authorization token that will be used for connecting to the service.

        .. note::
          The caller needs to ensure that the authorization token is valid. Before the
          authorization token expires, the caller needs to refresh it by calling this setter with a
          new valid token. Otherwise, the synthesizer will encounter errors while speech synthesis.
        """
        raise NotImplementedError

    @authorization_token.setter
    def authorization_token(self, authorization_token: str):
        raise NotImplementedError

    @property
    def synthesis_started(self) -> EventSignal:
        """
        Signal for events indicating synthesis has started.

        Callbacks connected to this signal will be called.
        """
        return self.__synthesis_started_event

    @property
    def synthesizing(self) -> EventSignal:
        """
        Signal for events indicating synthesis is ongoing.

        Callbacks connected to this signal will be called.
        """
        return self.__synthesizing_event

    @property
    def synthesis_completed(self) -> EventSignal:
        """
        Signal for events indicating synthesis has completed.

        Callbacks connected to this signal will be called.
        """
        return self.__synthesis_completed_event

    @property
    def synthesis_canceled(self) -> EventSignal:
        """
        Signal for events indicating synthesis has been canceled.

        Callbacks connected to this signal will be called.
        """
        return self.__synthesis_canceled_event
