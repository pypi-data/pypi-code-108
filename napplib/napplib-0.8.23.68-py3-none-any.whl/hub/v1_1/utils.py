import datetime
import re
import pandas as pd
import typing as T
import patoolib
import logging
from numbers import Number
from zipfile import ZipFile
from pathlib import Path

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

class Utils:
    @classmethod
    def create_values(self, value, tp):
        """
        Foi criado essa funcao devido a estrutura do nosso hub, em alguns casos temos que passar da seguinte forma:
        {'field': {'String': 'value', 'Valid': True}}
        Essa funcao cria o par de chaves e atribui seus tipos para ser atribuido no body de maneira correta.
        """
        pairKey = dict()  
        if tp == 'String':
            pairKey[tp] = str(value) if value != '' and value != None else ''
        elif tp == 'Int32':
            pairKey[tp] = int(value) if value != '' and value != None else 0
        elif tp == 'Int64':
            pairKey[tp] = int(value) if value != '' and value != None else 0
        elif tp == 'Float64':
            pairKey[tp] = float(value) if value != '' and value != None else 0  
        elif tp == 'Boolean':
            pairKey[tp] = bool(value) if value != '' and value != None else False
        pairKey['Valid'] = True if value != '' and value != None else False  
        return pairKey
    
    @classmethod
    def normalize_datetime(self, date):
        new_dt = date
        if new_dt and new_dt != '':
            if len(new_dt) > 25:
                # Eg: 2020-10-14T14:24:57.789000   
                new_dt = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                new_dt = new_dt.strftime('%d/%m/%Y %H:%M:%S')
            elif len(new_dt) == 25:
                # 2015-01-09T22:00:00-02:00
                new_dt = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                new_dt = new_dt.strftime('%d/%m/%Y %H:%M:%S')
            elif len(new_dt) == 10:
                # 1995-01-01
                try:
                    new_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
                    new_dt = new_dt.strftime('%d/%m/%Y')
                except:
                    new_dt = datetime.datetime.strptime(date, '%d-%m-%Y')
                    new_dt = new_dt.strftime('%d/%m/%Y')
            elif len(new_dt) == 19:
                # print(new_dt)
                new_dt = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                new_dt = new_dt.strftime('%d/%m/%Y %H:%M:%S')
        return new_dt

    @classmethod
    def aggregate_to_new_collumn(self,target_file, by, target, separator, columns, convert_columns=None, header=None, error_bad_lines=True, encoding='latin-1', drop_duplicated=False) -> list:
        csv_data = pd.read_csv(
            target_file,
            sep=separator,
            encoding=encoding,
            names=columns,
            index_col=False,
            header=header,
            error_bad_lines=error_bad_lines,
        )
        
        df = pd.DataFrame(columns=columns, data = csv_data)
        if drop_duplicated:
            df = df.drop_duplicates(keep='first')

        if convert_columns:
            for column in convert_columns:
                df[column] = df[column].apply(lambda x: x.strip() if isinstance(x, str) else x).replace('', 0).replace('None', 0)
                try:
                    df = df.replace(',','.', regex=True).astype({column: float})
                except:
                    df = df.astype({column: float})
        
        df_ag = df.groupby(by=[by])[target].sum()

        df_f = pd.merge(df,df_ag, left_on=by, right_index=True)
        
        return df_f.values.tolist()
    
    @classmethod
    def normalize_date(self, text, formats=None):
        """TODO: possibilitar o reconhecimento
        dos tipos de dados mais usados, e parametrizar
        casos ambiguos
        Args:
        - text: String contendo a data.
        - formats: uma string ou lista de strings contendo o formato da data.
        '01/09/2019' -> '2019-09-01 00:00:00'
        '01-09-2019' -> '2019-09-01 00:00:00'
        '2019/09/01' -> '2019-09-01 00:00:00'
        '2019-09-01' -> '2019-09-01 00:00:00'
        '01/09/19' -> '2019-09-01 00:00:00'
        '01/09/2019 10:50' -> '2019-09-01 10:50:00'
        """
        formats_date = [
            '%d/%m/%Y', '%d/%m/%y', '%d/%m/%Y %H', '%d/%m/%y %H', '%d/%m/%Y %H:%M', '%d/%m/%y %H:%M',
            '%d/%m/%Y %H:%M:%S', '%d/%m/%y %H:%M:%S', '%d/%m/%Y %H:%M:%S.%f', '%d/%m/%y %H:%M:%S.%f',
            '%Y/%m/%d', '%Y/%m/%d %H', '%y/%m/%d %H', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M',
            '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M:%S.%f', '%y/%m/%d %H:%M:%S.%f',
            '%d-%m-%Y', '%d-%m-%y', '%d-%m-%Y %H', '%d-%m-%y %H', '%d-%m-%Y %H:%M', '%d-%m-%y %H:%M',
            '%d-%m-%Y %H:%M:%S', '%d-%m-%y %H:%M:%S', '%d-%m-%Y %H:%M:%S.%f', '%d-%m-%y %H:%M:%S.%f',
            '%Y-%m-%d', '%Y-%m-%d %H', '%y-%m-%d %H', '%Y-%m-%d %H:%M', '%y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S', '%y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S', '%d-%m-%YT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f','%d-%b-%Y.%H:%M:%S', 
            '%Y-%m-%d%H:%M:%S','%Y%m%d%H%M%S','%Y-%m-%d%H%M%S', '%Y%m%d %H:%M:%S', '%Y%m%d %H:%M',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]

        if formats:
            if isinstance(formats, str):
                formats_date = [formats]
            else:
                formats_date = formats

        if isinstance(text, datetime.datetime):
            return text
        elif isinstance(text, dict):
            text = text['String']

        text = text.strip()

        results = []

        for form in formats_date:
            try:
                results.append(datetime.datetime.strptime(text, form))
            except ValueError:
                continue

        if results:
            if len(results) > 1:
                print(f'este é um caso abíguo: "{text}"" - {results}. Verificar Formato correto.')
                raise ValueError()
            result = results[0]
        else:
            print(f'Não foi possível converter a data "{text}", verificar o se é uma data e formato válido')
            raise ValueError()

        return result
    
    @classmethod
    def normaliza_hub_server(server):
        """[summary]

        Args:
            server ([type]): [description]

        Returns:
            [type]: [description]
        """
        if not '.nappsolutions.com' in server:
            server = f"https://{server}.nappsolutions.com"
        return server

    @classmethod
    def normalize_str(self, 
        text: T.Union[str, None],
        translate_spaces_to: str = '\x20',
        normalize_case: bool = True,
        white_list: str = '',) -> str:
        """Normaliza strings, removendo pontuação e acentuação e arrumando espaçamento

        Usar para comparar títulos de colunas em tabelas, e outras entradas
        que podem ter diferenças de digitação.
        White-list: string com caracteres de pontuação que devem ser mantidos.
        (Não funciona para caracteres acentuados)
        """
        import unicodedata
        import string

        valid_chars = string.ascii_lowercase + string.digits + " " + white_list

        if not text:
            return ""

        # Removes extra spaces:
        text = text.strip()

        if normalize_case:
            text = text.lower()

        # removes accented characters
        text = unicodedata.normalize("NFKD", text).encode("ASCII", errors="ignore").decode("ASCII")

        # Convert all white-space chars (\n\t,\x20 + strange unicode spacings) to space (\x20)
        text = re.sub("\s", "\x20", text, flags=re.MULTILINE)

        # remove non-white-listed chars:
        text = "".join(char for char in text if char in valid_chars)

        # coaslesce all space sequences to a single space and translate space character:
        text = re.sub("\s+", translate_spaces_to, text)

        return text

    @classmethod
    def unzip_file(self, file, extension=None):
        file = Path(file)
        folder = file.parent
        zip_obj = ZipFile(file)
        try:
            for name in zip_obj.namelist():
                if ".." in name:
                    warnn = 'Possivel tentativa de implantar malware'
                    logger.warn(
                        f"Atenção: arquivo com '..' no nome dentro de arquivo zip {file.absolute()}. {warnn}")
                    continue
                if extension and not name.lower().endswith(extension.lower()):
                    logger.debug(f"Arquivo inválido dentro de {file}: {name}")
                    continue
                zip_obj.extract(name, folder)
        except Exception as error:
            logger.error(f"Erro ao extrair conteúdos do arquivo {file} - {error}.")
            raise
        else:
            file.unlink()

    @classmethod
    def zip_files(self, files, folder_output, name_zip='files.zip'):
        with ZipFile(f'{folder_output}/{name_zip}', 'w') as zip:
                for file in files:
                    zip.write(file)

    @classmethod
    def extract_file(self, file, output=None):
        file = Path(file)
        outdir = output or file.absolute().parents[0]
        patoolib.extract_archive(str(file), outdir=str(outdir))

    @classmethod
    def compact_files(self, files, output, name='files', extension='zip'):
        files_normalized = []
        for file in files:
            file = str(Path(file).absolute())
            files_normalized.append(file)
        if extension.startswith('.'):
            extension = extension[1:]
        name_file = Path(f'{name}.{extension}')
        outpath = str(Path(output).absolute() / name_file)
        patoolib.create_archive(outpath, files_normalized)

    @classmethod
    def normalize_monetary_value(self,
        text: str,
        output_sep: str = ".",
        input_sep: T.Optional[str] = None,
        monetary_prefix: T.Optional[str] = None,
        ) -> str:
        
        r"""Recebe qualquer string com um valor numérico,
        e devolve na forma "nnnn.mm".
        Args:
            - text: String contendo valor a extrair
            - output_sep: Separador decimal para a saída (padrão: ".")
            - input_sep: Separador decimal usado nos dados de entrada.
                        Por padrão a função tenta detectar o separador entre "." e ",",
                        mas nos casos em que isso geraria ambiguidade, levanta um ValueError
            - monetary_prefix: Expressão regular com o prefixo monetário opcional para o valor.
                Por padrão: '([Rr]?\\$|BRL|brl)' que casa com r$, R$, $, brl ou BRL
                (O prefixo sempre é opcional, e olhado no começo da string)
        Exemplos:
        'R$ 140,00' -> '140.00'
        '$140.00' -> '140.00'
        ' 140,0' -> '140.00'
        '140.'' -> '140.00'
        '140' -> '140.00'
        '145.343,23' -> '145323.00'
        '140.0000',
        '140,000' e
        '140.234' -> ValueError: Valor ambiguo passe o parametro "input_sep" para desambiguar
        '140,234,23' -> ValueError: mais de um separador
        '140,234.23' -> "1401234.23" (veja os arquivos de testes para mais casos)

        """
        if isinstance(text, Number):
            return f"{text:.02f}"

        if not text:
            text = "0"
        text = text.strip()

        # find input decimal separator:
        if not input_sep:
            input_sep_expr = r'[\.,]'

        else:
            input_sep_expr = re.escape(input_sep)
        # Busca separador decimal nas três últimas posições do texto:
        cents_expr = fr"({input_sep_expr})(\d{{0,2}})"
        cents_match = re.search(cents_expr, text[-3:])

        if cents_match:
            # Garante duas casas depois da vírgula
            # Operados > na linha abaixo estava colocando um 0 antes do digito
            # Em cados com 1 casa decimal 2173.2 estava transformando em 2173.02
            # Inverti para < para que fique 2173.20 certo.
            cents = f"""{cents_match.groups()[1]:<02s}"""
            found_sep = cents_match.groups()[0]
            try:
                integer_part, _ = text.split(found_sep)
            except ValueError:
                raise ValueError(f"Mais de um separador decimal no valor: {text}")

        elif not input_sep:
            # Se não foi passado um separador decimal explícito,
            # e houver um "." ou "," fora do lugar, ValueError:
            if re.search(input_sep_expr, text):
                raise ValueError(f"Valor monetário ambíguo: {text}. Passe o separador explicitamente")
            integer_part = text
            cents = "00"
        else:
            # Mais casas decimais do que o esperado, mas o separador é explícito
            separadores = text.count(input_sep)
            if separadores > 1:
                raise ValueError(f"Valor monetário mal formatado: {text}")
            elif separadores == 0:
                integer_part = text
                cents = "00"
            else:
                integer_part, cents_part = text.split(input_sep)
                # Arredondar para apenas duas casas de centavos:
                cents_int = int(cents_part[0:2]) + int(int(cents_part[2]) >= 5)
                cents = f"{cents_int:02d}"

        if not monetary_prefix:
            # Prefixo default bate com r$, R$, $, brl, BRL
            monetary_prefix = r'([Rr]?\$|BRL|brl)'
        prefix_found = re.match(monetary_prefix, integer_part)
        if prefix_found:
            integer_part = integer_part[prefix_found.end():]

        digits = ""
        signal = ""
        for char in integer_part:
            if char in "0123456789":
                digits += char
            elif char in "-+":
                if digits or signal:
                    raise ValueError(f"Valor monetário mal formatado: {text}")
                signal = char
            elif char == " ":
                if digits:
                    raise ValueError(f"Valor monetário mal formatado: {text}")
            elif char not in "+-,.":
                raise ValueError(f"Valor monetário mal formatado: {text}")

        if signal == '+':
            signal = ''

        if not digits:
            digits = "0"

        value = f"{signal}{digits}{output_sep}{cents}"
        if value == "-0.00":
            value = "0.00"
        return value
