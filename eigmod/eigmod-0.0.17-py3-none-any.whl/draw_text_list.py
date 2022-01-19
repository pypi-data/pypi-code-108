import pygame

def text_draw(win, text_list, rect, color ,font,  input_spacer_counter = None, input_active = None, binde_seite = "mitte"):

    zeilen = len(text_list)
    anfangs_y = rect.y + rect.height/2

    # wenn binde seite nicht mitte dann puffer
    abstand_zu_seite = 5

    for index, zeile in enumerate(text_list): 
            
        t_input = font.render(zeile, True, (color))
        text_height_platz = rect.height / zeilen  
        eine_zeile_anteil = (zeilen - 1)/2
        mitte_verschiebung = t_input.get_height()/2
        index_abhangige_verschiebung = (index - eine_zeile_anteil) * text_height_platz 
        y = anfangs_y - mitte_verschiebung + index_abhangige_verschiebung
        if binde_seite == "mitte":
            x = rect.x + rect.width//2 - t_input.get_width()//2 
        elif binde_seite == "links":
            x = rect.x + abstand_zu_seite
        elif binde_seite == "rechts":
            x = rect.x  + rect.width - t_input.get_width() - abstand_zu_seite

        win.blit(t_input, (x, y))

    if input_active and input_spacer_counter % 30 >= 15:
        t_spacer = font.render("|", True, (color))

        if binde_seite == "mitte":
            spacer_x = x + t_input.get_width()
        elif binde_seite == "links":
            spacer_x = x + t_input.get_width() 
        elif binde_seite == "rechts":
            spacer_x = rect.x + rect.width - abstand_zu_seite*1.5
            
        win.blit(t_spacer, (spacer_x, y))
