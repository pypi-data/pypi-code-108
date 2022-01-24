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
    
    def get_people_full(self, lAuthor):
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

    

    def get_people_short(self, lAuthor):
        authors = ""
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
        return authors

    def get_pubYear(self, e):
        if "year" in e.fields.keys():
            year = e.fields['year']
        else:
            year = ""
        return year

    def get_title(self, e):
        if "title" in e.fields.keys():
            title = e.fields['title']
        else:
            title = ""
        return title

    def get_edition(self, e):

        if 'edition' in e.fields.keys():
            edition = e.fields['edition']
            edition = " ({ed}. Ed.)".format(ed = edition)
        else:
            edition = ""
            
        return edition

    def get_publisher(self, e):
        if 'publisher' in e.fields.keys():
            publisher = e.fields['publisher']
            if 'address' in e.fields.keys():
                location = e.fields['address']
                publisher = " {location}: {publisher}.".format(location = location, publisher = publisher)
            elif publisher:
                publisher = " {publisher}.".format(publisher = publisher)
            else:
                publisher = ""
        return publisher

    def get_pages(self, e):

        if 'pages' in e.fields.keys():
            pages = e.fields['pages']
        else:
            pages = ""
        return pages

    def get_issbn(self, e):
        if 'issbn' in e.fields.keys():
            issbn = e.fields['issbn']
        else:
            issbn = ""
        return issbn

    def get_note(self, e):
        if 'note' in e.fields.keys():
            note = e.fields['note']
        else:
            note = ""
        return note

    def get_url(self, e):
        if "url" in e.fields.keys() and len(e.fields['url']) > 0:
            link = e.fields['url']
        else:
            link = "?"
        return link
    

    def get_editors_short(self, e):
        if "editor" in e.persons.keys():
            editors = self.get_people_short(e.persons['editor'])
        else:
            editors = ""
        return editors
    
    def get_editors_full(self, e):
        if "editor" in e.persons.keys():
            editors = self.get_people_full(e.persons['editor'])
        else:
            editors = ""
        return editors

    def get_authors_short(self, e):
        if "author" in e.persons.keys():
            authors = self.get_people_short(e.persons['author'])
        else:
            authors = ""
        return authors

    def get_authors_full(self, e):
        if "author" in e.persons.keys():
            authors = self.get_people_full(e.persons['author'])
        else:
            authors = ""
        return authors
    
        

            
    def citation_short_output(self, id, link=None):
        e = self.citation_entry(id)
        link = self.get_url(e)
        authors = self.get_authors_short(e)
        title = self.get_title(e)    
        year = self.get_pubYear(e)
        edition = self.get_edition(e)
        publisher = self.get_publisher(e) 
            
        output = '<li id="{eid}"><a href="{link}" class="litref">{authors} ({pubYear}).</a> <em>{title}</em>{edition}. {publisher}'.format(eid = id, link = link, authors = authors, pubYear = year, title = title, edition = edition, publisher = publisher)
        return output
        
    def citation_full_output(self, id):
        e = self.citation_entry(id)
        link = self.get_url(e)
        authors = self.get_authors_full(e)
        editors = self.get_editors_full(e)        
        title = self.get_title(e)
        year = self.get_pubYear(e)
        edition = self.get_edition(e)
        pages = self.get_pages(e)
        issbn = self.get_issbn(e)    
        note = self.get_note(e)
        publisher = self.get_publisher(e)

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
""".format(eid = id, link = link, authors = authors, pubYear = year, title = title, edition = edition, publisher = publisher, editors = editors, pages = pages, issbn = issbn, note = note)
        return output

    def citation_full_cite(self,id,link=""):
        e = self.citation_entry(id)
        authors = self.get_authors_short(e)
        year = self.get_pubYear(e)
        output = """<a href=\"{link}#{id}\" class=\"litref\">({authors}, {pubYear})</a>""".format(link = link, id = id, authors = authors, pubYear = year)
        return output

    def citation_full_citeNP(self,id,link=""):
        e = self.citation_entry(id)
        authors = self.get_authors_short(e)
        year = self.get_pubYear(e)
        output = """<a href=\"{link}#{id}\" class=\"litref\">{authors} ({pubYear})</a>""".format(link = link, id = id, authors = authors, pubYear = year)
        return output

    def on_setup_env(self, **extra):
        def decode_filter(value):
            """ Make sure that special chars like german umlaute or accents are displayed in unicode """
            return LatexNodes2Text().latex_to_text(value)
     
        self.env.jinja_env.globals['citation_entries'] = self.citation_entries
        self.env.jinja_env.globals['citation_entry'] = self.citation_entry
        self.env.jinja_env.globals['citation_short_output'] = self.citation_short_output
        self.env.jinja_env.globals['citation_full_output'] = self.citation_full_output
        self.env.jinja_env.globals['citation_full_cite'] = self.citation_full_cite
        self.env.jinja_env.globals['citation_full_citeNP'] = self.citation_full_citeNP
        self.env.jinja_env.globals['citation_authors_short'] = self.get_authors_short
        self.env.jinja_env.globals['citation_authors_full'] = self.get_authors_full
        self.env.jinja_env.globals['citation_editors_short'] = self.get_editors_short
        self.env.jinja_env.globals['citation_editors_full'] = self.get_editors_full        
        self.env.jinja_env.globals['citation_pubYear'] = self.get_pubYear
        self.env.jinja_env.globals['citation_edition'] = self.get_edition
        self.env.jinja_env.globals['citation_publisher'] = self.get_publisher        
        self.env.jinja_env.globals['citation_title'] = self.get_title
        self.env.jinja_env.globals['citation_url'] = self.get_url
        self.env.jinja_env.globals['citation_issbn'] = self.get_issbn
        self.env.jinja_env.globals['citation_pages'] = self.get_pages
        self.env.jinja_env.globals['citation_note'] = self.get_note
        self.env.jinja_env.filters['decode'] = decode_filter
        
        
           
