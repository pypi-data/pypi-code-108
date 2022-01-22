# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
#    and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from urllib.parse import urlencode
from urllib.request import urlopen
from neon_utils.configuration_utils import get_neon_tts_config
from neon_utils.logger import LOG
from neon_utils.parse_utils import format_speak_tags, normalize_string_to_speak

try:
    from neon_audio.tts import TTS, TTSValidator
except ImportError:
    from mycroft.tts import TTS, TTSValidator
from mycroft.metrics import Stopwatch


class MozillaRemoteTTS(TTS):

    def __init__(self, lang="en-us", config=None):
        config = config or get_neon_tts_config().get("mozilla", {})
        super(MozillaRemoteTTS, self).__init__(lang, config, MozillaTTSValidator(self),
                                               audio_ext="wav",
                                               ssml_tags=["speak"])
        self.base_url = config.get("api_url", "http://0.0.0.0:5002/api/tts")

    def get_tts(self, sentence, wav_file, speaker=None):
        stopwatch = Stopwatch()

        to_speak = format_speak_tags(sentence, False)
        LOG.debug(to_speak)
        if to_speak:
            url = self._build_url(normalize_string_to_speak(to_speak))
            with stopwatch:
                wav_data = urlopen(url).read()
            LOG.debug(f"Request time={stopwatch.time}")

            with stopwatch:
                with open(wav_file, "wb") as f:
                    f.write(wav_data)
            LOG.debug(f"File access time={stopwatch.time}")
        return wav_file, None

    def _build_url(self, sentence) -> str:
        params = urlencode({'text': sentence})
        url = '?'.join([self.base_url, params])
        return url


class MozillaTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(MozillaTTSValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_dependencies(self):
        pass

    def validate_connection(self):
        # TODO
        pass

    def get_tts_class(self):
        return MozillaRemoteTTS
