class Beam_uniformP_knownMs:
    def __init__(self, MA, MB, l, p, left_support_name = 'A', rigth_support_name = 'B'):

        """

        Args:
            MA:
            MB:
            l:
            p:
        """
        self.MA = MA
        self.MB = MB
        self.l = l
        self.p = p

        self.left_support_name = left_support_name
        self.rigth_support_name = rigth_support_name

        self.logtext = []

    def calc(self):
        """

        """
        self.MABcenter = 0.5 * (self.MA + self.MB) + self.p * self.l ** 2 / 8
        self.VA = 0.5 * self.p * self.l + (self.MB - self.MA) / self.l
        self.VB = - 0.5 * self.p * self.l + (self.MB - self.MA) / self.l
        self.MABmax = self.MA + self.VA ** 2 / (2 * self.p)
        self.MABmaxr = self.MB + self.VB ** 2 / (2 * self.p)

    def __str__(self):
        self.logtext.append(f'M{self.left_support_name}{self.rigth_support_name}μέσο = {self.MABcenter:.2f}kNm')
        self.logtext.append(f'V{self.left_support_name} = {self.VA:.2f}kN')
        self.logtext.append(f'V{self.rigth_support_name} = {self.VB:.2f}kN')
        self.logtext.append(f'M{self.left_support_name}{self.rigth_support_name}max = {self.MABmax:.2f}kNm')
        self.logtext.append(f'M{self.left_support_name}{self.rigth_support_name}max = {self.MABmaxr:.2f}kNm (υπολογισμένο από δεξιά για επαλήθευση)')

        # print('VA = {0:.2f}kN'.format(VA))
        # print('VB = {0:.2f}kN'.format(VB))
        # print('MABmax = {0:.2f}kNm'.format(MABmax))
        # print('MABmax = {0:.2f}kNm (υπολογισμένο από δεξιά για επαλήθευση)'.format(MABmaxr))
        return '\n'.join(self.logtext)
