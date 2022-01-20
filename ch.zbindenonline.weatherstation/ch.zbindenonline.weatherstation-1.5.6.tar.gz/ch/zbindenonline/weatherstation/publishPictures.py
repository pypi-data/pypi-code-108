import datetime
import logging
import os
import shutil
from pathlib import Path

from ch.zbindenonline.weatherstation.logging import configure_logging
from .config import *
from .restServicePictures import RestServicePictures, Response


def get_pictures(picture_dir) -> list[str]:
    logging.info('Parsing ' + picture_dir)
    files = list()
    for file in os.listdir(picture_dir):
        if file.endswith('.jpg') or file.endswith('.webp'):
            files.append(os.path.join(picture_dir, file))
    return files


def get_existing_picture_dir(picture_dir) -> Path:
    pictures_path = Path(picture_dir)
    return Path(pictures_path, 'existing')


def should_be_moved(post_result):
    return post_result is Response.DUPLICATE or post_result is Response.UNPROCESSABLE_ENTITY


class Main:
    def __init__(self, config: PicturesConfig):
        self.service = self.__create_service(config)
        self.delete_after_publish = config.delete_after_publish
        self.existing_picture_dir = get_existing_picture_dir(config.picture_dir)

    def __create_service(self, config: PicturesConfig) -> RestServicePictures:
        return RestServicePictures(config.picture_url, config.camera_id,
                                   config.client_id, config.client_secret,
                                   config.username, config.password)

    def run(self, pictures: list[str]) -> None:
        start = datetime.datetime.now()
        try:
            if len(pictures) == 0:
                logging.info('Nothing to publish')
            else:
                self.service.login()
                posted_pictures = 0
                for picture in pictures:
                    logging.debug('Try to publish ' + picture)
                    try:
                        post_result = self.service.post_picture(picture)
                        if post_result is Response.OK:
                            posted_pictures += 1
                            self.__delete_if_wanted(picture)
                        elif should_be_moved(post_result):
                            logging.debug('Picture exists already')
                            self.__move_if_wanted(picture)
                    except Exception as e:
                        logging.warning('There was an Exception in posting picture ' + picture + ': ' + str(e))
                self.service.logout()

                elapsed_time = datetime.datetime.now() - start
                logging.info('Posted ' + str(posted_pictures) + ' in ' + str(elapsed_time))
        except Exception as e:
            logging.error("Error occurred: " + str(e))

    def __move_if_wanted(self, picture):
        if self.existing_picture_dir is not None:
            shutil.move(picture, str(self.existing_picture_dir), copy_function=shutil.copytree)

    def __delete_if_wanted(self, picture):
        if self.delete_after_publish:
            logging.debug('Delete ' + picture)
            os.remove(picture)


def main():
    config = read_configuration()
    configure_logging(config.loglevel)
    picture_config = config.pictures
    pictures = get_pictures(picture_config.picture_dir)

    Main(picture_config).run(pictures)


if __name__ == '__main__':
    main()
