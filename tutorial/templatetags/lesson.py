# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error

from django.contrib.auth.models import User
from django.conf import settings
from django.template import Context, Library, Node, TemplateSyntaxError
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from tutorial.models import Problem, Submission
from tutorial.problems import load_problem


register = Library()

ideal_user = User.objects.get(username='admin')

LESSON_IMG_ROOT = '/static/images/lesson_images/'


def _render_code_to_html(**kwargs):
    return get_template('code.html').render(Context(kwargs))


class ProblemLinkNode(Node):
    def __init__(self, problem_ref):
        self.problem_ref = problem_ref

    def render(self, context):
        problem_urlname = context[self.problem_ref]['urlname']
        problem = load_problem(Problem.objects.get(urlname=problem_urlname))
        user = context['request'].user
        if user.is_authenticated():
            statuses = [submission.get_status_display() for submission 
                    in Submission.objects.filter(user=user, problem=problem['db_object'])]
        else:
            statuses = []
        if 'ok' in statuses:
            css_class = 'okProblemLink'
        elif 'error' in statuses:
            css_class = 'errorProblemLink'
        else:
            css_class = 'unsubmittedProblemLink'
        return '<span class="{0}">{1}</span>'.format(css_class, problem['name'])


@register.tag('problem_link')
def get_problem_link(parser, token):
    try:
        tag_name, problem_ref = token.split_contents()
    except ValueError:
        msg = '{0} tag requires a single argument'.format(token.split_contents()[0])
        raise TemplateSyntaxError(msg)
    return ProblemLinkNode(problem_ref)


class IdealSolutionNode(Node):
    def __init__(self, problem_ref):
        self.problem_ref = problem_ref

    def render(self, context):
        problem_urlname = context[self.problem_ref]['urlname']
        problem = load_problem(Problem.objects.get(urlname=problem_urlname))

        user = context['request'].user
        if not user.is_authenticated():
            return ''

        user_solution = Submission.objects.filter(user=user, problem=problem['db_object'], status=1).order_by('time').last()
        if user_solution is None:
            return ''

        ideal_solution = Submission.objects.filter(user=ideal_user, problem=problem['db_object'], status=1).order_by('-time').first()
        if user_solution is not None:
            return '''
	<table class="table problem_user_and_ideal_solutions hidden-xs hidden-md">
		<thead>
			<tr>
				<th>Ваше решение</td>
				<th>Эталонное решение</td>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>
					{user_solution}
				</td>
				<td>
					{ideal_solution}
				</td>
			</tr>
		</tfoot>
	</table>'''.format(**{
                'user_solution': _render_code_to_html(code = user_solution.code,
                                                      context = context,
                                                      executable = False),

                'ideal_solution': _render_code_to_html(code = ideal_solution.code,
                                                       context=context,
                                                       executable=False),
            })

        else:
            return ''


@register.tag('ideal_solution')
def get_ideal_solution_link(parser, token):
    try:
        tag_name, problem_ref = token.split_contents()
    except ValueError:
        msg = '{0} tag requires a single argument'.format(token.split_contents()[0])
        raise TemplateSyntaxError(msg)
    return IdealSolutionNode(problem_ref)


def render_section(this, nesting_level=0):
    content = this.get('text', '')
    if 'subsections' in this:
        for subsection in this['subsections']:
            content += render_section(subsection, nesting_level + 1)
    else:
        if content.strip() == '':
            return ''
        else:
            return content

    return get_template('lesson_section.html').render(Context({
        'id': this['id'],
        'title': this['title'],
        'nesting_level': nesting_level,
        'content': content,
    }))

@register.filter
def lesson_content(lesson):
    content = ''

    for section in lesson['content']:
        content += render_section(section)

    return mark_safe(content)


def render_section_navitem(title, section_id, subsections):
    subsections_rendered = ''

    for subsection in subsections:
        subsections_rendered += render_section_navitem(*subsection)

    return get_template('lesson_section_navitem.html').render(Context({
        'id': section_id,
        'title': title,
        'subsections': subsections_rendered,
    }))

@register.filter
def lesson_navbar(lesson):
    navbar = ''

    for section in lesson['sections']:
        navbar += render_section_navitem(*section)

    return mark_safe(navbar)
