import argparse

import yaml
from fastecdsa import keys, curve


# host: localhost
# port: 1338
# private_key: null
# bn_nodes:
#   - 0.0.0.0:1337

# host: 0.0.0.0
# port: 1337
# private_key: null


def generate_peer_config(i: int, bn: list):
    return {
        'host': '0.0.0.0',
        'port': 10000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'bn_nodes': bn,
        'id': 10000 + i,
        'log_level': 1
    }


def generate_bn_config(i):
    return {
        'host': '0.0.0.0',
        'port': 30000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'id': 30000 + i,
        'log_level': 1
    }


def dump(config: dict, folder: str):
    network_folder = folder + '/' + str(config['id'])
    with open(network_folder, "w+") as node:
        node.write(yaml.dump(config))


def generate_network(peers_length: int, bns_length: int, byzantine_bn: int, byzantine_peer: int, folder: str):
    bns = []
    for i in range(bns_length):
        config = generate_bn_config(i)
        bns.append(str(config['host']) + ':' + str(config['port']))
        dump(config, folder)

    for i in range(bns_length):
        config = generate_bn_config(i)
        bns.append(str(config['host']) + ':' + str(config['port']))
        dump(config, folder)

    for i in range(peers_length):
        config = generate_peer_config(i, bns)
        dump(config, folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a gossip node')
    parser.add_argument('--folder', help='Network folder', default='network')
    parser.add_argument('--peer', type=int, help='Number of full nodes', default='10')
    parser.add_argument('--bn', type=int, help='Number of bootstrap nodes', default='3')
    parser.add_argument('--byzantine_bn', type=int, help='Number of byzantine bn', default='0')
    parser.add_argument('--byzantine_peer', type=int, help='Number of byzantine full nodes', default='0')
    parser.add_argument('--max_msg_drop', type=int, help='Percentage (0 to 100) of message lost/dropped', default='0')
    parser.add_argument('--peers_dropping_msg', type=int, help='Percentage of peers dropping messages', default='0')
    args = parser.parse_args()

    generate_network(args.peer, args.bn, args.byzantine_bn, args.byzantine_peer, args.folder)
