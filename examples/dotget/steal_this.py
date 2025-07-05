"""
Examples designed to be copied into your own code.
Each function is self-contained and requires no imports.
"""

# 1. Basic getter - copy this if you just need simple access
def get_nested(data, path, default=None):
    """Get nested value using dot notation."""
    try:
        for key in path.split('.'):
            data = data[int(key)] if key.isdigit() else data[key]
        return data
    except (KeyError, IndexError, TypeError):
        return default


# 2. Config wrapper - copy this for configuration files
class Config:
    """Simple config wrapper with dot notation."""
    def __init__(self, data):
        self._data = data

    def get(self, path, default=None):
        data = self._data
        try:
            for key in path.split('.'):
                data = data[int(key)] if key.isdigit() else data[key]
            return data
        except (KeyError, IndexError, TypeError):
            return default


# 3. Multi-getter - copy this for extracting multiple values
def extract_values(data, paths):
    """Extract multiple values from nested data."""
    result = {}
    for path in paths:
        value = data
        try:
            for key in path.split('.'):
                value = value[int(key)] if key.isdigit() else value[key]
            result[path] = value
        except (KeyError, IndexError, TypeError):
            result[path] = None
    return result


# Example usage (don't copy this part):
if __name__ == "__main__":
    data = {
        "app": {
            "name": "MyApp",
            "version": "1.0.0",
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
    }

    # Using basic getter
    print(get_nested(data, "app.name"))  # "MyApp"
    print(get_nested(data, "app.database.host"))  # "localhost"

    # Using config wrapper
    config = Config(data)
    print(config.get("app.database.port", 3306))  # 5432

    # Using multi-getter
    values = extract_values(data, [
        "app.name",
        "app.version",
        "app.database.port"
    ])
    print(values)
