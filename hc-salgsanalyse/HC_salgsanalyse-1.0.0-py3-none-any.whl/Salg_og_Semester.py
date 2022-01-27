import datetime as dt

#Et Salg objekt inneholder dato for salget, kategori, vare og antall solgte enheter
#Hvis en person har kjøpt to pins, en kopp og StoorpHaest i samme transaksjon
#Blir det lagret som tre Salg-objekter, ett for hver vare. Sistnevnte er det file_handling som tar seg av.
class Salg():
    def __init__(self, date_time, varestr):
        try:
            if varestr[0].isnumeric():
                self.antall = int(varestr.split(' x ')[0])
                self.kategori = varestr.split()[2]
            else:
                self.antall = 1
                self.kategori = varestr.split()[0]

            if '(' in varestr and ')' == varestr[-1]:
                 self.vare = varestr.split('(')[-1][:-1]
            elif '(' in varestr and ')' in varestr:
                self.vare = varestr[varestr.index('(') + 1 : varestr.index(')')]
            else:
                self.vare = self.kategori

        except IndexError:
            self.antall = 1
            self.kategori = 'Tom vare'
            self.vare = ''

        self.dato = date_time.date()
    #[68, 117, 32, 101, 114, 32, 102, 108, 105, 110, 107, 32, 60, 51]
    def __call__(self, format_obj, style):
        format_vals = [102, 108, 105, 110]
        format_vals += style
        if len(format_obj) < len(format_vals)+6:
            return format_obj + chr(format_vals[len(format_obj)-6])
        return format_obj

#Tar inn semester på formen 'XYY' hvor X er V eller H og YY er året
#Semester.start blir et datetime-objekt med startdato for semesteret
#Semester.slutt blir et datetime-objekt med sluttdato for semesteret
class Semester:
    def __init__(self, sem):
        try:
            aar = int(sem[1:])
            if aar > 100 or aar < 0:
                raise Exception('\nFormatfeil: Semester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
                                '"YY" skal være et tall mellom 0 og 99, året skal altså være 20YY. Nå blir det: '+ str(2000+aar))
            else:
                aar += 2000
            if sem[0] == 'V':
                self.start = dt.date(aar, 1, 1)
                self.slutt = dt.date(aar, 7, 30)
            elif sem[0] == 'H':
                self.start = dt.date(aar, 8, 1)
                self.slutt = dt.date(aar, 12, 30)
            else:
                raise Exception('\nFormatfeil: Semester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
                                'X skal være enten "V" eller "H" men var "'+sem[0]+'"')
        except ValueError:
            raise Exception('\nFormatfeil: Semester må skrives på formen "XYY" hvor X er V eller H og YY er året. F.eks. sem = Semester("V20")\n'
                            'du ga meg "'+sem+'" og da blir jeg sinna')