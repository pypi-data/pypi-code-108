def print_side_by_side(*strings, b=2):
    len_strings =0
    strings_to_print = []
    for string in strings:
        len_strings +=len(str(string))    
    if len_strings <=124:
            if b == 0:
                for i in range(0,len(strings)):
                    strings_to_print.append(str(list(strings)[i]).replace('[',"").replace(']',"").replace('',"").replace(',',"").replace("'",""))
                    ##########################################
                    strings_to_print.append(" "*int(63.5-8-len(strings_to_print[0])))
            else:
                count =0
                for i in range(0,b):
                    strings_to_print.append(str(list(strings)[i+count]).replace('[',"").replace(']',"").replace('',"").replace(',',"").replace("'",""))
                    count+=1
                    strings_to_print.append("")
                    strings_to_print.append(str(list(strings)[i+count]).replace('[',"").replace(']',"").replace('',"").replace(',',"").replace("'",""))
                    ############################################
                    strings_to_print.append(" "*int(63.5-10-len(strings_to_print[0])-len(strings_to_print[1])-len(strings_to_print[2])))
            strings_to_print.pop() 
            if len(str(strings_to_print).replace('[',"").replace(']',"").replace('',"").replace(',',"").replace("'",""))>127:
                raise Exception('Both or one of the strings exceeds the charachter limit!')
            else:
                print(str(strings_to_print).replace('[',"").replace(']',"").replace('',"").replace(',',"").replace("'",""))
    else:
            raise Exception('Both or one of the strings exceeds the charachter limit!')


from IPython.display import display_html
from itertools import chain,cycle
def display_side_by_side(*args,titles=cycle([''])):
    html_str=''
    for df,title in zip(args, chain(titles,cycle(['</br>'])) ):
        html_str+='<th style="text-align:center"><td style="vertical-align:top">'
        html_str+=f'<h2>{title}</h2>'
        html_str+=df.to_html().replace('table','table style="display:inline"')
        html_str+='</td></th>'
    display_html(html_str,raw=True)


if __name__ == '__main__':
    print_side_by_side(*strings, b=2)

