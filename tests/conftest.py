import pytest, os, shutil

@pytest.fixture(scope='function')
def tmp_dir():
    """ fixture that sets up and tears down a tmp directory for tests """
    # setup
    file_dir = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = os.path.abspath(os.path.join(file_dir, 'tmp'))
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)

    yield tmp_dir

    # teardown
    shutil.rmtree(tmp_dir)

@pytest.fixture(scope='function')
def init_abc(mocker):
    """ initializes an abstract base class for you """
    def setup_fn(ABC, *args, **kwargs):
        mocker.patch.object(ABC, '__abstractmethods__')
        ABC.__abstractmethods__ = set()
        return ABC(*args, **kwargs)

    return setup_fn
