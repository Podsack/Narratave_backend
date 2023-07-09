class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            try:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            except Exception as e:
                raise Exception(f"Exception in instance initialization: {e}")
        return cls._instances[cls]

