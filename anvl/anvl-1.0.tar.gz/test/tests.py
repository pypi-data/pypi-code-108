import os

import anvl

# Input test

def test_elements():
    a = "a:1\r\nb:2\r\nc:3\r\n"
    assert anvl.loads(a) == [{"a": "1", "b": "2", "c": "3"}]

def test_multiline_element_bodys():
    a = "foo:Oh, hey, look at this long line! It looks\r\n        someone needs to wrap it!\r\n"
    assert anvl.loads(a) == [{"foo": "Oh, hey, look at this long line! It looks someone needs to wrap it!"}]


def test_varied_multiline_indentation():
    a = "qux:This line is long like the last.\r\n But the identation\r\n   is all over\r\n                    the\r\n\tmap."
    assert anvl.loads(a) == [{"qux": "This line is long like the last. But the identation is all over the map."}]
    

def test_multiple_nonindent_spaces_preserved():
    a = "key:This line has      weird spacing.  But\r\n    it's preserved except for the indent.\r\n"
    assert anvl.loads(a) ==  [{"key": "This line has      weird spacing.  But it's preserved except for the indent."}]


def test_element_body_with_colons():
    a = "title:Mutual Aid: A Factor of Evolution\r\nauthor:Kropotkin, Pyoter\r\nurl:https://gutenberg.org/ebooks/4341"
    assert anvl.loads(a) == [
        {
        "title": "Mutual Aid: A Factor of Evolution",
        "author": "Kropotkin, Pyoter",
        "url": "https://gutenberg.org/ebooks/4341"
        }
    ]


def test_leading_trailing_whitespace():
    a = "key1  :        value1    \r\nkey2\t:\tvalue2\t\r\n"
    assert anvl.loads(a) == [{"key1": "value1", "key2": "value2"}]


def test_comments():
    a ="#comment\r\ncolor:yellow\r\n# another comment\r\n"
    assert anvl.loads(a) == [{"color": "yellow"}]

def test_multiple_records():
    a = "foo:bar\r\noof:rab\r\n"
    pass

def test_multiple_blank_lines():
    a = "\r\n\r\n\r\n\r\ntitle:burrito\r\n\r\ntitle:waffle\r\n\r\n\r\n"
    assert anvl.loads(a) == [{"title": "burrito"}, {"title": "waffle"}]
    pass

def test_no_final_empty_line():
    a = "surname:Vaughan\r\ngiven:Dorothy"
    assert anvl.loads(a) == [{"surname": "Vaughan", "given": "Dorothy"}]


def test_no_cr():
    a = "surname:Hopper\ngiven:Grace\n"
    assert anvl.loads(a) == [{"surname": "Hopper", "given": "Grace"}]


def test_load_file():
    input_file = "test/test.anvl"
    expected = [
            {
                "person": "Conway, Lynn",
                "biography": "Lynn Conway is a pioneering computer scientist and transgender activist. She invented generalized dynamic instruction handling and helped spark the Mead-Conway VLSI chip design revolution."
            },
            {
                "person": "Herrington, John",
                "biography": "A citizen of the Chickasaw Nation, John Herrington was an astronaut and the first Native American in space."
            }
    ]
    
    assert anvl.load(input_file) == expected

# Output tests
def test_ends_with_blank_line():
    l = [{"name": "hooks, bell"}]
    assert anvl.dumps(l) == "name: hooks, bell\r\n"


def test_blank_lines_between_records():
    l = [
            {
                "author": "Jackson, Shirley",
                "title":"The Haunting of Hill House"
            },
            {"author": "Gilman, Charlotte Perkins", "title": "Herland"}
    ]
    assert anvl.dumps(l) == "author: Jackson, Shirley\r\ntitle: The Haunting of Hill House\r\n\r\nauthor: Gilman, Charlotte Perkins\r\ntitle: Herland\r\n"


def test_nonstring_keys():
    l = [{1: "Won!", 2: "Too!"}]
    assert anvl.dumps(l) == "1: Won!\r\n2: Too!\r\n"


def test_nonstring_values():
    l = [{"bool": True, "int": 13}]
    assert anvl.dumps(l) == "bool: True\r\nint: 13\r\n"


def test_default_wrapping():
    l = [
            {
                "sentence": "This example sentence is over 80 characters long, so it should end up getting wrapped at the default width."
            }
    ]
    assert anvl.dumps(l) == "sentence: This example sentence is over 80 characters long, so it should end up\r\n\tgetting wrapped at the default width.\r\n"


def test_variable_width_wrapping():
    l = [
            {
                "sentence":"This sentence is shorter, but should still get wrapped if we specify a narrower width."
            }
    ]
    assert anvl.dumps(l, width=40) == "sentence: This sentence is shorter, but\r\n\tshould still get wrapped if we specify\r\n\ta narrower width.\r\n"


def test_change_indent():
    l = [
            {
                "sentence":"This example sentence is over 80 characters long, so it should end up getting wrapped at the default width."
            }
    ]
    assert anvl.dumps(l, indent="  ") == "sentence: This example sentence is over 80 characters long, so it should end up\r\n  getting wrapped at the default width.\r\n"


def test_change_line_end():
    l = [{"fi": "fie", "fo": "fum"}]
    assert anvl.dumps(l, line_end = "\n") == "fi: fie\nfo: fum\n"

def test_save_file():
    l = [
            {
                "person": "Conway, Lynn",
                "biography": "Lynn Conway is a pioneering computer scientist and transgender activist. She invented generalized dynamic instruction handling and helped spark the Mead-Conway VLSI chip design revolution."
            },
            {
                "person": "Herrington, John",
                "biography": "A citizen of the Chickasaw Nation, John Herrington was an astronaut and the first Native American in space."
            }
    ]
    expected = "person: Conway, Lynn\r\nbiography: Lynn Conway is a pioneering computer scientist and transgender\r\n\tactivist. She invented generalized dynamic instruction handling and helped\r\n\tspark the Mead-Conway VLSI chip design revolution.\r\n\r\nperson: Herrington, John\r\nbiography: A citizen of the Chickasaw Nation, John Herrington was an astronaut\r\n\tand the first Native American in space.\r\n"
    out_file = "stem_bios.txt"
    
    anvl.dump(l, "stem_bios.txt")
    
    # Need to read the file in as binary to keep Python from mangling "\r\n"
    # into "\n\n"
    with open(out_file, "rb") as fh:
        assert fh.read().decode("utf8") == expected
        
    os.remove(out_file)
    
    
