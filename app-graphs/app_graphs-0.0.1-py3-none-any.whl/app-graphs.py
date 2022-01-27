from ogdf_python import ogdf, cppinclude
import pandas as pd
cppinclude("ogdf/planarity/PlanarizationLayout.h")
cppinclude("ogdf/basic/graphics.h")


global default_colors
default_colors = {
    'red': ogdf.Color(r=245, g=20, b=20, a=204),
    'green': ogdf.Color(r=20, g=200, b=20, a=204),
    'blue': ogdf.Color(r=0, g=40, b=245, a=204),
    'yellow': ogdf.Color(r=245, g=245, b=0, a=204),
    'purple': ogdf.Color(r=70, g=0, b=200, a=204),
    'pink': ogdf.Color(r=200, g=0, b=140, a=204),
    'orange': ogdf.Color(r=245, g=100, b=0, a=204),
    'brown': ogdf.Color(r=100, g=40, b=0, a=204),
    'gray': ogdf.Color(r=120, g=120, b=120, a=204),
    'light_green': ogdf.Color(r=100, g=245, b=100, a=204),
    'light_blue': ogdf.Color(r=40, g=140, b=245, a=204),
    'light_red': ogdf.Color(r=245, g=60, b=60, a=204),
    'dark_green': ogdf.Color(r=0, g=90, b=0, a=204),
    'dark_blue': ogdf.Color(r=0, g=30, b=60, a=204),
    'dark_red': ogdf.Color(r=90, g=0, b=0, a=204)
}

