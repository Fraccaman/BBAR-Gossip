import yaml


class Config:

    def __init__(self, path):
        self.config = yaml.load(open(path), Loader=yaml.FullLoader)

    def get(self, key):
        return self.config[key] if key in self.config else None
