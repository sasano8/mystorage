from pydantic import BaseModel
from datetime import datetime
from typing import List, Tuple
import os

class ProviderFactory:
    def get_native_provider(self, path=""):
        ...

    def get_provider(self, path="") -> "Provider":
        ...


class ResourceTypes:
    NO_EXISTS = 0
    DIR = 1
    FILE = 2
    STORAGE = 3


class ProviderBase:
    def abspath(self, path):
        raise NotImplementedError()

    def exists(self, path) -> bool:
        raise NotImplementedError()

    def info(self, path):
        raise NotImplementedError()

    def type(self, path) -> ResourceTypes:
        raise NotImplementedError()

    def isdir(self, path) -> bool:
        raise NotImplementedError()

    def ls(self, path) -> List[str]:
        raise NotImplementedError()

    def ls_files(self, path) -> List[str]:
        raise NotImplementedError()

    def ls_dirs(self, path):
        raise NotImplementedError()

    def ll(self, path):
        raise NotImplementedError()

    def ll_files(self, path) -> List[str]:
        raise NotImplementedError()

    def ll_dirs(self, path):
        raise NotImplementedError()

    # def delete(self, path):
    #     raise NotImplementedError()

    # def mkdir(self, path):
    #     raise NotImplementedError()

    # def create(self, path, buf):
    #     raise NotImplementedError()

    # def put(self, path, buf):
    #     raise NotImplementedError()

    # def touch(self, path):
    #     raise NotImplementedError()


class Reader(ProviderBase):
    def read(self, path, buf):
        raise NotImplementedError()

    def read_bytes(self, path):
        import io

        buf = io.BytesIO()
        buf = self.read(path, buf)
        buf.seek(0)
        return buf.read()

    def read_text(self, path, encoding=None):
        import io

        buf = io.BytesIO()
        buf = self.read(path, buf)
        buf.seek(0)
        return io.TextIOWrapper(buf, encoding).read()

    def read_json(self, path):
        import io
        import json

        buf = io.BytesIO()
        buf = self.read(path, buf)
        buf.seek(0)
        return json.load(buf)


class Writer(Reader):
    def delete(self, path):
        raise NotImplementedError()

    def mkdir(self, path):
        raise NotImplementedError()

    def create(self, path, buf):
        raise NotImplementedError()

    def put(self, path, buf):
        raise NotImplementedError()

    def move(self, src, dest):
        raise NotImplementedError()

    def copy(self, src, dest):
        raise NotImplementedError()

    def rename(self, src, name):
        raise NotImplementedError()

    def write(self, path, buf):
        raise NotImplementedError()

    def write_bytes(self, path, data: bytes):
        raise NotImplementedError()

    def write_text(self, path, data: str, encoding=None):
        raise NotImplementedError()

    def write_json(self, path, json):
        raise NotImplementedError()

    def touch(self, path):
        import io

        buf = io.BytesIO(b"")
        return self.create(path, buf)


class Provider(Writer):
    ...


class LocalStorageBase(Provider):
    ...


class StorageArray(Provider):
    def __init__(self, **storages: Provider):
        self.storages = storages

    def get_storage_by_id(self, id: int):
        ...


class StorageSyncReplica(Provider):
    def __init__(self, storage, **replicas: Provider):
        self.storage = storage
        self.storages = replicas


class StorageAsyncReplica(Provider):
    def __init__(self, storage, **replicas: Provider):
        self.storage = storage
        self.storages = replicas


class Resource:
    def __init__(self, provider: Provider, path: str):
        self.provider = provider
        self.path = path

    def abspath(self):
        if isinstance(self.provider, LocalStorageBase):
            return os.path.abspath(self.path)
        else:
            raise Exception()

    def abspath_or_none(self):
        if isinstance(self.provider, LocalStorageBase):
            return os.path.abspath(self.path)
        else:
            return None

    def pull_from(self, remote: "Resource"):
        ...

    def push_to(self, remote: "Resource"):
        if self.abspath_or_none() is None:
            raise NotImplementedError()
            self.download()
        else:
            self.provider.dowload_local(remote.path)
            self.provider.put()


class SafeClient:
    def __init__(self, provider: Provider, root: str = ""):
        self.provider = provider
        self.root = root

    @staticmethod
    def validate(path):
        return path

    def mkdir(self, path):
        path = self.validate(path)
        return self.provider.mkdir(path)


class ArtifactDir:
    def __init__(
        self,
        local_client: SafeClient,
        pull_client: SafeClient = None,
        push_client: SafeClient = None,
    ):
        ...


class Artifact:
    def __init__(self, dir: ArtifactDir):
        ...


class FileInfo(BaseModel):
    created: datetime
    modified: datetime
    name: str
    size: int
    etag: str
    content_type: str = ""
    is_dir: bool
    path: str
