from datetime import datetime
import logging, re, zipfile, glob
import pandas as pd




logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")


class Utils:
    @classmethod
    def create_csv(self, filename, items):
        try:
            data = []
            
            for item in items:
                data.append(item.__dict__)

            df = pd.DataFrame.from_dict(data)
            df.to_csv(filename, sep=';', index=False)

            logging.info(f'[NappClient2] File {filename} has been saved successfully')
        except Exception as e:
            logging.info(f'[NappClient2] Error to save file {filename} - {e}')


    @classmethod
    def create_zip(self, output_path, revision: int = 1):
        try:
            dt = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f'{output_path}/{dt}_r{revision}.zip'
            csvs = glob.glob(f'{output_path}/*.csv')
            
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipOnj:
                for file in csvs:
                    zipOnj.write(file, file.split('/')[-1])
            
            logging.info('[NappClient2] Zip files with success')
            return filename

        except Exception as e:
            logging.info(f'[NappClient2] Failed to zip files: {e}')
            return None

    @classmethod
    def convert_to_datetime(self, value):
        return re.sub(r'^(\d{2}).?(\d{2}).?(\d{4})([\sT])?(.*)$', r'$3-$2-$1 $5', value)


    @classmethod
    def convert_to_currency(self, value):
        if type(value) != str:
            return value

        # Find all occurrences
        matches = re.findall(r'[\.,]+', value)

        # For an occurrence
        if len(matches) == 1:
            return re.sub(r',', '.', value)

        # More than one
        if len(matches) > 1:
            count = len(matches)
            for match in matches:
                # Define replace pattern
                replace = ''

                # Decrement count
                count = count - 1
                if count == 0:
                    if match == ',':
                        replace = '.'
                    else:
                        break

                value = re.sub(f'\{match}', 
                    replace, 
                    value, 1)

        return value