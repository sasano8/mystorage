from pydantic import BaseModel
from webdav3.client import Client as Webdav3Client
from webdav3.exceptions import ResponseErrorCode, RemoteResourceNotFound
from mystorage.types import ProviderFactory, Provider, ResourceTypes
from mystorage.exceptions import StorageException
from datetime import datetime, timezone, timedelta
import os

# https://github.com/ezhov-evgeny/webdav-client-python-3
# PUT DELETE MKCOL COPY MOVE
# PRPFIND OPTIONS
# create_full_put_path: アップロード先ディレクトリの自動生成有無


class WebdavConfig(BaseModel, ProviderFactory):
    user: str = "admin"
    password: str = "admin"
    protocol: str = "http"
    host: str = "localhost"
    port: int = 8080
    verify: bool = False  # To not check SSL certificates (Default = True)
    base_path: str = "remote.php/dav/files"
    webdav_root: str = "/"

    def get_url(self):
        return (
            f"{self.protocol}://{self.host}:{self.port}/{self.base_path}/{self.user}"
        )

    def get_option(self):
        return {
            "webdav_hostname": self.get_url(),
            "webdav_login": self.user,
            "webdav_password": self.password,
            "webdav_root": self.webdav_root
        }

    def get_native_provider(self):
        client = Webdav3Client(self.get_option())
        client.verify = self.verify  # To not check SSL certificates (Default = True)
        return client

    def get_provider(self):
        client = self.get_native_provider()
        provider = WebdavProvider(client)
        return provider


class FileInfo(BaseModel):
    created: datetime
    modified: datetime
    name: str
    size: int
    etag: str
    content_type: str = ""
    is_dir: bool
    path: str


DT_SAMPLE = "Sat, 17 Dec 2022 13:58:13 GMT"
DT_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"


def strptime(dt: str):
    tzname = dt.split(" ")[-1].upper()
    if tzname not in {"GMT", "UTC"}:
        raise Exception()
    dt = datetime.strptime(dt, DT_FORMAT)
    tz = timezone(timedelta(hours=+0))
    dt = dt.replace(tzinfo=tz)
    return dt


class WebdavProvider(Provider):
    def __init__(self, client: Webdav3Client):
        self.client = client

    @staticmethod
    def convert_info(x: dict):
        # return [FileInfo(**x) for x in self.client.list(path, get_info=True)]
        dt = str(strptime(x["modified"]))
        x["modified"] = dt
        if x["created"] is None:
            x["created"] = dt
        if x["size"] is None:
            x["size"] = 0
        else:
            if x["size"] == "":
                x["size"] = 0
            else:
                x["size"] = int(x["size"])
        if "isdir" in x:
            if x["isdir"]:
                x["isdir"] = ResourceTypes.DIR
            else:
                x["isdir"] = ResourceTypes.FILE
        else:
            x["isdir"] = ResourceTypes.FILE
        return x

    def login(self):
        # 認証について直接確認するものがないので、freeで代替する。free以外だと、的外れなメッセージが返る。
        self.client.free()  # if error return 401
        return True

    def options(self, path):
        # サーバからhttpメソッド: options を使ってサーバーの情報が取れるみたいだが、クライアントにそれらしい実装はない
        from webdav3.urn import Urn
        urn = Urn(path)
        response = self.client.execute_request(action='check', path=urn.quote())
        response.raise_for_status()
        # response.headers
        return response.headers

    def free(self):
        return int(self.client.free())

    def info(self, path):
        info = self.client.info(path)
        return self.convert_info(info)

    def info_or_none(self, path):
        if self.exists(path):
            return self.info(path)
        else:
            return None

    def delete(self, path) -> int:
        return self.client.clean(path)

    def exists(self, path):
        return self.client.check(path)

    def type(self, path):
        if not self.exists(path):
            return ResourceTypes.NO_EXISTS
        else:
            return self.info(path)["isdir"]

    def mkdir(self, path):
        self.client.mkdir(path)
        return self.info(path)

    def put(self, path, buf):
        return self._create_or_put("put", path, buf)

    def create(self, path, buf):
        return self._create_or_put("create", path, buf)

    def _create_or_put(self, action, path, buf):
        if action == "create":
            try:
                if self.exists(path):
                    raise StorageException("Resource already exists.")
            except RemoteResourceNotFound as e:
                ...
        elif action == "put":
            try:
                if self.client.is_dir(path):
                    raise StorageException("PUT is not allowed on non-files.")
            except RemoteResourceNotFound as e:
                ...
        else:
            raise Exception()
        res = self.client.resource(path)
        res.read_from(buf)
        return self.convert_info(res.info())

    def read(self, path, buf):
        res = self.client.resource(path)
        res.write_to(buf)
        return buf

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

    def ll(self, path):
        # return [FileInfo(**x) for x in self.client.list(path, get_info=True)]
        convert = self.convert_info
        return [convert(x) for x in self.client.list(path, get_info=True)]

    def ls(self, path):
        return [x.replace("/", "") for x in self.client.list(path, get_info=False)]

    def ls_files(self, path):
        return [x["name"] for x in self.ll_files()]

    def ls_dirs(self, path):
        return [x["name"] for x in self.ll_dirs()]

    def ll_files(self, path):
        type = ResourceTypes.FILE
        return [x for x in self.ll() if x["isdir"] == type]

    def ll_dirs(self, path):
        type = ResourceTypes.DIR
        return [x for x in self.ll() if x["isdir"] == type]

    def move(self, src, dest):
        if not self.exists(src):
            raise StorageException("Src not found.")

        res = self.client.resource(src)
        return res.move(dest)

    def copy(self, src, dest):
        if not self.exists(src):
            raise StorageException("Src not found.")
        res = self.client.resource(src)
        return res.copy(dest)

    def rename(self, src, name):
        if not self.exists(src):
            raise StorageException("Src not found.")
        res = self.client.resource(src)
        return res.rename(name)

    def download(self, remote_path, local_path):
        return self.client.download_sync(remote_path, local_path)

    def upload(self, local_path, remote_path):
        return self.client.upload_sync(remote_path, local_path)

    # download_sync
    # download_async
    # upload_sync
    # upload_async
    # move
    # pull  # Get the missing files
    # push  # Send missing files

    """
    res1 = client.resource("dir1/file1")

    res1.rename("file2")
    res1.move("dir1/file2")
    res1.copy("dir2/file1")
    info = res1.info()
    res1.read_from(buffer)
    res1.read(local_path="~/Documents/file1")
    res1.read_async(local_path="~/Documents/file1", callback)
    res1.write_to(buffer)
    res1.write(local_path="~/Downloads/file1")
    res1.write_async(local_path="~/Downloads/file1", callback)
    """
