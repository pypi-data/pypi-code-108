import argparse
from broker_clients import Balances
from broker_clients import session


def parse_args():
    parser = argparse.ArgumentParser(prog='module')
    #parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(dest='module', help='sub-command help')

    parser_a = subparsers.add_parser('create_balance', help='Create a balance')
    parser_a.add_argument('--name', type=str, dest='name', required=True, help='Balance name')
    parser_a.add_argument('--symbol', type=str, dest='symbol', required=True, help='Balance symbol')
    parser_a.add_argument('--time_frame', type=str, dest='time_frame', required=True, help='Balance time frame')
    parser_a.add_argument('--free', type=float, dest='free', required=True, help='Balance budget')

    #parser_b = subparsers.add_parser('b', help='b help')
    #parser_b.add_argument('--baz', choices='XYZ', help='baz help')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    if args.module == 'create_balance':
        balance = session.query(Balances).filter_by(name=args.name).first()
        if not balance:
            balance = Balances(name=args.name,
                               symbol=args.symbol,
                               time_frame=args.time_frame,
                               free=args.free,
                               locked=0)
            session.add(balance)
            session.commit()
            print(balance)
        else:
            print('Balance name already exists')

