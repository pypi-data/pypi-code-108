#!/usr/bin/env python3

class Line(object):
    _Line__lines = []

    @classmethod
    def registerLine(cls, station):
        if station not in cls.__lines:
            cls.__lines.append(station)

    @classmethod
    def getAllLines(cls):
        return cls.__lines

    @classmethod
    def getLineByName(cls, name):
        for l in cls.__lines:
            if l.name == name:
                return l
        raise ValueError(f"No line with name '{name}'.")

    def __init__(self, name, id, start, end):
        self.name = name
        self.id = id
        self.terminus = [start, end]
        Line.registerLine(self)

    def getTerminus(self, direction):
        if direction not in [1, 2]:
            raise ValueError(f"Expected direction to be either 1 or 2, got '{direction}'")
        return self.terminus[direction - 1]

    def __repr__(self):
        return f"<Line: {self.name}>"

METRO = Line("Métro", "175", ('Technopôle+SAINT-ETIENNE-DU-ROUVRAY', 'Georges+Braque+GRAND+QUEVILLY'), ('Boulingrin+ROUEN',))
T1 = Line("T1", "176", ('CHU+Charles+Nicolle+ROUEN',), ('Mont+aux+Malades+MONT-SAINT-AIGNAN',))
T2 = Line("T2", "177", ('Tamarelle+BIHOREL',), ('Mairie-V.+Schoelcher+N.-D.-DE-BONDEVILLE',))
T3 = Line("T3", "178", ('Durécu-Lavoisier+DARNÉTAL',), ('Monet+CANTELEU',))
T4 = Line("T4", "214", ('Zénith+-+Parc+Expo+GRAND+QUEVILLY',), ('Boulingrin+ROUEN',))
F1 = Line("F1", "94", ('Stade+Diochon+PETIT-QUEVILLY',), ('Plaine+de+la+Ronce+ISNEAUVILLE',))
F2 = Line("F2", "91", ('Tamarelle+BIHOREL',), ('La+Vatine+-+Centre+Commercial+MT-ST-AIGNAN', 'Parc+de+la+Vatine+MT-ST-AIGNAN'))
F3 = Line("F3", "97", ('Pôle+Multimodal+OISSEL',), ('Théâtre+des+Arts+ROUEN',))
F4 = Line("F4", "109", ('Mont-Riboudet+Kindarena+ROUEN',), ('Hameau+de+Frévaux+MALAUNAY',))
F5 = Line("F5", "118", ('Lycée+Galilée+FRANQUEVILLE-SAINT-PIERRE',), ('Théâtre+des+Arts+ROUEN',))
_5 = Line("5", "92", ('Martainville+ROUEN',), ('Collège+Jules+Verne+DEVILLE-LES-ROUEN',))
_6 = Line("6", "93", ('Les+Bouttières+GRAND-COURONNE',), ('Beauvoisine+ROUEN',))
_8 = Line("8", "95", ('Ile+Lacroix+ROUEN',), ('Longs+Vallons+NOTRE-DAME-DE-BONDEVILLE', 'Ecole+Moulin+NOTRE-DAME-DE-BONDEVILLE', 'Théâtre+des+Arts+ROUEN'))
_9 = Line("9", "96", ('E.+Lacroix+SAINT-PIERRE-DE-MANNEVILLE',), ('Chapelle+Saint-Siméon+DÉVILLE-LÈS-ROUEN',))
_11 = Line("11", "106", ('Grand+Val+AMFREVILLE-LA-MIVOIE',), ('Collège+L.+de+Vinci+BOIS-GUILLAUME',))
_13 = Line("13", "108", ('Mairie+BELBEUF', 'École+de+Musique+BOOS'), ('Hôtel+de+Ville+ROUEN',))
_20 = Line("20", "110", ("Rue+de+l'Église+SAINT-LÉGER-DU-BOURG-DENIS", 'Mairie+SAINT-AUBIN-ÉPINAY', 'Hôtel+de+Ville+ROUEN'), ('Le+Chapitre+BIHOREL',))
_22 = Line("22", "124", ('Bois+Tison+SAINT-JACQUES-SUR-DARNÉTAL',), ('Boulingrin+ROUEN',))
_26 = Line("26", "125", ('',), ('Mont-Riboudet+Kindarena+ROUEN',))
_27 = Line("29", "126", ('Gare+de+Saint-Etienne+SAINT-ÉTIENNE-DU-ROUVRAY',), ('Bel+Air+PETIT-COURONNE', 'Lycée+Val+de+Seine+GRAND+QUEVILLY'))
_29 = Line("29", "127", ('Route+de+Montville+MALAUNAY',), ('Gare+Routière+ROUEN',))
_30 = Line("30", "128", ('',), ('Gare+Routière+ROUEN',))
_32 = Line("32", "141", ('Champ+de+Foire+ELBEUF',), ('Théâtre+des+Arts+ROUEN',))
_33 = Line("33", "144", ('Pont+de+la+Chapelle+ST-ETIENNE-DU-ROUVRAY',), ('Théâtre+des+Arts+ROUEN',))
_34 = Line("34", "211", ('Vesta+PETIT-QUEVILLY',), ('Théâtre+des+Arts+ROUEN',))
_37 = Line("37", "216", ('',), ('',))
_38 = Line("38", "164", ('',), ('',))
_39 = Line("39", "165", ('Rue+du+Coq+LA+BOUILLE',), ('Lycée+Fernand+Léger+GRAND-COURONNE',))
_40 = Line("40", "166", ('Boulingrin+ROUEN',), ('La+Varenne+MONT-SAINT-AIGNAN',))
_41 = Line("41", "168", ('La+Bastille+SOTTEVILLE-LES-ROUEN',), ('Ancienne+Mare+PETIT-QUEVILLY',))
_42 = Line("42", "169", ('La+Houssière+SAINT-ETIENNE-DU-ROUVRAY',), ('Centre+Routier+GRAND+QUEVILLY',))
_43 = Line("43", "170", ('',), ('',))
_88 = Line("88", "174", ('',), ('',))
A = Line("A", "111", ('Mairie+SAINT-PIERRE-LES-ELBEUF',), ('Mairie+CLÉON',))
B = Line("B", "112", ('Parc+Saint-Cyr+ELBEUF',), ('Ecole+de+La+Londe+LA+LONDE',))
C = Line("C", "113", ('Bosc+Tard+SAINT-PIERRE-LÈS-ELBEUF', 'Liérout+SAINT-PIERRE-LÈS-ELBEUF'), ('Les+Arches+ELBEUF',))
E = Line("E", "114", ('Mairie+CLÉON',), ('Moulin+Saint-Etienne+ELBEUF',))
F = Line("F", "115", ("Z.I.+L'Oison+SAINT-PIERRE-LÈS-ELBEUF",), ('Pôle+Multimodal+OISSEL',))
H = Line("H", "107", ('Hôpital+LOUVIERS',), ("Hôpital+Intercommunal+d'Elbeuf+SAINT-AUBIN-LÈS-ELBEUF",))
D1 = Line("D1", "116", ('',), ('',))
D2 = Line("D2", "117", ('',), ('',))
t35 = Line("t35", "156", ("Sente+d'Houdeville+CANTELEU", 'Mont-Riboudet+Kindarena+ROUEN'), ('Bérat+MAROMME-LA+MAINE',))
t53 = Line("t53", "171", ('Coteaux+du+Larmont+ROUEN',), ('Boulingrin+ROUEN',))
t54 = Line("t54", "172", ("Pont+d'Eauplet+SOTTEVILLE-LES-ROUEN", 'Hôtel+de+Ville+SOTTEVILLE-LES-ROUEN'), ('Dieppedalle+Rive+Gauche+GRAND+QUEVILLY',))
