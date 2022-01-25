import sys
import requests
import threading
from utils.thread_helpers import thread





class adapter:
    def __init__(self, url: str):
        self._url = url



    def __core(self, filename: str, use_thread: bool = True):
        class Tracker:
            percentageCompleted = 0
            contentLength = 0
            bytesDownloaded = 0
            trackable = True
            downloadThread: threading.Thread = None

        trackObj = Tracker()

        def download(animate=False):
            with open(filename, 'wb+') as file:
                response = requests.get(self._url, stream=True)
                total_length = response.headers.get('content-length')


                if total_length is None or int(total_length) == 0:
                    trackObj.trackable = False
                    file.write(response.content)
                else:
                    bytesWritten = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        bytesWritten += len(data)
                        file.write(data)

                        percentageCompleted = (bytesWritten / total_length) * 100

                        trackObj.percentageCompleted = percentageCompleted
                        trackObj.bytesDownloaded = bytesWritten
                        trackObj.contentLength = total_length

                        if animate:
                            sys.stdout.write('\r{}% Downloaded'.format(trackObj.percentageCompleted.__round__(2)))
                            sys.stdout.flush()

                if animate:
                    sys.stdout.write('\rDownload Completed')

        if use_thread:
            trackObj.downloadThread = thread(func=download)
        else:
            download(animate=True)

        return trackObj

    def download(self, filename: str):
        """
        Asynchronously Download file.
        Returns Type Tracker with attributes:

        .percentageCompleted
        .contentLength
        .bytesDownloaded
        .trackable
        .downloadThread

        """
        return self.__core(filename=filename)

    @property
    def dlCore(self):
        return self.__core


if __name__ == '__main__':
    pass
