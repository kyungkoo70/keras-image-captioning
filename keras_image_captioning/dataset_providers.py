import numpy as np

from copy import copy
from math import ceil
from operator import attrgetter

from .config import active_config
from .datasets import get_dataset_instance
from .preprocessors import CaptionPreprocessor, ImagePreprocessor


class DatasetProvider(object):
    def __init__(self,
                 batch_size=None,
                 dataset=None,
                 image_preprocessor=None,
                 caption_preprocessor=None):
        """
        If an arg is None, it will get its value from config.active_config.
        """
        self._batch_size = batch_size or active_config().batch_size
        self._dataset = (dataset or get_dataset_instance())
        self._image_preprocessor = image_preprocessor or ImagePreprocessor()
        self._caption_preprocessor = (caption_preprocessor or
                                      CaptionPreprocessor())
        self._build()

    @property
    def vocab_size(self):
        return self._caption_preprocessor.vocab_size

    @property
    def training_steps(self):
        return int(ceil(1. * self._dataset.training_set_size /
                        self._batch_size))

    @property
    def validation_steps(self):
        return int(ceil(1. * self._dataset.validation_set_size /
                        self._batch_size))

    @property
    def testing_steps(self):
        return int(ceil(1. * self._dataset.testing_set_size /
                        self._batch_size))

    @property
    def training_results_dir(self):
        return self._dataset.training_results_dir

    def training_set(self):
        for batch in self._batch_generator(self._dataset.training_set):
            yield batch

    def validation_set(self):
        for batch in self._batch_generator(self._dataset.validation_set):
            yield batch

    def testing_set(self):
        for batch in self._batch_generator(self._dataset.testing_set):
            yield batch

    def _build(self):
        training_set = self._dataset.training_set
        training_captions = map(attrgetter('caption_txt'), training_set)
        self._caption_preprocessor.fit_on_captions(training_captions)

    def _batch_generator(self, datum_list):
        # TODO Make it thread-safe. Currently only suitable for workers=1 in
        # fit_generator.
        datum_list = copy(datum_list)
        while True:
            np.random.shuffle(datum_list)
            datum_batch = []
            for datum in datum_list:
                datum_batch.append(datum)
                if len(datum_batch) >= self._batch_size:
                    yield self._preprocess_batch(datum_batch)
                    datum_batch = []
            if not datum_batch:
                yield self._preprocess_batch(datum_batch)

    def _preprocess_batch(self, datum_batch):
        imgs_path = map(attrgetter('img_path'), datum_batch)
        captions_txt = map(attrgetter('caption_txt'), datum_batch)

        img_batch = self._image_preprocessor.preprocess_images(imgs_path)
        caption_batch = self._caption_preprocessor.encode_captions(captions_txt)

        imgs_input = self._image_preprocessor.preprocess_batch(img_batch)
        captions = self._caption_preprocessor.preprocess_batch(caption_batch)

        captions_input, captions_output = captions
        X, y = [imgs_input, captions_input], captions_output
        return X, y