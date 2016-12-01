import os
import json


def path_to_data_directory():
    """
    Searches downward from wherever is defined as "__main__" to find a `data` folder
    :return: The relative path to the data folder
    """
    path = "data/"
    layers = 1
    while not os.path.isdir(path):
        path = "../" + path
        layers += 1
        if layers > 100:
            # We are far too far away from the project and the data folder
            # likely doesn't exist. Raise and error to prevent an infinite loop
            raise FileNotFoundError("The data directory could not be found. Are you sure it exists?")
    return path


def _text_read(f):
    return [line for line in f]


def _text_write(lines, f):
    for line in lines:
        f.write(line + '\n')


def _tsv_read(f):
    return [line.split('\t') for line in f]


def _tsv_write(lines, f):
    for line in lines:
        f.write('\t'.join(line) + '\n')


DEFAULT_CACHE_FILE_MAPPINGS = {
    '.txt': (_text_read, _text_write),
    '.json': (json.load, json.dump),
    '.tsv': (_tsv_read, _tsv_write)
}


def mem_cache():
    def wrapper(fn):
        _cache = {}

        def inner_function(*args):
            if args not in _cache:
                # memory cache miss
                _cache[args] = fn(*args)
            return _cache[args]
        return inner_function
    return wrapper


def fs_cache(file_name, reader=None, writer=None):
    if reader is None:
        for ext, handlers in DEFAULT_CACHE_FILE_MAPPINGS.items():
            if file_name.endswith(ext):
                reader = handlers[0]
                break
    if writer is None:
        for ext, handlers in DEFAULT_CACHE_FILE_MAPPINGS.items():
            if file_name.endswith(ext):
                writer = handlers[1]
                break

    if reader is None or writer is None: raise ValueError('Missing reader/writer')

    def wrapper(fn):
        def inner_function(*args):
            cache_file = path_to_data_directory() + file_name.format(*args)
            if not os.path.exists(cache_file):
                # file cache miss
                result = fn(*args)
                with open(cache_file, 'w') as f: # store as file
                    writer(result, f)
                return result
            else:
                # file cache hit
                with open(cache_file) as f:
                    return reader(f)
            return _cache[args]
        return inner_function
    return wrapper


class TextStatistics:
    """Used to store a text and its cleaning information"""

    def __init__(self, text):
        self.original_text = text
        self.text = text
        self.emoji_count = 0
        self.hashtag_count = 0
        self.handle_count = 0
        self.url_count = 0
        self.abbreviation_count = 0
        self.punctuation_count = 0
        self.misspellings_count = 0
