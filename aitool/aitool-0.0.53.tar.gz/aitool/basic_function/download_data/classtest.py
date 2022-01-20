# -*- coding: UTF-8 -*-
# @Time    : 2020/10/22
# @Author  : xiangyuejia@qq.com
from typing import Any, Tuple

from aitool.basic_function.download_data.utils import check_integrity, download_and_extract_archive


class ClassTest1:
    base_folder = 'cifar-10-batches-py'
    url = 'https://raw.githubusercontent.com/deepgameai/datasets/main/NLP/classifier/test.txt'
    filename = 'test.txt'
    tgz_md5 = '749b1843d4c4be33afc4ba7f1158fc33'
    train_list = [
        ['data_batch_1', 'c99cafc152244af753f735de768cd75f'],
    ]
    test_list = [
        ['test_batch', '40351d587109b95175f43aff81a1287e'],
    ]

    def __init__(
            self,
            root: str,
            train: bool = True,
            download: bool = False,
    ) -> None:

        self.root = root
        self.train = train

        if download:
            self.download()

        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        if self.train:
            downloaded_list = self.train_list
        else:
            downloaded_list = self.test_list

        self.data: Any = []
        self.targets = []

        # now load the picked numpy arrays
        for file_name, checksum in downloaded_list:
            file_path = os.path.join(self.root, self.base_folder, file_name)
            with open(file_path, 'rb') as f:
                pass

        self._load_meta()

    def _load_meta(self) -> None:
        path = os.path.join(self.root, self.base_folder, self.meta['filename'])
        if not check_integrity(path, self.meta['md5']):
            raise RuntimeError('Dataset metadata file not found or corrupted.' +
                               ' You can use download=True to download it')
        with open(path, 'rb') as infile:
            path

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], self.targets[index]
        return img, target

    def __len__(self) -> int:
        return len(self.data)

    def _check_integrity(self) -> bool:
        root = self.root
        for fentry in (self.train_list + self.test_list):
            filename, md5 = fentry[0], fentry[1]
            fpath = os.path.join(root, self.base_folder, filename)
            if not check_integrity(fpath, md5):
                return False
        return True

    def download(self) -> None:
        if self._check_integrity():
            print('Files already downloaded and verified')
            return
        download_and_extract_archive(self.url, self.root, filename=self.filename, md5=self.tgz_md5)

    def extra_repr(self) -> str:
        return "Split: {}".format("Train" if self.train is True else "Test")


if __name__ == '__main__':
    import os
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:12639"
    data = ClassTest1('.', train=True, download=True)
    ccc = 1
