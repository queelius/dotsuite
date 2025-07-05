class Path:
    def __init__(self, path):
        self.parts = path.split('.')

    def get(self, data):
        for part in self.parts:
            if isinstance(data, dict):
                data = data.get(part)
            elif isinstance(data, list):
                try:
                    data = data[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return data
