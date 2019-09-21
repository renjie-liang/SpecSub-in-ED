import argparse
# import template

parser = argparse.ArgumentParser(description='Spectral Subtraction')

parser.add_argument('--input', required=True,
                    help='The input signal')
parser.add_argument('--output', required=True,
                    help='The output signal')

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


args = parser.parse_args()