class graph():
    def __init__(self):
        self.G = ogdf.Graph()
        self.GA = ogdf.GraphAttributes(self.G, ogdf.GraphAttributes.all)

    def read(self,
            filename_aplikacije,
            aplikacije_sheet_name,
            filename_vmesniki,
            vmesniki_sheet_name,
            aplikacije,
            komponente,
            vmesnik_izvor,
            vmesnik_ponor,
            vmesnik_smer,
            tehnologija,
            barve=None
            ):

        self.barve=barve

        self.df_apl = pd.read_excel(filename_aplikacije, engine='openpyxl',
                           sheet_name=aplikacije_sheet_name, header=None).dropna(how='all')
        self.df_apl.dropna(axis=1, how='all', inplace=True)
        self.df_apl.columns = self.df_apl.iloc[0]
        self.df_apl = self.df_apl.iloc[1:].reset_index(drop=True)

        self.df_vme = pd.read_excel(filename_vmesniki, engine='openpyxl',
                            sheet_name=vmesniki_sheet_name, header=None).dropna(how='all')
        self.df_vme.dropna(axis=1, how='all', inplace=True)
        self.df_vme.columns = self.df_vme.iloc[0]
        self.df_vme = self.df_vme.iloc[1:].reset_index(drop=True)

        stolpci_apl = self.df_apl.columns.values.tolist()
        
        if aplikacije not in stolpci_apl:
            print(
                f"Stolpec {aplikacije} v prvi xlsx datoteki ne obstaja.")
            return

        if komponente not in stolpci_apl:
            print(
                f"Stolpec {komponente} v prvi xlsx datoteki ne obstaja.")
            return

        if barve and barve not in stolpci_apl:
            print(
                f"Stolpec {barve} v prvi xlsx datoteki ne obstaja.")
            return

        stolpci_vme = self.df_vme.columns.values.tolist()

        if vmesnik_izvor not in stolpci_vme:
            print(
                f"Stolpec {vmesnik_izvor} v drugi xlsx datoteki ne obstaja.")
            return

        if vmesnik_ponor not in stolpci_vme:
            print(
                f"Stolpec {vmesnik_ponor} v drugi xlsx datoteki ne obstaja.")
            return

        if vmesnik_smer not in stolpci_vme:
            print(
                f"Stolpec {vmesnik_smer} v drugi xlsx datoteki ne obstaja.")
            return

        if tehnologija not in stolpci_vme:
            print(
                f"Stolpec {tehnologija} v drugi xlsx datoteki ne obstaja.")
            return

        optionsRight = ['>', '->', '-->', '--->', '---->', 'desno', 'right']
        optionsLeft = ['<', '<-', '<--', '<---', '<----', 'levo', 'left']

        for i in range(len(self.df_vme)):
            if pd.isnull(self.df_vme[vmesnik_smer][i]):
                continue
            elif str(self.df_vme[vmesnik_smer][i]).lower() in optionsRight:
                self.df_vme[vmesnik_smer][i] = 'forward'
            elif str(self.df_vme[vmesnik_smer][i]).lower() in optionsLeft:
                self.df_vme[vmesnik_smer][i] = 'back'
            else:
                self.df_vme[vmesnik_smer][i] = 'both'
        
        self.df_apl.rename(columns = {aplikacije:'aplikacije', komponente:'komponente'}, inplace = True)
        if barve:
            self.df_vme.rename(columns = {barve:'barve'}, inplace = True)
        
        self.df_vme.rename(columns = {vmesnik_izvor:'vmesnik_izvor',vmesnik_ponor: 'vmesnik_ponor', vmesnik_smer:'vmesnik_smer', tehnologija:'tehnologija'}, inplace = True)

    def draw(self):
        # dodajanje aplikacij, komponent in povezav med aplikacijami in njihovimi komponentami
        aplikacija = None
        NODES = {}
        b = None
        for i in range(self.df_apl.shape[0]):
            if pd.isnull(self.df_apl['aplikacije'][i]) == False:
                aplikacija = self.df_apl['aplikacije'][i]
                node = self.G.newNode()
                self.GA.label[node] = aplikacija
                self.GA.width[node] = 7 * len(aplikacija)
                NODES[aplikacija] = node

                if self.barve:
                    barva = self.df_apl['barve'][i]
                    if pd.isnull(self.df_apl['aplikacije'][i]):
                        return f'Barva za aplikacijo: {aplikacija} ni podana'
                    if barva in default_colors:
                        b = default_colors[barva]
                    else:
                        h = barva.lstrip('#')                            
                        r,g,b = [int(h[i:i+2], 16) for i in [0, 2, 4]]
                        b = ogdf.Color(r=r, g=g, b=b, a=204)
                else:
                    j = i%15
                    b = list(default_colors.items())[j][1]
                self.GA.fillColor[node] = b
                self.GA.strokeWidth[node] = 2
                #self.GA.strokeColor[node] = b
                

            elif aplikacija and pd.isnull(self.df_apl['komponente'][i]) == False:
                podaplikacija = self.df_apl['komponente'][i]
                node = self.G.newNode()
                self.GA.label[node] = podaplikacija
                self.GA.width[node] = 7 * len(podaplikacija)
                NODES[podaplikacija] = node
                self.GA.fillColor[node] = b
                #self.GA.strokeColor[node] = b
                self.GA.strokeWidth[node] = 0
                edge = self.G.newEdge(NODES[aplikacija], node)
                self.GA.strokeColor[edge] = b
                self.GA.arrowType[edge] = 0
            
        # dodajanje vmesnikov in povezav
        
        for i in range(self.df_vme.shape[0]):
            if pd.isnull(self.df_vme['vmesnik_izvor'][i])==False and pd.isnull(self.df_vme['vmesnik_ponor'][i])==False:
                node = self.G.newNode()
                self.GA.shape[node] = ogdf.Shape.Ellipse
                if pd.isnull(self.df_vme['tehnologija'][i])==False:
                    self.GA.label[node] = self.df_vme['tehnologija'][i]
                    self.GA.width[node] = 10 * len(self.df_vme['tehnologija'][i])
                if self.df_vme['vmesnik_smer'][i] == 'forward':
                    edge1 = self.G.newEdge(NODES[self.df_vme['vmesnik_izvor'][i]], node)
                    edge2 = self.G.newEdge(node, NODES[self.df_vme['vmesnik_ponor'][i]])
                elif self.df_vme['vmesnik_smer'][i] == 'back':
                    edge1 = self.G.newEdge(node, NODES[self.df_vme['vmesnik_izvor'][i]])
                    edge2 = self.G.newEdge(NODES[self.df_vme['vmesnik_ponor'][i]], node)
                else:
                    edge1 = self.G.newEdge(node, NODES[self.df_vme['vmesnik_izvor'][i]])
                    edge2 = self.G.newEdge(NODES[self.df_vme['vmesnik_ponor'][i]], node)
                    edgeArrow = ogdf.EdgeArrow.Both
                    self.GA.arrowType[edge1] = edgeArrow
                    self.GA.arrowType[edge2] = edgeArrow
                    

        PL = ogdf.PlanarizationLayout()
        PL.call(self.GA)

    def save_svg(self, filename):
        ogdf.GraphIO.write(self.GA, filename+".svg", ogdf.GraphIO.drawSVG)
        for edge in self.G.edges:
            print(self.GA.arrowType[edge])
            print(self.GA.label[edge.source()])
            print(self.GA.label[edge.target()])

    def save(self, filename='example', format='DOT'):
        available_formats = ['GML', 'DOT']
        if format not in available_formats:
            return f'Format is not supported. \nPlease chose format from the list:{available_formats}'
        switch = {
            'GML': lambda : ogdf.GraphIO.write(self.GA, filename+'.gml', ogdf.GraphIO.writeGML),
            'DOT': lambda : ogdf.GraphIO.write(self.GA, filename+'.dot', ogdf.GraphIO.writeDOT)
        }
        switch[format]()
