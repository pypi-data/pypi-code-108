import argparse
from pathlib import Path
import tensorflow as tf
import kessho.datasources.first_rate as fr


def create_thfp(argv=None):
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--symbols',
        dest='symbols',
        required=True,
        help='A comma-separated list of symbols to generate trading hour fingerprints for')
    
    arg_parser.add_argument(
        '--indir',
        dest='raw_data_path',
        required=True,
        default='.',
        help='The directory where the minute-wise ticker data files are stored')
    
    arg_parser.add_argument(
        '--outdir',
        dest='features_path',
        required=True,
        default='.',
        help='The directory where to write the resulting TFRecord files containing the features'
    )
   
    arg_parser.add_argument(
        '--weeks',
        dest='n_weeks',
        required=False,
        type=int,
        default=2,
        help='number of weeks to go back in tradinig hour history')
    
    arg_parser.add_argument(
        '--from-index',
        dest='from_index',
        required=False,
        type=int,
        default=None,
        help='Index within the input file to start from')
    
    arg_parser.add_argument(
        '--to-index',
        dest='to_index',
        type=int,
        required=False,
        default=None,
        help='Index within the input file to stop at')
    
    args, other_args = arg_parser.parse_known_args(argv)    
    
    raw_data_path = Path(args.raw_data_path)
    assert raw_data_path.exists(), f'{raw_data_path} does not exist.'
    
    features_path = Path(args.features_path)
    assert features_path.exists(), f'{features_path} does not exist.'

    assert args.n_weeks in [1, 2, 3], f'{n_weeks} weeks makes no sense. Choose 1, 2, or 3 weeks.'
    
    for symbol in args.symbols.split(','):
        minute_file = raw_data_path / f'{symbol}_1min.txt'
        if minute_file.exists():
            process_minute_file(minute_file, features_path,
                                args.n_weeks, args.from_index or 0, args.to_index or -1, symbol)
        else:
            print(f'{minute_file} does not exist. Continuing...')

            
def process_minute_file(minute_file: Path, features_path: Path,
                        n_weeks: int, from_index: int, to_index: int, symbol: str):
    
    print(f'processing {symbol}, file: {minute_file}')
    data = fr.MinuteCsv(minute_file, process=True, start=from_index, end=to_index)
    dates, features = data.compute_trading_hour_history_tensors(n_weeks=2)
    
    list_dates = list(dates)
    first_date = min(list_dates)
    last_date = max(list_dates)
    print(f'Computed {len(list_dates)} fingerprints from {first_date} to {last_date}')   

    output_file=str(features_path / f'{symbol}_THFP_{first_date}_{last_date}.tfrecord')
    print(f'Writing to {output_file}')

    ds = tf.data.Dataset.from_generator(
        lambda: features, output_types=tf.float16
    ).map(
        lambda r: tf.cast(r, dtype=tf.float16)
    ).map(tf.io.serialize_tensor)

    writer = tf.data.experimental.TFRecordWriter(output_file)
    writer.write(ds)    

    
if __name__ == '__main__':
    create_thfp()