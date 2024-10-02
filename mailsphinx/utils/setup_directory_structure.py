from ..utils import config

import os
import shutil

def make_directories():
    if not os.path.exists(config.path.filesystem):
        os.makedirs(config.path.filesystem)
    if not os.path.exists(config.path.report):
        os.makedirs(config.path.report)
    if not os.path.exists(config.path.email_storage):
        os.makedirs(config.path.email_storage)
    if not os.path.exists(config.path.email_image):
        os.makedirs(config.path.email_image)

def get_directory_structure_as_html(directory, indent_level=0, exclude_files=[]):
    html = convert_directory_structure_to_html(directory, indent_level, exclude_files) 
    directory_structure_html = config.html.indent + '<ul>\n' + html + config.html.indent + '</ul>\n'
    return directory_structure_html

def convert_directory_structure_to_html(directory, indent_level=0, exclude_files=[]):
    html = ''
    files_and_directories = sorted(os.listdir(directory))
    for thing in files_and_directories:
        if thing in exclude_files:
            continue
        path = os.path.join(directory, thing)
        if os.path.isdir(path):
            html += config.html.indent * (indent_level + 1) + '<li>\n'
            html += config.html.indent * (indent_level + 2) + '<span class="collapsible">' + thing + '</span>\n'
            html += config.html.indent * (indent_level + 2) + '<ul class="nested">\n'
            html += convert_directory_structure_to_html(os.path.join(directory, thing), indent_level=indent_level + 2)
            html += config.html.indent * (indent_level + 2) + '</ul>\n'
            html += config.html.indent * (indent_level + 1) + '</li>\n'
        else:
            relative_path = os.path.relpath(path, config.path.filesystem)
            html += config.html.indent * (indent_level + 1) + '<li><a href="' + relative_path + '">' + thing + '</a></li>\n'
    return html

def make_index_html():
    
    directory_structure_html = get_directory_structure_as_html(config.path.filesystem, indent_level=1, exclude_files=['index.html', 'styles.css'])
    a = open(config.path.index_template, 'r')
    html = a.read()
    a.close()
    html = html.replace('${directory-structure}$', directory_structure_html)

    a = open(config.path.index, 'w')
    a.write(html)
    a.close() 

    shutil.copy(config.path.index_template_stylesheet, config.path.index_stylesheet)


