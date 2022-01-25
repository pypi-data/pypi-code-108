import configparser


class Task:
    data = {}

    name = "name"

    contest = "contest"
    contest_preffix = "contest_preffix"

    # раздел
    section = "section"
    volume = "volume"
    volume_preffix = "volume_preffix"

    # краткое описание и сложность (1 - альфа, 2 - бетта и т.д.)
    hint = "hint"
    difficulty = "difficulty"

    # заметка (автор, год, источник, страница в интернете)
    note = "note"

    # ---- ограничения
    # по времени (мс)
    time_native = "time_native"
    time_javavm = "time_javavm"
    time_dotnet = "time_dotnet"
    time_custom = "time_custom"

    # по памяти (кб)
    memory_native = "memory_native"
    memory_javavm = "memory_javavm"
    memory_dotnet = "memory_dotnet"
    memory_custom = "memory_custom"

    # маска имен файлов тестов
    test_inputmask = "test_inputmask"
    test_patternmask = "test_patternmask"

    # название файла чекера
    checker_file = "checker_file"

    def get(self, key):
        return self.data[key]


def get_xml(info_file):
    task = Task()

    meta = configparser.ConfigParser()

    meta.read(info_file, encoding="utf-8")

    sects = ["MAIN", "LIMITS", "TESTS", "CHECKER"]

    for sect in sects:
        items = meta.items(sect)

        for item in items:
            task.data[item[0]] = item[1][1:-1]

    data = """<?xml version="1.0" encoding="windows-1251"?>
        <Problem generator="Contester 2.4">
            <Name lang="ru">""" + task.get(task.name) + """</Name>
            <Contest>
                <Name lang="ru">""" + task.get(task.contest) + """</Name>
            </Contest>

            <PreContest lang="ru">""" + task.get(task.contest_preffix) + """</PreContest>

            <Section>
                <Name lang="ru">""" + task.get(task.section) + """</Name>
                <Name lang="en">""" + task.get(task.section) + """</Name>
            </Section>

            <Volume>
                <Name lang="ru">""" + task.get(task.volume) + """</Name>
                <Name lang="en">""" + task.get(task.volume) + """</Name>
            </Volume>

            <PreVolume lang="ru">""" + task.get(task.volume_preffix) + """</PreVolume>

            <Hint lang="ru">""" + task.get(task.hint) + """</Hint>
            <Note lang="ru">""" + task.get(task.note) + """</Note>
            <Difficulty>""" + task.get(task.difficulty) + """</Difficulty>

            <TimeLimit platform="native">""" + task.get(task.time_native) + """</TimeLimit>
            <TimeLimit platform="javavm">""" + task.get(task.time_javavm) + """</TimeLimit>
            <TimeLimit platform="dotnet">""" + task.get(task.time_dotnet) + """</TimeLimit>
            <TimeLimit platform="custom">""" + task.get(task.time_custom) + """</TimeLimit>
            <MemoryLimit platform="native">""" + task.get(task.memory_native) + """</MemoryLimit>
            <MemoryLimit platform="javavm">""" + task.get(task.memory_javavm) + """</MemoryLimit>
            <MemoryLimit platform="dotnet">""" + task.get(task.memory_dotnet) + """</MemoryLimit>
            <MemoryLimit platform="custom">""" + task.get(task.memory_custom) + """</MemoryLimit>

            <AutoLimits>0</AutoLimits>
            <Statement lang="ru" src="statement.htm" />
            <TestList inputmask=" """ + task.get(task.test_inputmask) + """ " patternmask=" """ + task.get(task.test_patternmask) + """ " />
            <Judge><Checker src=" """ + task.get(task.checker_file) + """ " /></Judge>
        </Problem>
        """

    return data
