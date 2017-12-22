from os import remove
from os.path import isfile

FILE_TO_DEL = '../var/flickr8k/training-results/repro-final-model/hyperparams-config.yaml'

if isfile(FILE_TO_DEL) == True:
    print('Remove {} '.format(FILE_TO_DEL))
    remove('../var/flickr8k/training-results/repro-final-model/hyperparams-config.yaml')