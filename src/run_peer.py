import argparse

from config.Config import Config
from src.network.PeerNode import PeerNode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a gossip node')
    parser.add_argument('--config', help='config path', required=True)
    args = parser.parse_args()

    config = Config(args.config)

    server = PeerNode(config).start()
