# TODO: přemístit do k8s configu
OAREPO_OAI_PROVIDERS = {
    "nusl": {
        "description": "NUŠL",
        "synchronizers": [
            {
                "name": "marcxml",
                "oai_endpoint": "http://invenio.nusl.cz/oai2d/",
                "set": "global",
                "metadata_prefix": "marcxml",
                "bulk": True,
                "unhandled_paths": ['/leader', '/005', '/008', '020__/q', '/0248_',
                                    '/246__', '/340__', '/500__', '/502__/a', '/502__/b',
                                    '/502__/d', '/502__/g', '/506__', '/598__/9', '/6530_',
                                    '/6557_',
                                    '/655_7', "/656_7/2", '/8560_', '/85642/h',
                                    '/85642/z', '/8564_', '/909CO/p', '999c1', '/999C2',
                                    'FFT_0'],
                "default_endpoint": "common",
            }
        ]
    },
    "uk": {
        "description": "Univerzita Karlova",
        "synchronizers": [
            {
                "name": "xoai",
                "oai_endpoint": "https://dspace.cuni.cz/oai/nusl",
                "set": "nusl_set",
                "metadata_prefix": "xoai",
                "bulk": True,
                "unhandled_paths": ['/dc/date/accessioned',
                                    '/dc/date/available',
                                    '/dc/date/embargoEndDate',
                                    '/dc/identifier/repId',
                                    '/dc/identifier/aleph',
                                    '/dc/description/provenance',
                                    '/dc/description/department/en_US/value',
                                    '/dc/description/faculty/en_US/value',
                                    '/dc/language/cs_CZ/value',
                                    '/dc/unhandled',
                                    '/dcterms/created',
                                    '/thesis/degree',
                                    '/thesis/grade/en',
                                    '/thesis/grade/code',
                                    '/uk/thesis/type',
                                    '/uk/taxonomy',
                                    '/uk/faculty-name',
                                    '/uk/faculty-abbr',
                                    '/uk/degree-program/en',
                                    '/uk/degree-discipline/en',
                                    '/uk/abstract',
                                    '/uk/thesis/defenceStatus',
                                    '/uk/departmentExternal',
                                    '/uk/embargo/reason',
                                    '/bundles/bundle',
                                    '/others/handle',
                                    '/others/lastModifyDate',
                                    '/others/owningCollection',
                                    '/repository', ],
                "default_endpoint": "theses",
            }
        ]
    },
}
