from tableauscraper import TableauScraper as TS
import pandas as pd
from subprocess import run

def main():
    url="https://public.tableau.com/views/BarnardPublicDashboard/PUBLICDASHBOARD?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Fpublic.tableau.com%2F&:embed_code_version=3&:tabs=no&:toolbar=no&:animate_transition=yes&:display_static_image=no&:display_spinner=no&:display_overlay=yes&:display_count=yes&:language=en&publish=yes&:loadOrderID=0"
    file = __file__
    outpath = f"{file[:file.rfind('/')]}/covid-data.xlsx"

    ts = TS()
    ts.loads(url)
    wb = ts.getWorkbook()
    sp = wb.goToStoryPoint(storyPointId = 8)

    people_names = ["Faculty", "Staff", "Non-Residential Students", "Residential Students", "Other"]
    people = ["faculty", "staff", "nres", "res", "other"]
    headings = ["tests", "pos"]

    df = sp.worksheets[0].data
    weeks_col = [n[16:] for n in df.iloc[1:len(df.index)//10, -1]]
    outdf = pd.DataFrame({"Week Of": weeks_col})
    numrows = len(weeks_col)+1

    for i in range(10):
        outdf[f"{people[i//2]}-{headings[i%2]}"] = [int(n.replace(",","")) for n in df.iloc[(numrows*i)+1:numrows*(i+1), 4]]

    sheet_name = "data"
    writer = pd.ExcelWriter(outpath, engine="xlsxwriter")
    outdf.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook, sheet = writer.book, writer.sheets[sheet_name]

    tests_chart = workbook.add_chart({"type": "line"})
    pos_chart = workbook.add_chart({"type": "line"})

    for i in range(5):
        c = i*2 + 1
        tests_chart.add_series({
            'categories': [sheet_name, 1, 0, numrows, 0],
            'values': [sheet_name, 1, c, numrows, c],
            'name': people_names[i]
        })
        pos_chart.add_series({
            'categories': [sheet_name, 1, 0, numrows, 0],
            'values': [sheet_name, 1, c+1, numrows, c+1],
            'name': people_names[i]
        })

    tests_chart.set_size({"width": 960, "height": 480})
    tests_chart.set_title({"name": "# Covid Tests by Week"})
    tests_chart.set_x_axis({"name": "Week"}); tests_chart.set_y_axis({"name": "Number of Tests"})

    pos_chart.set_size({"width": 960, "height": 480})
    pos_chart.set_title({"name": "# Positive Cases by Week"})
    pos_chart.set_x_axis({"name": "Week"}); pos_chart.set_y_axis({"name": "Number Positive Cases"})

    sheet.insert_chart("M1", tests_chart)
    sheet.insert_chart("M25", pos_chart)

    writer.save()
    run(["open", outpath], capture_output=False)

