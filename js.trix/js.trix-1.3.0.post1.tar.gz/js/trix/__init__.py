from fanstatic import Library, Resource, Group

library = Library('trix', 'resources')

trix_css = Resource(library, 'trix.css')

trix_js = Resource(library, 'trix.js')

trix = Group([trix_css, trix_js])
