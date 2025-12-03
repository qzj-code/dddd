"""
@Project     : flights
@Author      : ciwei
@Date        : 2024/10/18
@Description :
@versions    : 1.0.0.0
"""
import bs4


class HtmlParseUtils:

    @classmethod
    def parse_form_one(cls, html_text: str, form_attrs: dict, input_attrs: dict):
        html_tag = bs4.BeautifulSoup(html_text, 'lxml')
        form_tag = html_tag.find('form', attrs=form_attrs)
        input_tags = form_tag.find_all('input', attrs=input_attrs)
        result_submit_data_dict = {}

        for i in input_tags:
            if 'name' in i.attrs:
                result_submit_data_dict[i['name']] = i['value']

        return form_tag['action'], result_submit_data_dict
