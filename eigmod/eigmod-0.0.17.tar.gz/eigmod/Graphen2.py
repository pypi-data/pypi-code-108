import random
import pygame
import math
import sys


def getmousecollision(maus, buttonx, buttony, width, height, verschiebung=0):
    if maus[0] >= buttonx and maus[0] <= buttonx + width and maus[1] >= buttony and maus[1] <= buttony + height or maus[0] >= buttonx + verschiebung and maus[0] <= buttonx + width + verschiebung and maus[1] >= buttony + verschiebung and maus[1] <= buttony + height + verschiebung:
        return True
    else:
        return False


def graph_zeichnen(databekommen, soll_wert=-1):
    pygame.init()
    pygame.font.init()

    scrwidth = 1000
    scrheight = 600

    pygame.init()
    win = pygame.display.set_mode((scrwidth, scrheight))
    pygame.display.set_caption("Graph")
    font = pygame.font.SysFont("comicsans", 30)

    clock = pygame.time.Clock()

    data = []
    großter = 0
    kleinster = 0
    durchschnitt = 0
    median = 0
    sortierte_liste = []
    ausgewahlt = False

    for i, d in enumerate(databekommen):
        data.append([i, d[0], d[1]])

    datalange = len(data)

    # median berechnen

    def takeSecond(elem):
        return elem[2]

    großtere_zahl = round(max(data, key=takeSecond)[2], 2)
    großter = großtere_zahl
    if großter < soll_wert:
        großter = soll_wert
    kleinster = round(min(data, key=takeSecond)[2], 2)

    sortierte_liste = data.copy()
    sortierte_liste.sort(key=takeSecond)
    median = round(sortierte_liste[int(datalange/2)][2], 2)

    # durchschnitt berechnen

    gesamt = 0
    for i in data:
        gesamt += i[2]
    durchschnitt = round(gesamt/datalange, 2)

    radius = 4

    x = font.render(str(round(großter, 1)), False, (255, 0, 0))

    abstand_zum_rand = 90
    if x.get_width() + 35 >= abstand_zum_rand:
        abstand_zum_rand = x.get_width() + 35

    abstand_linien = 10
    linien_breite_kurz = 2
    linien_breite_lang = 2
    langern_unterschied = 5
    zahlen_abstand_vom_stirch = 8
    x_und_y_gleichlang = True
    anzahl_x = 10
    anzahl_y = 10
    lange = 20
    abstand_durch_medi_linie = 40

    maximalskalierung = 10
    richtskalierung = 8

    if soll_wert > 0:
        y_soll = int(scrheight - abstand_zum_rand - ((scrheight-abstand_zum_rand-abstand_linien * 2))
                     * soll_wert/großter)

    y_durch = int(scrheight - abstand_zum_rand - ((scrheight-abstand_zum_rand-abstand_linien * 2))
                  * durchschnitt/großter)
    y_medi = int(scrheight - abstand_zum_rand - ((scrheight-abstand_zum_rand-abstand_linien * 2))
                 * median/großter)

    def draw():
        win.fill((0, 0, 0))

        if int(datalange/richtskalierung) > 1:
            skalierungen = richtskalierung+1
        else:
            skalierungen = datalange

        zahler = math.ceil((x.get_width() * (skalierungen + 1)
                            )/(scrwidth - abstand_zum_rand)) - 1

        pygame.draw.line(win, (255, 255, 255), (abstand_zum_rand, scrheight-abstand_zum_rand),
                         (scrwidth-(abstand_linien), scrheight-abstand_zum_rand), 2)
        pygame.draw.line(win, (255, 255, 255), (abstand_zum_rand, scrheight-abstand_zum_rand),
                         (abstand_zum_rand, abstand_linien), 2)

        for content in data:

            # kord x und y
            kordx = [int(abstand_zum_rand + (scrwidth-abstand_zum_rand-abstand_linien * 2)
                         * content[0]/data[-1][0]), scrheight - abstand_zum_rand]

            kordy = [abstand_zum_rand, int(
                scrheight - abstand_zum_rand - ((scrheight-abstand_zum_rand-abstand_linien * 2)) * (content[0]/data[-1][0]))]

            # Circle Position
            circ_pos = [int(abstand_zum_rand + (scrwidth-abstand_zum_rand-abstand_linien * 2)
                            * content[0]/data[-1][0]), int(scrheight - abstand_zum_rand - ((scrheight-abstand_zum_rand-abstand_linien * 2))
                                                           * content[2]/großter)]

            # Skalierung

            skzeichnen = False

            if datalange >= maximalskalierung:
                if content[0] % int(datalange/richtskalierung) == 0:
                    skzeichnen = True
            else:
                skzeichnen = True

            zahlanzeigen = False

            if skzeichnen:
                pygame.draw.line(
                    win, (0, 255, 0), (kordy[0] - 5, kordy[1]), (kordy[0] + 5, kordy[1]), linien_breite_kurz)

                if zahler == math.ceil((x.get_width() * (skalierungen + 1))/(scrwidth - abstand_zum_rand)) - 1:
                    zahlenx = font.render(
                        str(round(content[1], 2)), False, (255, 0, 0))
                    win.blit(
                        zahlenx, (int(kordx[0] - zahlenx.get_width()/2), kordx[1] + zahlen_abstand_vom_stirch))

                    if x.get_width() * (skalierungen+1) > scrwidth - abstand_zum_rand:
                        zahler = 0
                else:
                    zahler += 1

                anzeigezahly = content[0] * (großter/data[-1][0])

                if str(anzeigezahly)[-1] == "0":
                    anzeigezahly = str(int(anzeigezahly))
                else:
                    anzeigezahly = str(round(anzeigezahly, 1))

                zahleny = font.render(
                    anzeigezahly, False, (0, 255, 0))
                win.blit(
                    zahleny, (int(kordy[0] - zahleny.get_width() - zahlen_abstand_vom_stirch), int(kordy[1] - zahleny.get_height()/2 + zahlen_abstand_vom_stirch/3)))

                pygame.draw.line(
                    win, (255, 0, 0), (kordx[0], kordx[1] - 5), (kordx[0], kordx[1] + 5), linien_breite_kurz)

            # Kreise
            pygame.draw.circle(
                win, (0, 0, 255), (circ_pos[0], circ_pos[1]), radius)

        pygame.draw.rect(win, (255, 255, 255), (20, int(
            scrheight-abstand_zum_rand/2 - lange + 10), 40, 40))

        if ausgewahlt:
            pygame.draw.rect(win, (100, 200, 100), (25, int(
                scrheight-abstand_zum_rand/2 - lange + 10 + 5), 30, 30))
            gros = font.render(
                "H:"+str(großtere_zahl), False, (255, 255, 255))
            klein = font.render(
                "T:"+str(kleinster), False, (255, 255, 255))
            medi = font.render(
                "M:"+str(median), False, (240, 170, 0))
            durch = font.render(
                "D:"+str(durchschnitt), False, (210, 4, 70))
            win.blit(
                gros, (300, int(scrheight-(abstand_zum_rand * 2/3) - gros.get_height()/2) + 10))
            win.blit(
                klein, (300, int(scrheight-(abstand_zum_rand * 1/3) - gros.get_height()/2) + 10))
            win.blit(
                medi, (100, int(scrheight-(abstand_zum_rand * 2/3) - gros.get_height()/2) + 10))
            win.blit(
                durch, (100, int(scrheight-(abstand_zum_rand * 1/3) - gros.get_height()/2) + 10))

            pygame.draw.line(win, (210, 4, 70), (abstand_zum_rand,
                                                 y_durch), (scrwidth-abstand_linien - abstand_durch_medi_linie, y_durch), 2)
            pygame.draw.line(win, (240, 170, 0), (abstand_zum_rand,
                                                  y_medi), (scrwidth-abstand_linien - abstand_durch_medi_linie, y_medi), 2)

            medi_linien_letter = font.render(
                "M", False, (240, 170, 0))
            durch_linien_letter = font.render(
                "D", False, (210, 4, 70))
            win.blit(
                medi_linien_letter, (int(scrwidth - abstand_durch_medi_linie - 5), int(y_medi - medi_linien_letter.get_height()/2) + 2))
            win.blit(
                durch_linien_letter, (int(scrwidth - abstand_durch_medi_linie - 5), int(y_durch - durch_linien_letter.get_height()/2 + 2)))

        else:
            pygame.draw.rect(win, (200, 100, 100), (25, int(
                scrheight-abstand_zum_rand/2 - lange + 10 + 5), 30, 30))

        if soll_wert > 0:
            pygame.draw.line(win, (5, 210, 190), (abstand_zum_rand,
                                                  y_soll), (scrwidth-abstand_linien, y_soll), 2)

    run = True

    while run:
        clock.tick(20)
        maus = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if getmousecollision(
                    maus, 20, int(scrheight-abstand_zum_rand/2 - lange + 10), 40, 40) and event.type == pygame.MOUSEBUTTONDOWN:
                ausgewahlt = not ausgewahlt

        keys = pygame.key.get_pressed()

        draw()

        pygame.display.update()

    pygame.quit()


def create_data():
    infos = []
    for i in range(0, int(math.pi * 100), 1):
        x = (i)
        # y = math.sin(i/50)
        # y = 2.72**i
        y = int((i**2 - (i**2.5) * 0.1) + 10)
        infos.append([x, y])

    return(infos)

if __name__ == "__main__":
    graph_zeichnen(create_data())
