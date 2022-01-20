#!/usr/bin/env python3

import datetime
from datetime import datetime as dt


def format_date(date, date_standard):

        if isinstance(date, str):
                date_list = date.split("/")
                year = date_list[2]
                if len(year) == 2:
                        date2 = datetime.datetime.strptime(date, '%m/%d/%y')
                elif len(year) == 4:
                        date2 = datetime.datetime.strptime(date, '%m/%d/%Y')
        else:
                date2 = date

        if date_standard == "deutsch":
                date_formatted = date2.strftime('%d.%m.%Y')        
        elif date_standard == "international":
                date_formatted = date2.strftime('%Y-%m-%d')
        elif date_standard == "us":                
                d = date2.day
                y = date2.year
                m = date2.month
                
                if m==1:
                        str_month = "JAN"
                elif m==2:
                        str_month = "FEB"
                elif m==3:
                        str_month = "MAR"
                elif m==4:
                        str_month = "APR"
                elif m==5:
                        str_month = "MAY"
                elif m==6:
                        str_month = "JUN"
                elif m==7:
                        str_month = "JUL"
                elif m==8:
                        str_month = "AUG"
                elif m==9:
                        str_month = "SEP"
                elif m==10:
                        str_month = "OCT"
                elif m==11:
                        str_month = "NOV"
                elif m==12:
                        str_month = "DEC"
                
                date_formatted = str_month + " " + str(d) + ", " + str(y)
                                

        return date_formatted
	
