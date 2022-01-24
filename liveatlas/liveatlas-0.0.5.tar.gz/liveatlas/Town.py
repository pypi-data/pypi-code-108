import re


class Town:
    def __init__(self, html):
        self.raw_html = html
        self.desc = self.parse_desc()
        # todo: try this: iterate over parsed[] once and check for "tags" (i.e Culture -, Residents -, etc.). Then
        #      get that value from index(tag) i + 1. Check that value to see if it is in the right format, if true,
        #      assign it to the corresponding self variable. Handle nations explicitly.
        #
        # There are 32 (2^5) possible town type combinations. The following are values that can be missing from a town tag:
        # N = has nation
        # O = is occupied
        # C = has culture
        # R = has resources
        # M = has members
        # To avoid a large cascading conditional to handle this, we will iterate over the list once and search for
        # key words, which will be added to a list of consistent sorting

        # town_data = [None] * 11
        # self.nation = town_data[0]
        # self.occupied = town_data[1]
        # self.mayor = town_data[2]
        # self.peaceful = town_data[3]
        # self.culture = town_data[4]
        # self.board = town_data[5]
        # self.bank = town_data[6]
        # self.upkeep = town_data[7]
        # self.founded = town_data[8]
        # self.resources = town_data[9]
        # self.population = town_data[10]

        # for tag in parsed:
        #     match tag:
        #         case tag.startswith("Member of "):
        #             self.nation = tag.removeprefix("Member of ")
        #         case

 

    def parse_desc(self):
        html = self.raw_html
        html = re.split("<.*?>", html)
        parsed = []
        for i in html:
            if i == '' or i == ' ' or i == '"' or i == "'":
                pass
            else:
                parsed.append(i)

        print(parsed)
        print(len(parsed))

        return parsed


"<div class=\"regioninfo\"><div class=\"infowindow\"><div align =\"center\"><span style=\"font-size:150%;\"><\/span> " \
"<br \/> <span style=\"font-size:200%;\">Nuovo-Porto<\/span> <br \/> Occupying Nation - <span style=\"font-weight:bold;" \
"\">Oceanic_Empire<\/span> <br \/> Mayor - <span style=\"font-weight:bold;\">disco__devil<\/span> <br \/> <img src = " \
"\"https:\/\/cravatar.eu\/helmhead\/disco__devil\/190.png\" style=\"width:100px;height:100px;\"> <\/div> <br \/> \u2022 " \
"Peaceful? <span style=\"font-weight:bold;\">true<\/span> <br \/> \u2022 Culture - <span style=\"font-weight:bold;\">" \
"Italian-creole<\/span> <br \/> \u2022 Board - <span style=\"font-weight:bold;\">The Land Between Seas!<\/span> <br \/> " \
"\u2022 Bank - <span style=\"font-weight:bold;\">$335<\/span> <br \/> \u2022 Upkeep - <span style=\"font-weight:bold;" \
"\">$6<\/span> <br \/> \u2022 Founded - <span style=\"font-weight:bold;\">Dec 22 2021<\/span> <br \/> \u2022 Resources" \
" - <span style=\"font-weight:bold;\"><\/span> <br \/> \u2022 Residents (1) - <span style=\"font-weight:bold;\"" \
">disco__devil<\/span> <\/div><\/div>"

# split by html tags
