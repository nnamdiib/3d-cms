from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def fetch(context, file_path):
	request = context['request']
	file_name = file_path.split("/")[-1]
	url_str = 'http://{}/fetch/{}'.format(request.get_host(), file_name)
	return url_str

@register.simple_tag(takes_context=True)
def get_file_name(context, file_path):
	request = context['request']
	file_name = file_path.split(".")[0].split("/")[-1]
	return file_name