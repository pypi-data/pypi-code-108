'''
Tests for StoneMark
'''

from __future__ import unicode_literals

from stonemark import PPLCStream
from stonemark import *
from textwrap import dedent
from unittest import TestCase, main

class TestPPLCStream(TestCase):

    def test_get_char(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        line_no = 0
        while stream:
            self.assertEqual(stream.line_no, line_no)
            ch = stream.get_char()
            result.append(ch)
            if ch == '\n':
                line_no += 1
        self.assertEqual(''.join(result), sample+'\n')
        self.assertEqual(line_no, 2)
        self.assertEqual(line_no, stream.line_no)

    def test_get_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        line_no = 0
        while stream:
            self.assertEqual(stream.line_no, line_no)
            line = stream.get_line()
            result.append(line)
            line_no += 1
        self.assertEqual(''.join(result), sample+'\n')
        self.assertEqual(line_no, 2)
        self.assertEqual(line_no, stream.line_no)

    def test_peek_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        self.assertEqual(stream.current_line, 'line one\n')
        self.assertEqual(stream.peek_line(), 'line two\n')
        self.assertEqual(stream.get_line(), 'line one\n')
        self.assertEqual(stream.current_line, 'line two\n')
        self.assertEqual(stream.peek_line(), '')
        self.assertEqual(stream.get_line(), 'line two\n')
        self.assertEqual(stream.current_line, '')
        try:
            stream.get_line()
        except EOFError:
            pass

    def test_push_char(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        stream.push_char('2')
        stream.push_char('4')
        line_no = 0
        while stream:
            self.assertEqual( stream.line_no, line_no)
            line = stream.get_line()
            result.append(line)
            line_no += 1
        self.assertEqual( ''.join(result), '42'+sample+'\n')
        self.assertEqual( line_no, 2)
        self.assertEqual( line_no, stream.line_no)

    def test_push_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        stream.push_line('line zero')
        line_no = 0
        while stream:
            self.assertEqual( stream.line_no, line_no)
            ch = stream.get_char()
            result.append(ch)
            if ch == '\n':
                line_no += 1
        self.assertEqual( ''.join(result), 'line zero\n'+sample+'\n')
        self.assertEqual( line_no, 3)
        self.assertEqual( line_no, stream.line_no)


class TestStonemark(TestCase):
    def test_simple_doc_1(self):
        test_doc = dedent("""\
        Document Title
        ==============

        In this paragraph we see that we have multiple lines of a single
        sentence.

        - plus a two-line
        - list for good measure
          + and a sublist
          + for really good measure

        Now a tiny paragraph.

            and a code block!

        ```
        and another code block!
        ```
        """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h2>Document Title</h2>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <p>Now a tiny paragraph.</p>

                <pre><code>
                and a code block!
                </code></pre>

                <pre><code>
                and another code block!
                </code></pre>
                """).strip())

    def test_simple_doc_2(self):
        test_doc = dedent("""\
                ==============
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  1) and a sublist
                  2) for really good measure
                - back to main list


                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]], ListItem], CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ol>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ol>
                <li>back to main list</li>
                </ul>

                <pre><code>
                and another code block!
                </code></pre>
                """).strip())

    def test_simple_doc_3(self):
        test_doc = dedent("""\
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                Now a tiny paragraph I mean header
                ----------------------------------

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h2>Document Title</h2>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>
                and a code block!
                </code></pre>

                <pre><code>
                and another code block!
                </code></pre>
                """).strip())

    def test_simple_doc_4(self):
        test_doc = dedent("""\
                ==============
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure

                ---

                Now a tiny paragraph.

                    and a code block!

                ```
                and another code block!
                ```
                """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem], Rule, Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                </ul>

                <hr>

                <p>Now a tiny paragraph.</p>

                <pre><code>
                and a code block!
                </code></pre>

                <pre><code>
                and another code block!
                </code></pre>
                """).strip())

    def test_failure_1(self):
        test_doc = dedent("""\
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure
                - back to main list

                    and a code block!

                ```
                and another code block!
                ```
                """)

        try:
            doc = Document(test_doc)
        except BadFormat as exc:
            self.assertTrue('line 12' in exc.msg)
        else:
            raise Exception('failure did not occur')

    def test_format_nesting_1(self):
        test_doc = dedent("""\
                **this is **really important** important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is really important important info</b></p>")

    def test_format_nesting_2(self):
        test_doc = dedent("""\
                **this is *really important* important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is <i>really important</i> important info</b></p>")

    def test_format_footnote(self):
        test_doc = dedent("""\
                This is a paragraph talking about many things. [^1] The question is:
                how are those many things related?

                ---

                [^1]: Okay, maybe just the one thing.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph, Rule, IDLink])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about many things. <sup><a href="#footnote-1">1</a></sup> The question is:
                how are those many things related?</p>

                <hr>

                <span id="footnote-1"><sup>1</sup> Okay, maybe just the one thing.</span>
                """).strip())

    def test_format_external_link_1(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources][1].  How many of them
                are there, anyway?

                [1]: http://www.boardgamegeek.com
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
                are there, anyway?</p>
                """).strip())

    def test_format_external_link_2(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources](http://www.boardgamegeek.com).  How many of them
                are there, anyway?
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
                are there, anyway?</p>
                """).strip())

    def test_format_wiki_link(self):
        test_doc = dedent("""\
                Check the [Documentation] for more details.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>Check the <a href="Documentation">Documentation</a> for more details.</p>
                """).strip())


    def test_format_image(self):
        test_doc = dedent("""\
                An introductory paragraph.

                ![*a riveting picture*](https://www.image_library/photos/rivets.png)

                A concluding paragraph.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc), [Paragraph, Image, Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>An introductory paragraph.</p>

                <img src="https://www.image_library/photos/rivets.png" alt="<i>a riveting picture</i>">

                <p>A concluding paragraph.</p>
                """).strip())

    def test_formatted_doc_1(self):
        test_doc = dedent("""\
                ==============
                Document Title
                ==============

                In **this paragraph** we see that we have multiple lines of a *single
                sentence*.

                - plus a ***two-line***
                - list `for good` measure
                  + and __a sublist__
                  + for ~~really~~ good measure

                Now a ==tiny paragraph== that talks about water (H~2~O) raised 2^4^ power.

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In <b>this paragraph</b> we see that we have multiple lines of a <i>single
                sentence</i>.</p>

                <ul>
                <li>plus a <b><i>two-line</i></b></li>
                <li>list <code>for good</code> measure</li>
                    <ul>
                    <li>and <u>a sublist</u></li>
                    <li>for <del>really</del> good measure</li>
                    </ul>
                </ul>

                <p>Now a <mark>tiny paragraph</mark> that talks about water (H<sub>2</sub>O) raised 2<sup>4</sup> power.</p>

                <pre><code>
                and a code block!
                </code></pre>

                <pre><code>
                and another code block!
                </code></pre>
                """).strip())

    def test_html_chars(self):
        self.maxDiff = None
        test_doc = dedent("""\
                ===================
                Some Maths & Stuffs
                ===================

                1) a = 4
                2) b < 5
                3) c > 1

                To ~~everyone~~ *anyone* **who <hears> this** -- HELP![^jk]

                ```
                a < b >= c
                ```

                Is a < b ?  Yes.

                Is a >= b ?  Yes.

                Is a & b = a ?  Yes.

                ![someone sayd, "OReily?"](https://www.fake.com/images/123.png)

                ---

                [^jk]: Just a joke!  I'm >fine<!
                """)
        doc = Document(test_doc)
        self.assertEqual(
                doc.to_html(),
                dedent("""\
                <h1>Some Maths &amp; Stuffs</h1>

                <ol>
                <li>a = 4</li>
                <li>b &lt; 5</li>
                <li>c &gt; 1</li>
                </ol>

                <p>To <del>everyone</del> <i>anyone</i> <b>who &lt;hears&gt; this</b> -- HELP!<sup><a href="#footnote-jk">jk</a></sup></p>

                <pre><code>
                a &lt; b &gt;= c
                </code></pre>

                <p>Is a &lt; b ?  Yes.</p>

                <p>Is a &gt;= b ?  Yes.</p>

                <p>Is a &amp; b = a ?  Yes.</p>

                <img src="https://www.fake.com/images/123.png" alt="someone sayd, &quot;OReily?&quot;">

                <hr>

                <span id="footnote-jk"><sup>jk</sup> Just a joke!  I&#x27;m &gt;fine&lt;!</span>
                """).strip(), doc.to_html())

def shape(document, text=False):
    result = []
    if isinstance(document, Document):
        document = document.nodes
    for thing in document:
        if not text and isinstance(thing, Text):
            continue
        elif isinstance(thing, Node):
            result.append(thing.__class__)
            intermediate = shape(thing.items)
            if intermediate:
                result.append(intermediate)
    return result

main()
