import argparse
# import template

parser = argparse.ArgumentParser(description='Spectral Subtraction')

parser.add_argument('--name', required=True,
                    help='The name of expriment')
parser.add_argument('--noise_db', required=True,type=int,
                    help='The noise_db')
parser.add_argument('--input_dir', required=True,
                    help='The input signal')

parser.add_argument('--inc', default=160,type=int,
                    help='The inc size')
parser.add_argument('--wlen', default=400,type=int,
                    help='The window len')
parser.add_argument('--a_in', default=4,type=int,
                    help='The a coeffcient')
parser.add_argument('--b_in', default=0.001,type=float,
                    help='The b coeffcient')
parser.add_argument('--NIS', default=23,type=int,
                    help='The NIS')
parser.add_argument('--quantizer', default=2**32,type=int,
                    help='The quantizer of scale')

parser.add_argument('--debug', action='store_true')
args = parser.parse_args()



