from Qtalk.integration import *

def success_alert(rs_name, page_name, user_name):

    Mattermost.publish_message(Mattermost, text={
    'Red Social':rs_name, 
    'Página':page_name, 
    'Usuario':user_name, 
    'Estado':'Activo :large_green_circle:'})

def fail_alert(rs_name, page_name, user_name):

    Mattermost.publish_message(Mattermost, text={
    'Red Social':rs_name, 
    'Página':page_name, 
    'Usuario':user_name, 
    'Estado':'Inactivo :red_circle:'})

def say_hi():
    print('Hello there!')
