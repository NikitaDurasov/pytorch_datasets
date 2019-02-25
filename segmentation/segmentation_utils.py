from torch.utils.data import Dataset
from abc import abstractmethod
import h5py
import os

module_path = os.path.dirname(os.path.realpath(__file__))


class SegmentationBase(Dataset):

    def __init__(self, data_path, split, transform=None):
        self.data_path = data_path
        self.transform = transform
        self.split = split

        self.data_files = self.generate_split()

    def __len__(self):
        return len(self.data_files)

    def __getitem__(self, index):
        sample = self.data_files[index]

        image_name = sample[0]
        mask_name = sample[1]

        image = self.load_image(image_name)
        mask = self.load_segmentation(mask_name)

        if mask is not None:
            sample = {"image": image, "mask": mask}
        else:
            sample = {"image": image}

        if self.transform:
            sample = self.transform(**sample)

        return sample

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def load_image(self, filename):
        pass

    @abstractmethod
    def load_segmentation(self, filename):
        pass

    def line_to_filepaths(self, line):
        line = line.rstrip()
        image = os.path.join(*[self.data_path] + line.split("\t")[0].split(" "))

        if line.split("\t")[1].split(" ")[0] != "-":
            mask = os.path.join(*[self.data_path] + line.split("\t")[1].split(" "))
        else:
            mask = '-'

        return image, mask

    @abstractmethod
    def generate_split(self):

        if self.split == "train":
            split_path = os.path.join(module_path, "splits", self.name() + "_train_split.txt")
            split_file = open(split_path)
            return list(map(self.line_to_filepaths, split_file.readlines()))

        elif self.split == "valid":
            split_path = os.path.join(module_path, "splits", self.name() + "_val_split.txt")
            split_file = open(split_path)
            return list(map(self.line_to_filepaths, split_file.readlines()))

        elif self.split == "test":
            split_path = os.path.join(module_path, "splits", self.name() + "_test_split.txt")
            split_file = open(split_path)
            return list(map(self.line_to_filepaths, split_file.readlines()))

class SegmentationHDF5(Dataset):

    def base_path(self):
        return module_path