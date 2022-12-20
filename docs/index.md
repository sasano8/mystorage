

```
from myhdf5 import ModelFile, TempModelStore, ModelStore
```

```
ModelFile.save("file1.hdf5", {})
assert ModelFile.load("file1.hdf5") == {}
```

```
f2 = ModelFIle("f2.hdf5")
f2.save({})
assert f2.load() == {}
```

```
with TempModelStore() as store:
    f1 = store.file()
    f1.save({})
    f1.load()  == {}

    f2 = store.file()
    f2.save({})
    f2.load()  == {}

    store.list()
```

```
with TempModelStore() as store:
    f1 = store.file()
    f1.save({}, meta={"name": "aaaa"})
```


```
ByteSerializer,
JsonSerializer,
NdarraySerializer,
WieghtsSerializer,
```