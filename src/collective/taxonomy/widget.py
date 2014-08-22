import zope.interface
import zope.component
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.browser.orderedselect import OrderedSelectWidget
from z3c.form.widget import FieldWidget
from plone import api
from interfaces import ITaxonomySelectWidget
import simplejson


class TaxonomySelectWidget(OrderedSelectWidget):
    zope.interface.implements(ITaxonomySelectWidget,
                              interfaces.IOrderedSelectWidget)

    def getData(self):
        #there has to be better way to obtain taxonomy name
        taxonomy_name = "collective.taxonomy.{}".format(self.field.getName()[9:])
        self.request.set('taxonomy',taxonomy_name)
        portal = api.portal.get()
        json_view = zope.component.getMultiAdapter((portal, self.request), name='taxonomy-json')
        data = simplejson.loads(json_view())
        if data:
            data = data[0]['children']
        return data

    @property
    def values(self):
        return []#self.field.get()    

    def getHTML(self, children):
        if not children:
            return ''
        li_nodes = []
        for child in children:
            children_html = self.getHTML(child['children'])
            if child['key'] in self.value:
                li_nodes.append(u'<li class="selected" id="{}">{}{}</li>'.format(child['key'], child['title'] if isinstance(child['title'], unicode) else child['title'].decode('utf-8'), self.getHTML(child['children'])))
            else:
                li_nodes.append(u'<li id="{}">{}{}</li>'.format(child['key'], child['title'] if isinstance(child['title'], unicode) else child['title'].decode('utf-8'), children_html))
        return u'<ul>{}</ul>'.format(u'\n'.join(li_nodes))
    

@zope.component.adapter(zope.schema.interfaces.ISequence,
                        interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def TaxonomySelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, TaxonomySelectWidget(request))
