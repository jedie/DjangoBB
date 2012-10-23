# coding: utf-8


import unittest

from django.test import TestCase, RequestFactory
from django.conf import settings

from djangobb_forum.models import Post
from djangobb_forum.util import urlize, smiles, convert_text_to_html, paginate


markdown_installed = False
markdown2_installed = False
try:
    # https://github.com/trentm/python-markdown2
    import markdown2
except ImportError:
    try:
        # http://pypi.python.org/pypi/Markdown
        import markdown
    except ImportError:
        pass
    else:
        markdown_installed = True
else:
    markdown2_installed = True


try:
    import pygments
except ImportError:
    pygments_installed = False
else:
    pygments_installed = True


class TestParsers(TestCase):
    def setUp(self):
        self.data_url = "Lorem ipsum dolor sit amet, consectetur http://djangobb.org/ adipiscing elit."
        self.data_smiles = "Lorem ipsum dolor :| sit amet :) <a href=\"http://djangobb.org/\">http://djangobb.org/</a>"
        self.markdown = ""
        self.markdown2 = "markdown test\n\n```python\nprint 'it works'\n```\n\n:)"
        self.bbcode = "[b]Lorem[/b] [code]ipsum :)[/code] =)"

    def test_urlize(self):
        urlized_data = urlize(self.data_url)
        self.assertEqual(urlized_data, u"Lorem ipsum dolor sit amet, consectetur <a href=\"http://djangobb.org/\" rel=\"nofollow\">http://djangobb.org/</a> adipiscing elit.")

    def test_smiles(self):
        smiled_data = smiles(self.data_smiles)
        self.assertEqual(smiled_data, u"Lorem ipsum dolor <img src=\"{0}djangobb_forum/img/smilies/neutral.png\" /> sit amet <img src=\"{0}djangobb_forum/img/smilies/smile.png\" /> <a href=\"http://djangobb.org/\">http://djangobb.org/</a>".format(settings.STATIC_URL))

    def test_convert_text_to_html(self):
        bb_data = convert_text_to_html(self.bbcode, 'bbcode')
        self.assertEqual(bb_data, "<strong>Lorem</strong> <div class=\"code\"><pre>ipsum :)</pre></div>=)")

    @unittest.skipUnless(markdown2_installed and pygments_installed, "test only for markdown2 with pygments")
    def test_markdown2_with_pygments(self):
        html = convert_text_to_html(self.markdown2, 'markdown')
        self.assertEqual(html, """<p>markdown test</p>\n\n<div class="codehilite"><pre><code><span class="k">print</span> <span class="s">&#39;it works&#39;</span>\n</code></pre></div>\n\n<p>:)</p>\n""")

    @unittest.skipUnless(markdown2_installed and not pygments_installed, "test only for markdown2 without pygments")
    def test_markdown2_without_pygments(self):
        html = convert_text_to_html(self.markdown2, 'markdown')
        self.assertEqual(html, "<p>markdown test\n<code>python\nprint 'it works'\n</code>\n:)</p>\n")


class TestPaginators(TestCase):
    fixtures = ['test_forum.json']

    def setUp(self):
        self.posts = Post.objects.all()[:5]
        self.factory = RequestFactory()

    def test_paginate(self):
        request = self.factory.get('/?page=2')
        pages, paginator, _ = paginate(self.posts, request, 3)
        self.assertEqual(pages, 2)

        request = self.factory.get('/?page=1')
        _, _, paged_list_name = paginate(self.posts, request, 3)
        self.assertEqual(paged_list_name.count(), 3)


class TestVersion(TestCase):
    def test_get_version(self):
        import djangobb_forum

        djangobb_forum.version_info = (0, 2, 1, 'f', 0)
        self.assertEqual(djangobb_forum.get_version(), '0.2.1')
        djangobb_forum.version_info = (2, 3, 1, 'a', 5)
        self.assertIn('2.3.1a5.dev', djangobb_forum.get_version())
