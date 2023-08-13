from threading import Lock


class Singleton(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._lock.acquire()

            try:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            except Exception as e:
                raise Exception(f"Exception in instance creation: {e}")
            finally:
                cls._lock.release()
        return cls._instances[cls]

