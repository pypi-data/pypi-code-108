# -*- coding: utf-8 -*-
import os
from pylatexenc.latex2text import LatexNodes2Text
from pybtex.database import parse_file
from lektor.pluginsystem import Plugin


class CitationPlugin(Plugin):
    name = 'lektor-citation'
    description = u'This Plugin should extend lektor with APA-styled citations using bibtex files. It was based on the known lektor-bibtex-support plugin by arunpersaud.'


    def __init__(self, env, id):
        super().__init__(env, id)

        config = self.get_config()
        self.bibfile = config.get('Bibtex.file', []).strip()

        self.bib_data = parse_file(os.path.join(env.root_path, 'assets', self.bibfile))

    def citation_entries(self):
        return self.bib_data.entries

    def citation_entry(self, id):
        return self.bib_data.entries[id]

    def citation_short_output(self, id, link=None):
        e = self.citation_entry(id)
        if "url" in e.fields.keys() and len(e.fields['url']) > 0:
            link = e.fields['url']
        else:
            link = "?"
        authors = ""
        lAuthor = e.persons['author']
        n = 1
        for author in lAuthor:
            prelast = author.prelast_names
            if len(prelast) > 0:
                for item in prelast:
                    authors += "{i} ".format(i = str(item))
            authors += str(author.last_names[0])
            first =  author.first_names
            if len(first) > 0 :
                authors += ","
                for item in first:
                    authors += " {i}.".format(i = str(item[:1]))
            middle =  author.middle_names
            if len(middle) > 0 :
                for item in middle:
                    authors += " {i}.".format(i = str(item[:1]))
            
            if len(lAuthor) > 1:
                
                if n == (len(lAuthor) - 1):
                    authors += " \& "
                elif n < (len(lAuthor) -1):
                    authors += ", "

            n = n + 1

            
        year = e.fields['year']
        edition = ""
        if 'edition' in e.fields.keys():
            edition = e.fields['edition']
            edition = " ({ed}. Ed.)".format(ed = edition)
        else:
            edition = ""
        

        if 'publisher' in e.fields.keys():
            publisher = e.fields['publisher']
            if 'address' in e.fields.keys():
                location = e.fields['address']
                publisher = " {location}: {publisher}.".format(location = location, publisher = publisher)
            elif publisher:
                publisher = " {publisher}.".format(publisher = publisher)
            else:
                publisher = ""
            
        output = '<li id="{eid}"><a href="{link}" class="litref">{authors} ({pubYear}).</a> <em>{title}</em>{edition}. {publisher}'.format(eid = id, link = link, authors = authors, pubYear = year, title = e.fields['title'], edition = edition, publisher = publisher)
        return output
        
    def citation_full_output(self, id):
        e = self.citation_entry(id)
        if "url" in e.fields.keys() and len(e.fields['url']) > 0:
            link = e.fields['url']
        else:
            link = "?"
        
        def circle_people(lAuthor):
            authors = ""
            n = 1
            for author in lAuthor:
                first =  author.first_names
                if len(first) > 0 :
                    for item in first:
                        authors += "{i} ".format(i = str(item))
                middle =  author.middle_names
                if len(middle) > 0 :
                    for item in middle:
                        authors += "{i} ".format(i = str(item))
            
                prelast = author.prelast_names
                if len(prelast) > 0:
                    for item in prelast:
                        authors += "{i} ".format(i = str(item))
                authors += str(author.last_names[0])
            
                if len(lAuthor) > 1:
                
                    if n == (len(lAuthor) - 1):
                        authors += " \& "
                    elif n < (len(lAuthor) -1):
                        authors += ", "

                n = n + 1
            return authors


        authors = circle_people(e.persons['author'])
        if "editor" in e.persons.keys():
            editors = circle_people(e.persons['editor'])
        else:
            editors = ""

            
        year = e.fields['year']
        edition = ""
        if 'edition' in e.fields.keys():
            edition = e.fields['edition']
            edition = " {ed}. Ed.".format(ed = edition)
        else:
            edition = ""

        if 'pages' in e.fields.keys():
            pages = e.fields['pages']
        else:
            pages = ""
            
        if 'issbn' in e.fields.keys():
            issbn = e.fields['issbn']
        else:
            issbn = ""

        if 'note' in e.fields.keys():
            note = e.fields['note']
        else:
            note = ""
        

        if 'publisher' in e.fields.keys():
            publisher = e.fields['publisher']
            if 'address' in e.fields.keys():
                location = e.fields['address']
                publisher = " {location}: {publisher}.".format(location = location, publisher = publisher)
            elif publisher:
                publisher = " {publisher}.".format(publisher = publisher)
            else:
                publisher = ""
 

        output = """<h2>{title}</h2><h3>{authors} ({pubYear})</h3>
<p>{note}</p>
<dl class="literature">
<dt class="edition"></dt>
<dd>{edition}</dd>
<dt class="editors"></dt>
<dd>{editors}</dd>
<dt class="pages"></dt>
<dd>{pages}</dd>
<dt class="issbn"></dt>
<dd>{issbn}</dd>
<dt class="publisher"></dt>
<dd>{publisher}</dd>
</dl>
""".format(eid = id, link = link, authors = authors, pubYear = year, title = e.fields['title'], edition = edition, publisher = publisher, editors = editors, pages = pages, issbn = issbn, note = note)
        return output

    def on_setup_env(self, **extra):
        def decode_filter(value):
            return LatexNodes2Text().latex_to_text(value)
     
        self.env.jinja_env.globals['citation_entries'] = self.citation_entries
        self.env.jinja_env.globals['citation_entry'] = self.citation_entry
        self.env.jinja_env.globals['citation_short_output'] = self.citation_short_output
        self.env.jinja_env.globals['citation_full_output'] = self.citation_full_output
        self.env.jinja_env.filters['decode'] = decode_filter
        
        
           
