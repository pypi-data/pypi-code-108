import glob
import os
from os.path import expanduser
from datetime import date, timedelta
import yaml
from yaml.loader import SafeLoader
import click
import logging
import smtplib
from email.message import EmailMessage

home = expanduser("~")


def trace():
    var = "------------------------------------------------------------------------"
    return var


def create_yaml(dictionary, date, path):
    """Recebe um dicionario e uma data para montar o arquivo yaml"""
    if os.path.exists(output_yaml_file()):
        full_path = os.path.join(output_yaml_file(), f"{date}.yml")
        if len(dictionary["arquivos"]) > 0:
            with open(full_path, "w") as yaml_file:
                yaml.dump(dictionary, yaml_file, default_flow_style=False)
            click.echo(f"{trace()}\nArquivo exportado: {full_path}\n{trace()}")
            logging.info(f"Arquivo exportado: {full_path}")
            logging.debug(
                f"Função create_yaml recebeu a diretório {path} e a data: {date}"
            )
        else:
            click.echo(
                f"{trace()}\nNão há arquivos no diretório {path}\n{trace()}"
            )
            logging.warning(f"Não há arquivos no diretório {path}")
    else:
        click.echo(
            f"{trace()}\nDiretório não encontrado: {output_yaml_file()}"
        )
        logging.error(f"Diretório não encontrado: {output_yaml_file()}")
        click.echo(
            f"{trace()}\nExecutar o comando: python3 -m file_retention install\n{trace()}"
        )
        logging.warning(
            f"Executar o comando: python3 -m file_retention install"
        )


def get_files(fullpath, extension):
    """Recebe um diretorio e coleta todos os arquivos que existe no diretorio recursivamente e salva em uma lista"""
    values = [
        f for f in glob.glob(f"{fullpath}**/*.{extension}", recursive=True)
    ]
    count = len(values)
    click.echo(f"{trace()}\n{count} arquivos encontrados!")
    logging.info(f"{count} arquivos encontrados!")
    return values


def create_dict(files, path):
    """Recebe uma data e cria um dicionario com a data e a lista de arquivos encontrados na funcao get_files()"""
    if type(files) is list:
        dicts = {}
        dicts["arquivos"] = files
        logging.info(f"Dicionario criado com sucesso")
        return dicts
    else:
        click.echo(f"Existe algum erro na lista de arquivos")
        return {}


def read_yaml(date, key):
    """Recebe uma data e uma chave para ler o arquivo yaml"""
    full_path = os.path.join(output_yaml_file(), f"{date}.yml")
    if os.path.exists(full_path):
        click.echo(f"{trace()}\nArquivo encontrado: {full_path}")
        logging.info(f"Arquivo encontrado: {full_path}")
        with open(full_path, "r") as yaml_file:
            data = yaml.load(yaml_file, Loader=SafeLoader)
            if type(data) is dict:
                data = data[key]
        return data


def delete_files(date, file_list, retention):
    """Recebe uma data deleta os arquivos consultando o yaml ~/.file_retention/yyyy-mm-dd.yml"""
    filename = os.path.join(output_yaml_file(), f"{date}.yml")
    if os.path.exists(filename) and type(file_list) is list:
        click.echo(
            f"{trace()}\nArquivos de {retention} ({date}) dias atrás serão excluídos!!\n{trace()}"
        )
        logging.info(
            f"Arquivos de {retention} ({date}) dias atrás serão excluídos!! "
        )
        for f in file_list:
            if os.path.exists(f):
                os.remove(f"{f}")
                click.echo(f"Arquivo removido: {f}")
            else:
                click.echo(f"O Arquivo {f} não existe mais")
        click.echo(
            f"{trace()}\n{len(file_list)} arquivos no yaml: {filename}\n{trace()}"
        )
        logging.info(f"{len(file_list)} arquivos no yaml: {filename}")
    elif os.path.exists(filename) is False:
        click.echo(f"{trace()}\nArquivo não existe: {filename}\n{trace()}")
        logging.error(f"Arquivo não existe: {filename}")
    elif type(file_list) is not list:
        click.echo(f"{trace()}\nErro no yaml: {filename}\n{trace()}")
        logging.error(f"Erro no yaml: {filename}")
    else:
        click.echo(f"{trace()}\nO arquivo {filename} não existe.\n{trace()}")


def send_mail(filename, retention):
    days_ago = today() - timedelta(days=retention)
    email_message = f"""
Os arquivos excluidos estao listados no arquivo: {output_yaml_file()}/{days_ago}.yml
Os arquivos coletados no dia de hoje estao no arquivo {output_yaml_file()}/{today()}.yml
"""
    if os.path.exists(filename):
        files_ago = read_yaml(days_ago, "arquivos")
        with open(filename, "r") as yaml_file:
            try:
                data = yaml.load(yaml_file, Loader=SafeLoader)
                msg = EmailMessage()
                msg["subject"] = data["subject"]
                msg["from"] = data["sender"]
                msg["to"] = data["receiver"]
                msg.set_content(email_message)
                with smtplib.SMTP(data["server"], data["port"]) as smtp:
                    smtp.send_message(msg)
                click.echo(f"{trace()}\nEmail enviado!!\n{trace()}")
                logging.info(f"Email enviado!!\n{trace()}")
            except (
                ConnectionRefusedError,
                smtplib.SMTPServerDisconnected,
                TypeError,
                KeyError,
            ) as error:
                click.echo(f"{trace()}\nErro ao enviar o e-mail!!\n{trace()}")
                click.echo(
                    f"Verificar arquivo de configuração: {filename}\n{trace()}"
                )
                logging.error(
                    f"Erro ao enviar o e-mail!! Verificar arquivo de configuração: {filename}"
                )
                logging.error(error)
    else:
        click.echo(
            f"{trace()}\nArquivo {filename} de configuração não encontado.\n{trace()}"
        )
        logging.error(f"Arquivo {filename} de configuração não encontado.")


def today():
    today = date.today()
    return today


def output_yaml_file():
    home = expanduser("~")
    output_yaml = os.path.join(home, ".file_retention")
    return output_yaml


def setup():
    output_mail_config = os.path.join(home, ".file_retention", "mail.yml")
    mail_config = {
        "sender": "",
        "receiver": "",
        "password": "",
        "subject": "Arquivos que serao excluidos hoje",
        "server": "",
        "port": 25,
    }
    if os.path.exists(output_yaml_file()) is False:
        os.makedirs(output_yaml_file(), exist_ok=True)
        click.echo(
            f"{trace()}\nDiretório criado: {output_yaml_file()}\n{trace()}"
        )
    else:
        click.echo(f"{trace()}\nDiretório já existe: {output_yaml_file()}")

    if os.path.exists(output_mail_config) is False:
        with open(output_mail_config, "w") as yaml_file:
            yaml.dump(mail_config, yaml_file, default_flow_style=False)
        click.echo(
            f"Arquivo de configuração criado: {output_mail_config}\n{trace()}"
        )
    else:
        click.echo(
            f"{trace()}\nArquivo de configuração já existe: {output_mail_config}\n{trace()}"
        )
