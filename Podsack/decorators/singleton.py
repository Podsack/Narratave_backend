def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        nonlocal instances
        print(instances, id(instances))
        if cls not in instances:
            try:
                instances[cls] = cls(*args, **kwargs)
            except Exception as e:
                raise Exception(f"Exception in instance initialization: {e}")
        return instances[cls]
