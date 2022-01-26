import errno
import os
import requests


class FileDownloadUtil:
    def __init__(self):
        path = "../temp/"
        if not os.path.exists(path):
            os.mkdir(path)
        self.downloadPath = path

    def save(self, file_url, filename):
        """

        :param file_url:
        :param filename:
        :return:
        """

        response = requests.get(file_url, stream=True)

        if not os.path.exists(os.path.dirname(self.downloadPath + filename)):
            try:
                os.makedirs(os.path.dirname(self.downloadPath + filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.downloadPath + filename, 'wb') as f:
            f.write(response.content)

        print('File ' + filename + ' is saved at ' + self.downloadPath)


if __name__ == '__main__':
    fd = FileDownloadUtil()
    url = 'https://goedoc.uni-goettingen.de/bitstream/handle/1/7672/Sommer.pdf'
    fileName = 'metadata.pdf'
    fd.save(url, fileName)
    print('file downloaded...')
    print('exiting program...')
