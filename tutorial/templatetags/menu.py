from django import template
from django.core import urlresolvers
from django.template import Node


register = template.Library()

class IfPageIsNode(Node):
    def __init__(self, if_page, nodelist):
        self.if_page = if_page
        self.nodelist = nodelist

    def render(self, context):
        try:
            resolved = urlresolvers.resolve(context.get('request').path)
            return self.nodelist.render(context) if resolved.url_name == self.if_page else ''
        except:
            return []

@register.tag
def ifpageis(parser, token):
    tag_name, if_page = token.split_contents()
    nodelist = parser.parse(('endif',))
    parser.delete_first_token()
    return IfPageIsNode(if_page, nodelist)
