# -*- coding: utf-8 -*-

import csv
from plone import api
from BTrees.OOBTree import OOBTree
from plone.namedfile.field import NamedBlobFile
from zope.interface import Interface
from zope import schema
from .i18n import MessageFactory as _
from z3c.form import form, field, button, interfaces as form_interfaces
from interfaces import ITaxonomy


class IImportForm(Interface):
    """ schema for import form """

    import_file = NamedBlobFile(
        title=_(u"Upload prepared CSV file"),
        description=_(u" "),
        required=True
    )
    first_row = schema.Int(
        title=_(u"First row with data"),
        description=_(u"First row with data"),
        default = 2,
        required=True
    )
    first_column = schema.Int(
        title=_(u"First column with data"),
        description=_(u"First column with data"),
        default = 2,
        required=True
    )
    index_column = schema.Int(
        title=_(u"Column with index number to be attached"),
        description=_(u""),
        required=False
    )
    taxonomy = schema.TextLine(
        title=_(u"Modified taxonomy"),
        description=_(u""),
        required=True
    )


class TaxonomyImportForm(form.Form):

    fields = field.Fields(IImportForm)
    ignoreContext = True

    label = u"Update taxonomy data"
    description = u"Simple, sample form"

    def updateWidgets(self):
        super(TaxonomyImportForm, self).updateWidgets()
        self.widgets["taxonomy"].mode = form_interfaces.HIDDEN_MODE

    @button.buttonAndHandler(u'Update')
    def handleApply(self, action):
        data, errors = self.extractData()
        import_file = data['import_file']
        first_column = data['first_column']
        first_row = data['first_row']
        taxonomy_name = data['taxonomy']
        index_column = data['index_column']

        portal = api.portal.get()
        sm = portal.getSiteManager()
        taxonomy = sm.queryUtility(ITaxonomy,
                                  name=taxonomy_name)
        if not taxonomy:
            raise ValueError('Taxonomy could not be found.')

        rows = csv.reader(import_file.open(), delimiter=';', quotechar='"')
        counter = 1
        taxonomy_values = []
        index_mapper = {}
        while first_row>1:
            rows.next()
            first_row -= 1
        for row in rows:
            index = '{0} - '.format(row[index_column] if index_column is not None else '')
            values = filter(None, row[(first_column-1):])
            #newline and '/' characters are breaking taxonomy storage
            values = [v.replace('\n', ' ').replace('/', '|') for v in values]
            if values:
                #I'm adding tuples to the mapper. Per column, per value
                print values
                index_mapper[(len(values)-1, values[-1])] = '{0}{1}'.format(index, values[-1])
                formatted_values = [index_mapper[(v_tuple[0], v_tuple[1])] for v_tuple in enumerate(values)]
                taxonomy_values.append('/'.join(formatted_values))

        language = taxonomy.default_language
        taxonomy.data[language] = OOBTree()
        for (key, value) in enumerate(taxonomy_values):
            taxonomy.data[language][value] = str(key+1)
        api.portal.show_message(message='Taxonomy data updated!', request=self.request)
        return_url = '{}/@@taxonomy-settings'.format(portal.absolute_url())
        self.request.response.redirect(return_url)    
