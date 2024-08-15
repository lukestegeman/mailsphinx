from ..utils import format_objects
from ..utils import config

import datetime

# BUILD HTML OBJECTS
def build_section_title(title, base_indent=0):
    text =  (base_indent + 0) * config.html.indent + '<div class="section_title">\n'
    text += (base_indent + 1) * config.html.indent + '<p>' + title + '</p>\n'
    text += (base_indent + 0) * config.html.indent + '</div>\n'
    return text

def build_paragraph_title(title, base_indent=0, sublevel=0):
    text =  (base_indent + 0) * config.html.indent + '<div class="' + sublevel * 'sub' + 'paragraph_title">\n'
    text += (base_indent + 1) * config.html.indent + '<p>' + title + '</p>\n'
    text += (base_indent + 0) * config.html.indent + '</div>\n'
    return text

def build_regular_text(regular_text, base_indent=0):
    text = (base_indent + 0) * config.html.indent + '<div class="regular_text">\n'
    text += (base_indent + 1) * config.html.indent + '<p>' + regular_text + '</p>\n'
    text += (base_indent + 0) * config.html.indent + '</div>\n'
    return text

def build_table(headers, table_data, base_indent=0, header_color=config.color.associations['Neutral'], header_color_dict=None):
    """
    Writes the html that displays a table.
    
    Parameters
    ----------
    headers : list of strings

    table_data : list of lists of strings

    Returns
    -------
    text : string
    """
    text = ''
    text += (base_indent + 0) * config.html.indent + '<table class="table_block" role="presentation">\n'
    text += (base_indent + 1) * config.html.indent + '<thead style="background-color: ' + header_color + '">\n'
    text += (base_indent + 2) * config.html.indent + '<tr>\n'
    for i in range(0, len(headers)):
        style_string = ''
        if (header_color_dict is not None):
            if headers[i] in list(header_color_dict.keys()) and (header_color_dict[headers[i]] is not None):
                style_string = ' style="background-color: ' + header_color_dict[headers[i]] + ';"'
        text += (base_indent + 3) * config.html.indent + '<th' + style_string + '>' + headers[i] + '</th>\n'
    text += (base_indent + 2) * config.html.indent + '</tr>\n'
    text += (base_indent + 1) * config.html.indent + '</thead>\n'
    for i in range(0, len(table_data)):
        text += (base_indent + 1) * config.html.indent + '<tbody>\n'
        text += (base_indent + 2) * config.html.indent + '<tr>\n'
        for j in range(0, len(table_data[i])):
            style_string = ''
            text += (base_indent + 3) * config.html.indent + '<td' + style_string + '>' + format_objects.format_df_datetime(table_data[i][j]) + '</td>\n' 
        text += (base_indent + 2) * config.html.indent + '</tr>\n'
        text += (base_indent + 1) * config.html.indent + '</tbody>\n'
    text += (base_indent + 0) * config.html.indent + '</table>\n'
    return text

def build_image(image_filename, base_indent=0):
    text = ''
    text += (base_indent + 0) * config.html.indent + '<table border="0" cellpadding="0" cellspacing="0" class="image_block" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">\n'
    text += (base_indent + 1) * config.html.indent + '<tr>\n'
    text += (base_indent + 2) * config.html.indent + '<td class="pad" style="width:100%;">\n'
    text += (base_indent + 3) * config.html.indent + '<div align="center" class="alignment" style="line-height:10px">\n'
    text += (base_indent + 4) * config.html.indent + '<div style="max-width: 1000px;"><img height="auto" src="' + image_filename + '" style="display: block; height: auto; border: 0; width: 100%;" width="1000"/></div>\n'
    text += (base_indent + 3) * config.html.indent + '</div>\n'
    text += (base_indent + 2) * config.html.indent + '</td>\n'
    text += (base_indent + 1) * config.html.indent + '</tr>\n'
    text += (base_indent + 0) * config.html.indent + '</table>\n'
    return text

def build_html_shortlink(link, text):
    text = '<a href="' + link + '">' + text + '</a>'
    return text

def build_head_section():
    """
    Writes the html that makes up the front matter of the email body.

    Parameters
    ----------
    None
    
    Returns
    -------
    test : string
    """
    a = open(config.path.email_header_template, 'r')
    text = a.read() + '\n'
    a.close()
    gmt_datetime = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0).strftime('%Y-%m-%d %H:%M %Z')
    text = text.replace('${generation_time}$', 'Report Generation Time: ' + gmt_datetime)
    return text

def build_close_section():
    text = ''
    text += config.html.indent * 5 + '</td>\n' 
    text += config.html.indent * 4 + '</tr>\n'
    text += config.html.indent * 3 + '</tbody>\n'
    text += config.html.indent * 2 + '</table>\n'
    text += config.html.indent * 1 + '</body>\n'
    text += config.html.indent * 0 + '</html>\n'
    return text

def build_divider(base_indent=0):
    text =  (base_indent + 0) * config.html.indent + '<table border="0" cellpadding="10" cellspacing="0" class="divider_block" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">\n'
    text += (base_indent + 1) * config.html.indent + '<tbody>\n'
    text += (base_indent + 2) * config.html.indent + '<tr>\n'
    text += (base_indent + 3) * config.html.indent + '<td class="pad">\n'
    text += (base_indent + 4) * config.html.indent + '<div align="center" class="alignment">\n'
    text += (base_indent + 5) * config.html.indent + '<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;" width="100%">\n'
    text += (base_indent + 6) * config.html.indent + '<tbody>\n'
    text += (base_indent + 7) * config.html.indent + '<tr>\n'
    text += (base_indent + 8) * config.html.indent + '<td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 10px solid ' + config.color.associations['Divider'] + ';">\n'
    text += (base_indent + 9) * config.html.indent + '<span style="word-break: break-word;">&hairsp;</span>\n'
    text += (base_indent + 8) * config.html.indent + '</td>\n'
    text += (base_indent + 7) * config.html.indent + '</tr>\n'
    text += (base_indent + 6) * config.html.indent + '</tbody>\n'
    text += (base_indent + 5) * config.html.indent + '</table>\n'
    text += (base_indent + 4) * config.html.indent + '</div>\n'
    text += (base_indent + 3) * config.html.indent + '</td>\n'
    text += (base_indent + 2) * config.html.indent + '</tr>\n'
    text += (base_indent + 1) * config.html.indent + '</tbody>\n'
    text += (base_indent + 0) * config.html.indent + '</table>\n'
    return text



