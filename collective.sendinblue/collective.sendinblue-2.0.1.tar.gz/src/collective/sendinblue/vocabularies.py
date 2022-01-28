# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from collective.sendinblue.interfaces import ISendinblueAPI


def available_lists(context):
    sendinblue = getUtility(ISendinblueAPI)
    lists = sendinblue.lists()
    if not lists:
        return SimpleVocabulary([])
    terms = []
    accounts = {}
    if len(lists) > 1:
        # we have multiple accounts, so we need to distinguish them later
        accounts = sendinblue.accounts()
    for key, listsinfos in lists.items():
        for listinfos in listsinfos:
            account_id = key
            account_infos = accounts.get(account_id)
            if account_infos:
                company = account_infos[2].get('company', '')
                title = u" — ".join([company, listinfos.get('name', '')])
            else:
                title = listinfos.get('name', '')
            value = u"%s-%s" % (account_id, listinfos['id'])
            terms.append(
                SimpleTerm(value=value, title=title)
            )
    return SimpleVocabulary(terms)
