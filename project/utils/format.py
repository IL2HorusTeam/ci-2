# -*- coding: utf-8 -*-


def format_remote_file_link(remote_file):
    return format_html_link(url=remote_file['alternateLink'],
                            text=remote_file['title'])


def format_html_link(url, text):
    return "<a href='{}' target='_blank'>{}</a>".format(url, text)
