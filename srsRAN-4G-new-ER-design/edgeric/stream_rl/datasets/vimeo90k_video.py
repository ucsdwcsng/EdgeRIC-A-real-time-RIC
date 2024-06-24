from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset


class Vimeo90kDataset(Dataset):
    """Load a Vimeo-90K structured dataset.

    Vimeo-90K dataset from
    Tianfan Xue, Baian Chen, Jiajun Wu, Donglai Wei, William T. Freeman:
    `"Video Enhancement with Task-Oriented Flow"
    <https://arxiv.org/abs/1711.09078>`_,
    International Journal of Computer Vision (IJCV), 2019.

    Training and testing image samples are respectively stored in
    separate directories:

    .. code-block::

        - rootdir/
            - sequence/
                - 00001/001/im1.png
                - 00001/001/im2.png
                - 00001/001/im3.png

    Args:
        root (string): root directory of the dataset
        transform (callable, optional): a function or transform that takes in a
            PIL image and returns a transformed version
        split (string): split mode ('train' or 'valid')
        tuplet (int): order of dataset tuplet (e.g. 3 for "triplet" dataset)
    """

    def __init__(self, root, transform=None, split="train", tuplet=3):
        list_path = Path(root) / self._list_filename(split, tuplet)

        with open(list_path) as f:
            self.sequences = [
                f"{root}/sequences/{line.rstrip()}" for line in f if line.strip() != ""
            ]

        self.tuplet = tuplet
        self.transform = transform

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            img: `PIL.Image.Image` or transformed `PIL.Image.Image`.
        """
        imgs = [
            self._img(f"{self.sequences[index]}/im{i}.png")
            for i in range(1, self.tuplet + 1)
        ]
        return torch.stack(imgs)

    def _img(self, path):
        img = Image.open(path).convert("RGB")
        if self.transform:
            return self.transform(img)
        return img

    def __len__(self):
        return len(self.sequences)

    def _list_filename(self, split: str, tuplet: int) -> str:
        tuplet_prefix = {3: "tri", 7: "sep"}[tuplet]
        list_suffix = {"train": "trainlist", "valid": "testlist"}[split]
        return f"{tuplet_prefix}_{list_suffix}.txt"
