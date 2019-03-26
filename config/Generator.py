import argparse
import random
from math import floor

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
from fastecdsa.point import Point

CURVE = curve.secp256k1


def generate_peer_config(i: int, bn: list, byzantine, will_drop, drop_rate):
    return {
        'host': '0.0.0.0',
        'port': 10000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'bn_nodes': bn,
        'id': 10000 + i,
        'log_level': 1,
        'byzantine': byzantine,
        'percentage_message_drop': drop_rate,
        'is_dropping': will_drop
    }


def generate_bn_config(i, byzantine, will_drop, drop_rate):
    return {
        'host': '0.0.0.0',
        'port': 30000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'id': 30000 + i,
        'log_level': 1,
        'byzantine': byzantine,
        'percentage_message_drop': drop_rate,
        'is_dropping': will_drop
    }


def dump(config: dict, folder: str):
    network_folder = folder + '/' + str(config['id']) + '.yaml'
    with open(network_folder, "w+") as node:
        node.write(yaml.dump(config))


def get_drop_message_data(perc_message_drop, perc_max_message_drop):
    will_drop = random.uniform(0, 1) < perc_message_drop
    drop_rate = random.choice([i for i in range(perc_max_message_drop)]) if perc_max_message_drop > 0 else 0
    return will_drop, drop_rate


def is_byzantine(perc_byzantine):
    return random.uniform(0, 1) < perc_byzantine


def dump_public_key(public_key: Point):
    return '{}-{}-{}'.format(public_key.x, public_key.y, public_key.curve.name)


def dump_ip_port(config):
    return '{}:{}'.format(str(config['host']), str(config['port']))


def dump_bn_info(config):
    bn_address = dump_ip_port(config)
    pk = keys.get_public_key(config['private_key'], CURVE)
    public_key = dump_public_key(pk)
    return '{}, {}'.format(bn_address, public_key)


def generate_network(folder, total, perc_peers, perc_byzantine_peers, perc_byzantine_bn, perc_max_message_drop, perc_message_drop):
    n_of_peers = floor(total * perc_peers) + 1
    n_of_bn = floor(total * (1 - perc_peers)) + 1

    bns = []

    for bn in range(n_of_bn):
        will_drop, drop_rate = get_drop_message_data(perc_message_drop, perc_max_message_drop)
        will_byzantine = is_byzantine(perc_byzantine_bn)

        config = generate_bn_config(bn, will_byzantine, will_drop, drop_rate)
        dump(config, folder)
        bn_info = dump_bn_info(config)
        bns.append(bn_info)

    for peer in range(n_of_peers):
        will_drop, drop_rate = get_drop_message_data(perc_message_drop, perc_max_message_drop)
        will_byzantine = is_byzantine(perc_byzantine_peers)

        config = generate_peer_config(peer, bns, will_byzantine, will_drop, drop_rate)
        dump(config, folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a gossip node.')
    parser.add_argument('--folder', help='Network folder', default='network')
    parser.add_argument('--total', type=int, help='Number of full nodes')
    parser.add_argument('--peer', type=float, help='Percentage (0 to 1) of full nodes. Rest are bootstrap node.', default='0.9')
    parser.add_argument('--byzantine', type=int, help='Percentege (0 to 1) of byzantine full nodes.', default='0')
    parser.add_argument('--byzantine_bn', type=int, help='Percentege (0 to 1) of byzantine bootstrap nodes.', default='0')
    parser.add_argument('--max_msg_drop', type=int, help='Percentage (0 to 1) of message lost/dropped.', default='0')
    parser.add_argument('--peers_dropping_msg', type=int, help='Percentage (0 to 1) of peers dropping messages.', default='0')
    args = parser.parse_args()

    generate_network(args.folder, args.total, args.peer, args.byzantine, args.byzantine_bn, args.max_msg_drop, args.peers_dropping_msg)
