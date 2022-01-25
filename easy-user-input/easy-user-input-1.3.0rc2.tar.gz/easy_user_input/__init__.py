#alias eui to easy_user_input (the old file name)
#this will be removed in a future update
from easy_user_input import eui as easy_user_input
import sys
sys.modules['easy_user_input.easy_user_input'] = sys.modules['easy_user_input.eui']