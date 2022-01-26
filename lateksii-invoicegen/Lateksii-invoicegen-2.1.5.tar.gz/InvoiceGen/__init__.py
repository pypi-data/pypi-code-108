# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for c lasses, files, tool windows, actions, and settings.
import os
import sys
import PySimpleGUI as sg
import datetime as dt

fuksia_theme = {'BACKGROUND': '#db008b',
                'TEXT': '#fadcef',
                'INPUT': '#fadcef',
                'TEXT_INPUT': '#000000',
                'SCROLL': '#c7e78b',
                'BUTTON': ('#db008b', '#fadcef'),
                'PROGRESS': ('#01826B', '#D0D0D0'),
                'BORDER': 2,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

class Item:
    def __init__(self, q, n, p):
        self.quantity = int(q)
        self.name = n
        self.uprice = float(p)
        self.price = self.quantity*self.uprice

def referenceCalc(id):
    wages = [7, 3, 1]
    n = 1
    s = 0
    # Reverse order
    for i in range(len(id) - 1, -1, -1):
        s += int(id[i]) * wages[(n % 3) - 1]
        n += 1
    verify = 10 - s % 10
    if verify == 10:
        verify = 0
    return id + str(verify)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sg.theme_add_new("Fuksia",fuksia_theme)
    sg.theme("Fuksia")
    now = dt.date.today()
    items = []
    strlist = []
    layout = [
        [
        sg.Text("Lateksii ry laskupohjaeditori",font=20)
        ],
        # Invoice id and reference number
        [
        sg.Text("Laskun numero",size=(12,1)),
        sg.InputText(key = 'invoiceid',size=(6,1)),
        ],
        [
        sg.Text("Viitenumero",size=(12,1)),
        sg.InputText(key='reference',size=(6,1))
        ],
        [
        sg.Text("Maksuehto",size=(12,1)),
        sg.InputText("14",key='condition',size=(3,1))
        ],

        # Duedate and condition
        [
        sg.Text("Päivämäärä: ",size=(12,1)),
        sg.InputText(now.strftime("%d.%m.%Y"),key='date',size=(10,1))
        ],
        [
        sg.Text("Eräpäivä: ",size=(12,1)),
        sg.InputText((now+dt.timedelta(days=14)).strftime("%d.%m.%Y"),key='duedate',size=(10,1))
        ],
        # Address and receiver
        [
        sg.Text("Osoite",size=(12,1)),
        sg.Multiline(key="address",size=(40,4))
        ],
        [
        sg.Text("Vastaanottaja:",size=(12,1)),
        sg.InputText(size=(20,1),key='email')
        ],
        [
        sg.Text("Lisätiedot: ",size=(12,1)),
        sg.Multiline(key='info',size=(40,2))
        ],
        [
        sg.Text("Tuotteet: ",size=(12,1)),
        sg.Listbox(values=[],size=(40,5),key='items')
        ],
        [sg.Button("Lisää tuote",key='add'),sg.Button("Poista tuote"),sg.Button("OK")]
    ]


    # Create the window
    win1 = sg.Window("Demo", layout)
    win2_active = False
    # Create an event loop
    while True:
        ev1, vals1 = win1.read(timeout=100)
        if ev1 == 'OK':
            break
        if ev1 == sg.WIN_CLOSED:
            win1.close()
            sys.exit(0)

        if not win2_active and ev1 == 'add':
            win2_active = True
            layout2 = [
                [sg.Text("Lisää tuote:", font=20)],
                [
                    sg.Text("Lkm: ", font=20, size=(10, 1)),
                    sg.InputText("1", font=20, size=(4, 1), key='quantity')
                ],
                [
                    sg.Text("Kuvaus: ", font=20, size=(10, 1)),
                    sg.InputText("", font=20, size=(30, 1), key='info')
                ],
                [
                    sg.Text("Hinta: ", font=20, size=(10, 1)),
                    sg.InputText("", font=20, size=(6, 2), key='price')
                ],
                [sg.Button("Lisää", key='additem', font=20)]
            ]
            win2 = sg.Window('Window 2', layout2)
        # Jotai paskaa, vissiin se toinen ikkuna
        if win2_active:
            ev2, vals2 = win2.read(timeout= 100)
            if ev2 == 'additem':
                newitem = Item(vals2['quantity'],vals2['info'],vals2['price'])
                items.append(newitem)
                # String displayed on main window
                strlist.append("{} kpl, {}, {}€ ({:.2f}€)".format(newitem.quantity,newitem.name,newitem.uprice,newitem.price))

                win1['items'].update(values=strlist)
                win2_active = False
                win2.close()
            if ev2 == sg.WIN_CLOSED:
                win2_active = False
                win2.close()


    vals1['address'] = vals1['address'].replace('\n',r'\\')
    vals1['reference'] = referenceCalc(vals1['reference'])

    itemstr = ""
    itemsum = 0
    for item in items:
        itemstr += r" {} & {} & {:.2f} & {:.2f} \\ \hline".format(item.quantity, item.name, item.uprice, item.price).replace(".", ",")
        itemsum += item.price
    vals1['items'] = itemstr
    vals1['price'] = "{:.2f}".format(itemsum).replace(".", ",")

    invoiceDir = os.path.expanduser("~\\Documents\\InvoiceGen\\Invoices")

    if not os.path.exists(invoiceDir):
        os.makedirs(invoiceDir)

    filename = os.getcwd() + "\\cache\\" + "Lasku" + vals1.get('invoiceid')

    with open(sys.prefix+"\\res\\template.tex", "r", encoding="utf-8") as template:
        text = template.read()

        for key, value in vals1.items():
            text = text.replace("${}$".format(key), str(value))

        with open(filename + ".tex", "w", encoding="utf-8") as output:
            output.write(text)

    os.system("pdflatex -output-directory=" + os.getcwd() + "\\cache " + filename + ".tex")
    os.system("move " + filename + ".pdf " + invoiceDir)
    win1.close()


