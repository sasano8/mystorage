import io
import tempfile
from pathlib import Path

import pytest

from mystorage import providers
from mystorage.exceptions import StorageException
from mystorage.testtool import Cleanup, NoCleanup
from mystorage.types import Provider, SafeClient


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as dirname:
        yield Path(str(dirname))


def test_providers(tmpdir: Path):
    ROOT = "test1"
    provider = providers.WebdavConfig().get_provider()

    # with Cleanup(ROOT, provider):
    with NoCleanup(ROOT, provider):
        assert provider.login() == True
        assert provider.options("")
        print(provider.options(""))
        assert isinstance(provider.exists(ROOT), bool)

        # mkdir
        assert provider.exists(ROOT) == False
        assert provider.mkdir(ROOT)
        assert provider.exists(ROOT) == True

        # put
        assert provider.exists(ROOT + "/file2.txt") == False
        assert provider.put(ROOT + "/file2.txt", io.BytesIO("あ".encode("utf8")))
        assert provider.exists(ROOT + "/file2.txt") == True
        assert provider.read_bytes(ROOT + "/file2.txt").decode("utf8") == "あ"

        # put if overwrite
        assert provider.put(ROOT + "/file2.txt", io.BytesIO("い".encode("utf8")))
        assert provider.exists(ROOT + "/file2.txt") == True
        assert provider.read_bytes(ROOT + "/file2.txt").decode("utf8") == "い"

        # put if overwrite onto dir
        with pytest.raises(StorageException):
            assert provider.put(ROOT, io.BytesIO("い".encode("utf8")))

        # create
        assert provider.exists(ROOT + "/file3.txt") == False
        assert provider.create(ROOT + "/file3.txt", io.BytesIO("あ".encode("utf8")))
        assert provider.exists(ROOT + "/file3.txt") == True
        assert provider.read_bytes(ROOT + "/file3.txt").decode("utf8") == "あ"

        # create if overwrite
        with pytest.raises(StorageException):
            assert provider.create(ROOT + "/file3.txt", io.BytesIO("い".encode("utf8")))

        # create if overwrite onto dir
        with pytest.raises(StorageException):
            assert provider.create(ROOT, io.BytesIO("い".encode("utf8")))

        # touch
        assert provider.exists(ROOT + "/file1.txt") == False
        assert provider.touch(ROOT + "/file1.txt")
        assert provider.exists(ROOT + "/file1.txt") == True
        assert provider.read_bytes(ROOT + "/file1.txt").decode("utf8") == ""

        # touch if overwrite
        with pytest.raises(StorageException):
            assert provider.touch(ROOT + "/file1.txt")

        # touch if overwrite onto dir
        with pytest.raises(StorageException):
            assert provider.touch(ROOT + "/file1.txt")

        # move
        assert provider.exists(ROOT + "/file1.txt") == True
        assert provider.exists(ROOT + "/moved.txt") == False
        assert provider.move(ROOT + "/file1.txt", ROOT + "/moved.txt") is None
        assert provider.read_bytes(ROOT + "/moved.txt").decode("utf8") == ""
        assert provider.exists(ROOT + "/file1.txt") == False
        assert provider.exists(ROOT + "/moved.txt") == True

        assert provider.exists(ROOT + "/not_exists.txt") == False
        with pytest.raises(StorageException):
            assert provider.move(ROOT + "/not_exists.txt", ROOT + "/moved2.txt") is None

        # copy
        assert provider.exists(ROOT + "/moved.txt") == True
        assert provider.exists(ROOT + "/copied.txt") == False
        assert provider.copy(ROOT + "/moved.txt", ROOT + "/copied.txt")
        assert provider.read_bytes(ROOT + "/copied.txt").decode("utf8") == ""
        assert provider.exists(ROOT + "/moved.txt") == True
        assert provider.exists(ROOT + "/copied.txt") == True

        assert provider.exists(ROOT + "/not_exists.txt") == False
        with pytest.raises(StorageException):
            assert (
                provider.copy(ROOT + "/not_exists.txt", ROOT + "/copied2.txt") is None
            )

        # rename
        assert provider.exists(ROOT + "/copied.txt") == True
        assert provider.exists(ROOT + "/renamed.txt") == False
        assert provider.rename(ROOT + "/copied.txt", ROOT + "/renamed.txt") is None
        assert provider.read_bytes(ROOT + "/renamed.txt").decode("utf8") == ""
        assert provider.exists(ROOT + "/copied.txt") == False
        assert provider.exists(ROOT + "/renamed.txt") == True

        assert provider.exists(ROOT + "/not_exists.txt") == False
        with pytest.raises(StorageException):
            assert (
                provider.rename(ROOT + "/not_exists.txt", ROOT + "/renamed2.txt")
                is None
            )

        if True:
            DIR_DOWN = tmpdir / "download_test"
            DIR_UP = tmpdir / "upload_test"
            DIR_DOWN.mkdir()
            DIR_UP.mkdir()
        else:
            ...

        # download
        assert provider.mkdir(ROOT + "/download_empty_dir")
        assert DIR_DOWN.exists()
        assert provider.exists(ROOT + "/download_empty_dir")
        provider.download(ROOT + "/download_empty_dir", str(DIR_DOWN))
        assert provider.exists(ROOT + "/download_empty_dir")
        assert len(list(DIR_DOWN.glob("*"))) == 0

        assert provider.touch(ROOT + "/download_empty_dir" + "/download_file1.txt")
        assert provider.download(ROOT + "/download_empty_dir", str(DIR_DOWN)) is None
        assert len(list(DIR_DOWN.glob("*"))) == 1

        assert provider.touch(ROOT + "/download_empty_dir" + "/download_file2.txt")
        assert provider.download(ROOT + "/download_empty_dir", str(DIR_DOWN)) is None
        assert len(list(DIR_DOWN.glob("*"))) == 2

        assert provider.touch(ROOT + "/download_file3.txt")
        assert (
            provider.download(
                ROOT + "/download_file3.txt", str(DIR_DOWN) + "/download_file3.txt"
            )
            is None
        )
        assert len(list(DIR_DOWN.glob("*"))) == 3

        # if no exists dir
        assert (
            provider.download(
                ROOT + "/download_file3.txt",
                str(DIR_DOWN) + "/no_exists/download_file3.txt",
            )
            is None
        )
        assert len(list(DIR_DOWN.glob("*"))) == 3

        # overwrite
        assert provider.touch(ROOT + "/download_file4.txt")
        assert (
            provider.download(
                ROOT + "/download_file4.txt", str(DIR_DOWN) + "/download_file3.txt"
            )
            is None
        )
        assert len(list(DIR_DOWN.glob("*"))) == 3

        # upload

        for name in provider.ls(ROOT):
            print(name)
            assert isinstance(name, str)

        for info in provider.ll(ROOT):
            print(info)
            assert not isinstance(info, str)
