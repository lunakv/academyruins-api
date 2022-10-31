import json
from . import static_paths as paths
from pathlib import Path

# global cache store
_caches = {}


class ReadOnlyCache:
    def __init__(self, resource, path):
        self.path = path
        self.resource = resource
        if resource not in _caches:
            if path and Path(path).is_file():
                with open(path, "r") as file:
                    _caches[resource] = json.load(file)
            else:
                _caches[resource] = {}

    def get(self, key):
        cache = _caches[self.resource]
        return cache.get(key)

    def has(self, key):
        return key in _caches[self.resource]

    def keys(self):
        return _caches[self.resource].keys()

    def data(self):
        return _caches[self.resource]


class UpdatableCache(ReadOnlyCache):
    def replace(self, new_resource):
        _caches[self.resource] = new_resource
        self._update()

    def _update(self):
        if not self.path:
            return
        with open(self.path, "w") as file:
            json.dump(_caches[self.resource], file)


class Cache(UpdatableCache):
    def set(self, key, value):
        _caches[self.resource][key] = value
        self._update()

    def delete(self, key):
        if key in _caches[self.resource]:
            del _caches[self.resource][key]
            self._update()


class UnofficialGlossaryCache(ReadOnlyCache):
    def __init__(self):
        super().__init__("unofficial_glossary", paths.unofficial_glossary_dict)


class GlossaryCache(UpdatableCache):
    def __init__(self):
        super().__init__("glossary", paths.glossary_dict)
        self.unofficial = UnofficialGlossaryCache()
        self.searches = Cache("glossary.searches", None)

        unofficial_searches = self.__generate_searches(self.unofficial.data())
        self.searches.set("unofficial", unofficial_searches)
        self.__create_searches()

    def __create_searches(self):
        official_searches = self.__generate_searches(self.data())
        self.searches.set("official", official_searches)
        self.searches.set("all", self.searches.get("unofficial") | official_searches)

    def __generate_searches(self, store):
        searches = {}
        splits = []
        for key in store:
            search_term = key.replace(" (obsolete)", "")
            searches[search_term] = key
            search_split = search_term.split(", ")
            if len(search_split) > 1:
                for elem in search_split:
                    splits.append((elem, key))
        for split in splits:
            if split[0] not in searches:
                searches[split[0]] = split[1]

        return searches

    def get_any(self, key):
        return self.get(key) if self.has(key) else self.unofficial.get(key)

    def _update(self):
        super()._update()
        self.__create_searches()

    def all_searches(self):
        return self.searches.get("all")

    def official_searches(self):
        return self.searches.get("official")

    def unofficial_searches(self):
        return self.searches.get("unofficial")


class KeywordCache(UpdatableCache):
    def __init__(self):
        super().__init__("keyword", paths.keyword_dict)
