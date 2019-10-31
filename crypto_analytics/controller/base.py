from abc import ABC, abstractmethod

class Controller(ABC):
    """ An abstract base class for all controllers """

    @abstractmethod
    def run(self):
        """ Start controller runloop """
        pass
