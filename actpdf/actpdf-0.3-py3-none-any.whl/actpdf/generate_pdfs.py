import json, os, sys, re
from weasyprint import HTML
import jinja2
# import pygal dfd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from jinja2.nodes import CallBlock
from jinja2.ext import Extension
import markdown


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(os.path.expanduser("~"),"Desktop")
TEMPLATE_PATH = "templates" # "src/xcodepdf_package/templates"
# need to remove this once markdown is installed
# os.environ['PATH'] +=':'+os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(DIR_PATH))), 'github','temp','markdown')


class MarkdownExtension(Extension):
    # https://github.com/jpsca/jinja-markdown/
    tags = set(['markdown'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(['name:endmarkdown'],drop_needle=True)
        return CallBlock(self.call_method('_render_markdown'),[],[],body).set_lineno(lineno)

    def _render_markdown(self, caller):
        return  markdown.markdown(caller(), extensions=['attr_list'])

class PDFHelper:    

    def __init__(self):        
        self.jinja_env = self.setup_jinja2_filters()


    def split_at_digit(self,s):
        # jinja2 filter
        if not s: return []
        return re.split(r'\d+\.\s?',s)[1:]

    def remove_unwanted_chars(self,s):
        get_data = lambda data: data.split(':')[1] if ':' in data else data
        # jinja2 filter
        # : lg= left green, rr = right red, if its not green or red then its orange
        m = re.match(r"[^\w-]*(\w*)](.*)", s) # \w- used to match any non-alphanumeric character
        
        # this is a bug since there is no ] in s
        if not m: return {'outcome':'o','data': get_data(s).replace('_sss_','')}
        color = m.group(1) if len(m.group(1))==1 else m.group(1)[1]
        data = m.group(2).replace('_sss_','')
        return {'outcome':color,'data': get_data(data)}

    def split_at_comma(self,s):
        # jinja2 filter
        if not s: return []
        resp =[d for d in s.split(',') if d and d!='-']
        return list(set(resp))

    def split_and_order(self,s):
        """This is a quick fix need to update in future.
        whenever you see "Average, Good, Excellent" 
        use that order, the others sem to be OK."""
        exp_order = ['Average:','Good:','Excellent:']
        curr_order = [exp_order.index(w) for w in s.split(' ') if w in exp_order] # [0, 2, 1]

        if len(curr_order) == 3:
            list1, list2 = zip(*sorted(zip(curr_order, s.split('*')))) # https://stackoverflow.com/a/9764364/2351696
            return list2 # print(list1, list2)
        return s.split('*')

    def get_outcome_color(self,s):
        """
        To fix : https://github.com/gamifications/pdf/issues/9
        """
        outcomes = ['Increased','Good','Excellent','Favorable','Faster','Fast','Gluten insensitive',
            'Normal','Low','Need less','Slow','Gluten Sensitive','Tolerant','Insensitive',
            'Moderate','Need more','Average','Intolerant', 'Higher','Slower','Decreased','Unfavorable',
            'Lower','High','Bad']
        # search outcome in given string and remove beginning chars
        item = re.match(f"(?i)(\s?)({'|'.join(outcomes)})(.*)", s)
        # print(item,s)
        if not item:
            outcome= 'Average'
        else:
            outcome = item.group(2)
        if outcome in ['Need more','Moderate']: outcome = 'Average' # this is wrong need to replace
        return {'index':outcomes.index(outcome), 'avg_index':outcomes.index('Average')}

    def generate_piechart(self,context, image):
        """ There is a piechart in fitness/nutrition folder"""
        if 'ES_pie' in context and context['ES_pie']:
            # fitness graph
            colors = ['#FFCCFF','#99FFCC']
            sizes = [context['ES_pie']['E'],context['ES_pie']['S']]
            labels = ['Endurance', 'Power']

        elif 'CFP' in context and context['CFP']:
            # nutrition graph
            colors = ['#FFCCFF','#99FFCC','#CCFFFF']
            sizes = [context['CFP']['C'],context['CFP']['F'],context['CFP']['P']]
            labels = ['Carbohydrates', 'Fats', 'Protiens']
        else:
            return

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90,colors=colors)
        plt.savefig(image, bbox_inches='tight', transparent=True, dpi=100)

    def setup_jinja2_filters(self):
        """Jinja2 setup """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(DIR_PATH))
        env.filters['split_at_digit'] = self.split_at_digit
        env.filters['split_at_comma'] = self.split_at_comma
        env.filters['remove_unwanted_chars'] = self.remove_unwanted_chars
        env.filters['split_and_order'] = self.split_and_order
        env.filters['get_outcome_color'] = self.get_outcome_color  
        env.add_extension(MarkdownExtension)
        return env

    
    def create_pdfs(self,startswith=None):
        is_html_only = False
        if startswith == 'html':
            # if startswith = 'html' create html files only
            is_html_only = True
            startswith = None

        pdfs = []
        # check pdf exists
        if os.path.exists(os.path.join(OUTPUT_PATH,'pdf')):
            _, _, pdfs = next(os.walk(os.path.join(OUTPUT_PATH, 'pdf')))
            pdfs = [pdf.replace('.json','') for pdf in pdfs]
            
        else:
            os.makedirs(os.path.join(OUTPUT_PATH,'pdf'))

        # get all json files from json folder
        if os.path.exists(os.path.join(OUTPUT_PATH,'json')):
            # get file_names in the json folder
            _, _, folder_files = next(os.walk(os.path.join(OUTPUT_PATH, 'json')))
            json_files = []

            for fname in folder_files:
                # if not a json file skip
                if fname.endswith('json'):
                    if startswith: 
                        # if user called python pdf.py fit
                        # then we only convert json files startswith fit
                        if fname.lower().startswith(startswith.lower()):
                            json_files.append(fname)
                    else:
                        json_files.append(fname)

            # json_files = [f for f in json_files if f.endswith('json')] # if not a json file skip
            self.total = len(json_files)
            json_files = [fn for fn in json_files if fn.replace('.json','.pdf') not in pdfs]
            self.skipped = self.total - len(json_files)
            print(f"Total JSON files {self.total}.")
            print(f"Skipped JSON files {self.skipped}.")
            

            for i,fn in enumerate(json_files): 
                
                # if fn.replace('.json','.pdf') in pdfs:
                #     yes_no = input('PDF exists. Press Enter to skip, y to overwrite: ')
                #     if yes_no.lower() not in ['y','yes','replace','r']:
                #         continue

                print(f"\nConverting {i+1} of {self.total - self.skipped}: {fn}")
                template={
                    'allergy':'allergy',
                    'nut':'nutrition', 
                    'fit':'fitness', 
                    'hlth':'health',
                    'detox':'detox',
                    'skin': 'skin',
                    'pgx':'pgx',
                    'persn':'personality',
                    'carr':'carrier',
                    'sleep':'sleep',
                    'disease':'disease'
                }                
                # generate template folder name from json filename

                # """
                template_folder = [template[key] for key in template if key in fn][0]
                self.create_pdf(template_folder, fn, is_html_only, template)
                """
                try:
                    template_folder = [template[key] for key in template if key in fn][0]
                    self.create_pdf(template_folder, fn)
                except:
                    print(f'Error! unable to convert {fn}')
                    self.failed+=1
                """
        else:
            print(os.path.join(OUTPUT_PATH,'json'), ':Json folder not found.')

        
    def generate_frontcover(self, temp_folder, partner):
        # generate front cover page using logo
        # template = fitness_quanutrition
        logoIm = Image.open(os.path.join(OUTPUT_PATH,'logos',f"{partner}.png")) # ~/Desktop/logos
        logoWidth, logoHeight = logoIm.size
        im = Image.open(os.path.join(temp_folder,'images','front_plain.png'))
        im.paste(logoIm, (logoWidth-85, logoHeight-120), logoIm)
        im.save(os.path.join(temp_folder,'images','partner_cover.png'))
        
    def convert_4_qua_fit_to_Fitness_4_qua(self, template):
        # input eg: 4_qua fit.json
        # output eg: Fitness-4_qua.pdf
        for key in template:
            if key in json_fn:
                # replace fit and endpart json and strip the blank space at ends
                tk = json_fn.replace(key,'').replace('.json','').strip() 
                print(f"{template[key].title()}-{tk}.pdf")

        for key,value in template.items():
                if key in json_fn:
                    # replace fit and endpart json and strip the blank space at ends
                    tk = json_fn.replace(key,'').replace('.json','').strip() 
                    print(f"{template[key].title()}-{tk}.pdf")

    def create_pdf(self, template_folder, json_fn, is_html_only, template=None): 
        # read json file
        with open(os.path.join(OUTPUT_PATH, 'json', json_fn)) as f:
            data = json.load(f)
            if 'your report' in data:
                data['your_report']=data['your report']
            if 'how to read' in data:
                data['how_to_read']=data['how to read']

        if 'partner' in data and data['partner'] != 'xcode':
            # if partner(eg: quanutrition) in json file
            if data['partner'] == 'xcode':
                # generate front cover page using logo
                self.generate_frontcover(template_folder,data["partner"] )
                
            elif data['partner']:
                # if quanutrition then take templates from quanutrition folder
                template_folder=f'{template_folder}_{data["partner"]}'
                

        # create context dict based on folder
        dir_path = os.path.join(DIR_PATH,TEMPLATE_PATH,template_folder)

        # Jinja issues 411 and 412 - os.path.dirname and os.path.join will use '\\', 
        # which FilesystemLoader will reject. Make sure the result is separated with '/'
        context= {'folder': f'{TEMPLATE_PATH}/{template_folder}', 'img_path':os.path.join(dir_path,'images')}        

        if os.path.exists(os.path.join(dir_path,'images')):
            # get file_names in the image folder
            _, _, images = next(os.walk(os.path.join(dir_path,'images')))

            # create a dict of images like {'back_img': '/home/images/back.img'}
            # context -> back_img, cover_img, front_plain_img, pie_chart_img
            context.update({f"{f.split('.')[0]}_img":os.path.join(dir_path,'images',f) for f in images})

        if template_folder in ['health','disease']:
            # if json file data is not list and it is dict.
            context['data']=data
        else:
            context.update(data)

        self.generate_piechart(context, os.path.join(DIR_PATH,TEMPLATE_PATH,template_folder,'images','pie_chart.svg'))

        # generate pdf from html

        # Jinja issues 411 and 412 - os.path.dirname and os.path.join will use '\\', 
        # which FilesystemLoader will reject. Make sure the result is separated with '/'
        html_template = self.jinja_env.get_template(f"{TEMPLATE_PATH}/{template_folder}/template.html")

        for key in template:
            if key in json_fn:
                print(key)
        if is_html_only:
            htmlfp=open(os.path.join(OUTPUT_PATH, 'pdf', f"{json_fn.replace('.json','.html')}"),'w')
            htmlfp.write(html_template.render(context))
        else:
            html = HTML(string=html_template.render(context))

            """
            Convert -> 4_qua_fit.json to Fitness_4_qua.pdf
            input eg: 4_qua fit.json
            output eg: Fitness-4_qua.pdf
            """
            output_pdf_file_name = ''
            for key in template:
                if key in json_fn:
                    # replace fit and endpart json and strip the blank space at ends        
                    tk = json_fn.rsplit('fit',1)[0].strip() 
                    output_pdf_file_name=f"{template[key].title()}-{tk}.pdf"

            pdf_path = os.path.join(OUTPUT_PATH, 'pdf', output_pdf_file_name)
            html.write_pdf(pdf_path)

        


def main():
    helper = PDFHelper()

    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            helper.create_pdfs(sys.argv[1])
        else:
            print('Calling with args deprecated. Try without arguments,ie: python pdf.py')
    else:
        helper.create_pdfs()

    if (helper.total - helper.skipped) > 0:
        print(f'{helper.skipped} files skipped.')
        print(f'{helper.total - helper.skipped} files converted to pdf.')
    else:
        print('Nothing converted.')

if __name__ == '__main__':
    main()
