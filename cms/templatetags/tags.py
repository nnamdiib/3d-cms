from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def fetch_url(context, file_name, file_type=None):
	request = context['request']
	url_str = 'http://{}/fetch/{}.stl'.format(request.get_host(), file_name)
	if file_type == 'extra':
		url_str = 'http://{}/fetch/extra/{}.stl'.format(request.get_host(), file_name)
	return url_str