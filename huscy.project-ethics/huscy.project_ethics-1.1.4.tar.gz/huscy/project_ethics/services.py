from huscy.project_ethics.models import Ethic, EthicBoard, EthicFile


def create_ethic_board(name):
    return EthicBoard.objects.create(name=name)


def get_ethic_boards():
    return EthicBoard.objects.all()


def update_ethic_board(ethic_board, name):
    ethic_board.name = name
    ethic_board.save()
    return ethic_board


def create_ethic(project, ethic_board, code=''):
    return Ethic.objects.create(project=project, ethic_board=ethic_board, code=code)


def get_ethics(project):
    return Ethic.objects.filter(project=project)


def update_ethic(ethic, ethic_board, code):
    ethic.code = code
    ethic.ethic_board = ethic_board
    ethic.save()
    return ethic


def create_ethic_file(ethic, filehandle, filetype, creator, filename=''):
    filename = filename or filehandle.name.split('/')[-1]

    return EthicFile.objects.create(
        ethic=ethic,
        filehandle=filehandle,
        filename=filename,
        filetype=filetype,
        uploaded_by=creator.get_full_name(),
    )


def get_ethic_files(ethic):
    return EthicFile.objects.filter(ethic=ethic)


def update_ethic_file(ethic_file, filetype, filename):
    ethic_file.filetype = filetype
    ethic_file.filename = filename
    ethic_file.save()
    return ethic_file
