class StorageException(Exception):
    ...


class FileNotFound(StorageException, FileNotFoundError):
    ...