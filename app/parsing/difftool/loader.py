from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def load(self, doc_desc):
        pass


class CRLoader(Loader):
    def load(self, set_id):
        pass
