import argparse
import hashlib
import pickle
import random
from math import ceil

import yaml
from fastecdsa import keys, curve
from fastecdsa.point import Point

CURVE = curve.secp256k1


def get_level_of_byz(is_byz, mean_lvl_byz, std_lvl_byz):
    return random.normalvariate(mean_lvl_byz, std_lvl_byz) if is_byz else 0


def get_bns(bns, reg_number):
    return bns if reg_number >= len(bns) else random.sample(bns, k=reg_number)


def generate_peer_config(i: int, bns, byzantine: bool, altruistic: bool, reg_number: int, mean_lvl_byz, std_lvl_byz):
    return {
        'host': '0.0.0.0',
        'port': 10000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'bn_nodes': get_bns(bns, reg_number),
        'id': 10000 + i,
        'log_level': 1,
        'byzantine': get_level_of_byz(byzantine, mean_lvl_byz, std_lvl_byz),
        'altruistic': altruistic,
    }


def generate_bn_config(i, epoch_time, reg_difficulty):
    return {
        'host': '0.0.0.0',
        'port': 30000 + i,
        'private_key': keys.gen_private_key(curve.secp256k1),
        'id': 30000 + i,
        'log_level': 1,
        'epoch_timeout': epoch_time,
        'min_difficulty': reg_difficulty
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
    return random.normalvariate(0, 1) < perc_byzantine


def is_rational(perc_rational):
    return random.normalvariate(0, 1) < perc_rational


def dump_public_key(public_key: Point):
    return '{}.{}.{}'.format(public_key.x, public_key.y, public_key.curve.name)


def dump_ip_port(config):
    return '{}:{}'.format(str(config['host']), str(config['port']))


def dump_bn_info(config):
    bn_address = dump_ip_port(config)
    pk = keys.get_public_key(config['private_key'], CURVE)
    public_key = dump_public_key(pk)
    return '{}, {}'.format(bn_address, public_key)


def generate_network(folder, total_full_nodes, total_bn_nodes, reg_number, perc_byz_full_nodes, perc_rat_full_nodes, mean_lvl_byz, std_lvl_byz, epoch_time_bn, difficulty_reg_bn):
    bns = []

    for bn in range(total_bn_nodes):
        config = generate_bn_config(bn, epoch_time_bn, difficulty_reg_bn)
        dump(config, folder)
        bn_info = dump_bn_info(config)
        bns.append(bn_info)

    for peer in range(total_full_nodes):
        is_byz = is_byzantine(perc_byz_full_nodes)
        is_rat = is_byzantine(perc_rat_full_nodes) and not is_byz

        config = generate_peer_config(peer, bns, is_byz, is_rat, reg_number, mean_lvl_byz, std_lvl_byz)
        dump(config, folder)


def generate_random_data(folder, total_transactions, mean_size_txs, std_size_txs):
    transactions = []
    for i in range(total_transactions):
        b = ceil(random.normalvariate(mean_size_txs, std_size_txs))
        transaction = bytearray(random.getrandbits(8) for _ in range(b))
        full_id = hashlib.new('sha256', transaction).hexdigest()
        short_id = hashlib.new('ripemd160', transaction).hexdigest()
        transactions.append([transaction.hex().strip(), full_id, short_id])
    with open(folder + '/data.data', 'wb') as the_file:
        the_file.write(pickle.dumps(transactions))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a gossip node.')
    parser.add_argument('--folder', help='Network folder', default='../network')
    parser.add_argument('--seed', help='Network seed generation', default=1337)
    parser.add_argument('--total-full-nodes', type=int, help='Number of full nodes', default=10)
    parser.add_argument('--total-bn-nodes', type=int, help='Number of bootstrap nodes', default=2)
    parser.add_argument('--reg_number', type=int, help='Number of bn substriptions per full_nodes', default=2)
    parser.add_argument('--perc-byz-full-nodes', type=int, help='Percentage of byzantine full nodes, Max 1, Min 0', default=0)
    parser.add_argument('--perc-rational-full-nodes', type=int, help='Percentage of rational full nodes, Max 1, Min 0',
                        default=0)
    parser.add_argument('--mean-lvl-byz', type=int, help='Mean level of byzantines of full nodes. Max 1, Min 0.1', default=0)
    parser.add_argument('--std-lvl-byz', type=int, help='Standard deviation of level of byzantines of full nodes. Max 1, Min 0.1', default=0)
    parser.add_argument('--epoch-time-bn', type=int, help='Time between each epoch', default=10)
    parser.add_argument('--difficulty-reg-bn', type=float, help='Difficulty to get a registration', default=1e-5)
    parser.add_argument('--total-transactions', type=int, help='Number of transactions', default=500)
    parser.add_argument('--mean-size-txs', type=int, help='Mean byte-size of transactions. ', default=226)
    parser.add_argument('--std-size_txs', type=int, help='Standard deviation of transactions byte-sze. Max 1, Min 0', default=1)
    args = parser.parse_args()

    random.seed(args.seed)

    assert(args.total_bn_nodes <= args.reg_number)
    assert(args.perc_byz_full_nodes + args.perc_rational_full_nodes <= 1)

    generate_network(args.folder, args.total_full_nodes, args.total_bn_nodes, args.reg_number, args.perc_byz_full_nodes, args.perc_rational_full_nodes, args.mean_lvl_byz, args.std_lvl_byz,
                     args.epoch_time_bn, args.difficulty_reg_bn)

    generate_random_data(args.folder, args.total_transactions, args.mean_size_txs, args.std_size_txs)
