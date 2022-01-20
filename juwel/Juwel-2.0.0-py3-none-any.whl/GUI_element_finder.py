#!/usr/bin/env python3


def find_gui_element(gui_element):
    gui_element = gui_element.lower()
    
    if gui_element[-3:] == "xes":
        gui_element = gui_element[:-2]
    if gui_element[-1] == "s":
        gui_element = gui_element[:-1]


    if "_" in gui_element:
        gui_element = gui_element.replace("_", "")
    if " " in gui_element:
        gui_element = gui_element.replace(" ", "")


    if "dropdown" in gui_element or "list" in gui_element or "option" in gui_element:
        gui_element = "selectbox"

    if "button" in gui_element or "check" in gui_element:
        gui_element = "checkbox"

    if "text" in gui_element:
        gui_element = "textfield"

    if "alender" in gui_element or "date" in gui_element or "datum" in gui_element:
        gui_element = "calendar"
    

    return gui_element
