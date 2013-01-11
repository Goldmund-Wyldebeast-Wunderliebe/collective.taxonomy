# -*- coding: utf-8 -*-

from interfaces import ITaxonomy

from Products.CMFCore.utils import getToolByName

from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.interfaces import IVocabulary, IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.component.hooks import getSite

_pmf = MessageFactory('plone')


class TaxonomyVocabulary(object):
    # Vocabulary for generating a list of existing taxonomies

    implements(IVocabularyFactory)

    def __call__(self, adapter):
        results = []
        sm = getSite().getSiteManager()
        utilities = sm.getUtilitiesFor(ITaxonomy)

        for (utility_name, utility) in utilities:
            utility_name = utility.name
            utility_title = utility.title

            results.append(SimpleTerm(value=utility_name,
                                      title=utility_title)
                           )

        return SimpleVocabulary(results)


class Vocabulary(object):
    """Vocabulary, generated by the ITaxonomy utility"""

    implements(IVocabulary)

    def __init__(self, name, data, inv_data):
        self.data = data
        self.inv_data = inv_data
        self.message = MessageFactory(name)

    def __iter__(self):
        for term in self.getTerms():
            yield term

    def __len__(self):
        return len(self.getTerms())

    def __contains__(self, identifier):
        return self.getTerm(identifier) is not None

    def getTermByToken(self, input_identifier):
        return SimpleTerm(value=input_identifier,
                          title=self.message(input_identifier,
                                             self.inv_data[
                                                 input_identifier]))

    def getTerm(self, input_identifier):
        return self.getTermByToken(input_identifier)

    def getTerms(self):
        results = []

        for (path, identifier) in self.data.items():
            term = SimpleTerm(value=identifier,
                              title=self.message(identifier, path))
            results.append(term)

        return results


class GroupsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        result = []
        acl_users = getToolByName(context, 'acl_users')

        groups = acl_users.source_groups.getGroupIds()
        for group in groups:
            result.append(SimpleTerm(group))

        return SimpleVocabulary(result)
