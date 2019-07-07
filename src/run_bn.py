import argparse

from config.Config import Config
from src.network.BootstrapNode import BootstrapNode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a bootstrap node')
    parser.add_argument('--config', help='config path', required=True)
    args = parser.parse_args()

    config = Config(args.config)

    server = BootstrapNode(config).start()
