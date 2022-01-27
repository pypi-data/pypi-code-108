# imports all CLI clients.
import vandal
from vandal.objects import montecarlo

# runs the main CLI client.
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--entry', help = 'Enter options', type = str,
    choices = ['montecarlo'])
    args = parser.parse_args()

    if args.entry == 'montecarlo':
        vandal.objects.montecarlo.Main()

