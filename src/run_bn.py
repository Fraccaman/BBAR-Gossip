import argparse
import os

from config.Config import Config
from src.network.BootstrapNode import BootstrapNode


def delete_dbs(id):
    if id != 30000: return
    dir_name = "../network/"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".db"):
            os.remove(os.path.join(dir_name, item))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a bootstrap node')
    parser.add_argument('--config', help='config path', required=True)
    args = parser.parse_args()

    config = Config(args.config)

    delete_dbs(config.get('id'))

    server = BootstrapNode(config).start()
