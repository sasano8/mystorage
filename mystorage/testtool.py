from mystorage.types import Provider


class Cleanup:
    def __init__(self, root, provider: Provider):
        self.root = root
        self.provider = provider

    def __enter__(self):
        SpecDiffTool.cleanup(self.root, self.provider)

    def __exit__(self, *args, **kwargs):
        SpecDiffTool.cleanup(self.root, self.provider)


class NoCleanup:
    def __init__(self, root, provider: Provider):
        self.root = root
        self.provider = provider

    def __enter__(self):
        SpecDiffTool.cleanup(self.root, self.provider)

    def __exit__(self, *args, **kwargs):
        ...


class SpecType(Cleanup):
    def exists(self, path):
        result = self.provider.exists(path)
        assert isinstance(result, bool)
        return result


def iterate(func):
    def wrapper(self, *args, **kwargs):
        it = iter(self.providers)
        ignores = self.ignore_functions
        actual = func(next(it), *args, **kwargs)

        for provider in it:
            expect = func(provider, *args, **kwargs)
            if func.__name__ not in ignores:
                if actual != expect:
                    raise Exception(
                        f"{provider.__class__}.{func.__name__}({args}, {kwargs}) actual != expect: {actual} != {expect}"
                    )

        return True

    return wrapper


class SpecDiffTool:
    def __init__(self, root, *providers: Provider, ignore_functions=set()):
        self.root = root
        self.providers = providers
        if not root:
            raise Exception()

        if len(self.providers) < 2:
            raise Exception()

    @staticmethod
    def cleanup(root, *providers):
        for provider in providers:
            try:
                if provider.exists(root):
                    provider.delete(root)
            except Exception as e:
                ...

    def __enter__(self):
        self.cleanup(self.root, *self.providers)

    def __exit__(self, *args, **kwargs):
        self.cleanup(self.root, *self.providers)

    @iterate
    def exists(self, path):
        return self.exists(path)
