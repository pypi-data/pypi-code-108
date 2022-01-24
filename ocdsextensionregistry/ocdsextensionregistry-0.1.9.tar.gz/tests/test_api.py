from textwrap import dedent

from ocdsextensionregistry import build_profile


def test_build_profile(tmpdir):
    basedir = tmpdir.mkdir('schema')
    profile = basedir.mkdir('profile')
    profile.join('extension.json').write('{"codelists":[],"dependencies":[],"testDependencies":[]}')

    build_profile(basedir, '1__1__5', {
        "bidOpening": "master",
        "lots": "v1.1.5",
        "options": "master",
    })

    patched_codelists = basedir.join('patched').join('codelists')
    profile_codelists = basedir.join('profile').join('codelists')

    assert len(basedir.listdir()) == 2
    assert len(basedir.join('patched').listdir()) == 3
    assert len(patched_codelists.listdir()) == 19
    assert len(basedir.join('profile').listdir()) == 2
    assert not profile_codelists.exists()

    assert profile.join('extension.json').read() == dedent("""\
    {
      "dependencies": [
        "https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/master/extension.json"
      ],
      "testDependencies": [
        "https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/master/extension.json",
        "https://raw.githubusercontent.com/open-contracting-extensions/ocds_finance_extension/master/extension.json"
      ]
    }
    """)

    codelist = patched_codelists.join('awardCriteria.csv').read()

    assert ',Deprecated' not in codelist
    assert 'lowestCost' not in codelist
    assert ',Extension\n' in codelist
    assert ',OCDS Core\n' in codelist


def test_build_profile_codelists(tmpdir):

    def update_codelist_urls(text, codelists):
        url = 'https://standard.open-contracting.org/{{version}}/{{lang}}/schema/codelists/#release-tag'
        return text.replace(url, 'https://www.example.com')

    basedir = tmpdir.mkdir('schema')
    profile = basedir.mkdir('profile')
    profile.join('extension.json').write('{}')

    build_profile(basedir, '1__1__5', {
        "location": "v1.1.5",
    }, update_codelist_urls=update_codelist_urls)

    patched_codelists = basedir.join('patched').join('codelists')
    profile_codelists = basedir.join('profile').join('codelists')

    assert len(basedir.listdir()) == 2
    assert len(basedir.join('patched').listdir()) == 3
    assert len(patched_codelists.listdir()) == 21
    assert len(basedir.join('profile').listdir()) == 3
    assert len(profile_codelists.listdir()) == 2

    assert profile.join('extension.json').read() == dedent("""\
    {
      "codelists": [
        "locationGazetteers.csv",
        "geometryType.csv"
      ]
    }
    """)

    schema = basedir.join('patched').join('release-schema.json').read()

    assert 'https://standard.open-contracting.org/{{version}}/{{lang}}/schema/codelists/#release-tag' not in schema
    assert 'https://www.example.com' in schema
