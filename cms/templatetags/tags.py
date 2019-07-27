from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def fetch(context, file_name):
	request = context['request']
	url_str = 'http://{}/fetch/{}'.format(request.get_host(), file_name)
	return url_str