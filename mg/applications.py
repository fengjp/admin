#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
role   : 管理端 Application
"""

from websdk.application import Application as myApplication
from mg.handlers.verify_handler import sso_urls
from mg.handlers.login_handler import login_urls
from mg.handlers.users_handler import user_mg_urls
from mg.handlers.roles_handler import roles_urls
from mg.handlers.functions_handler import functions_urls
from mg.handlers.menus_handler import menus_urls
from mg.handlers.components_handler import components_urls
from mg.handlers.app_mg_handler import app_mg_urls
from mg.handlers.app_settings_handler import app_settings_urls
from mg.handlers.notifications_handler import notifications_urls
from mg.handlers.dictconfig_handler import dictconfig_urls
from mg.handlers.stakeholder_handler import stakeholder_urls
from mg.handlers.company_handler import company_urls
from mg.handlers.people_handler import peoplelist_urls
from mg.handlers.post_handler import postlist_urls


class Application(myApplication):
    def __init__(self, **settings):
        urls = []
        urls.extend(sso_urls)
        urls.extend(user_mg_urls)
        urls.extend(login_urls)
        urls.extend(roles_urls)
        urls.extend(functions_urls)
        urls.extend(components_urls)
        urls.extend(menus_urls)
        urls.extend(app_mg_urls)
        urls.extend(app_settings_urls)
        urls.extend(notifications_urls)
        urls.extend(dictconfig_urls)
        urls.extend(stakeholder_urls)
        urls.extend(company_urls)
        urls.extend(peoplelist_urls)
        urls.extend(postlist_urls)
        super(Application, self).__init__(urls, **settings)


if __name__ == '__main__':
    pass
