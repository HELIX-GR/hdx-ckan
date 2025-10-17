import json
from flask import Blueprint

import logging
log = logging.getLogger(__name__)

import sqlalchemy

import ckan.plugins.toolkit as tk
from ckan import model

config = tk.config

hdx_count = Blueprint(u'hdx_count', __name__)


def _get_count(table, type, extra):
    isPrivate=''
    extraQ=''
    if type == 'dataset':
        isPrivate=' and private = FALSE'

    if extra:
        extraQ = "where state='active' and type='{type}' {isPrivate}".format(type=type, isPrivate=isPrivate)

    q = sqlalchemy.text(''' select count(*) from {name} {extra};'''.format(name=table, extra=extraQ))
    result = model.Session.connection().execute(q, entity_id=id).scalar()
    return result


def dataset():
    q = sqlalchemy.text('''
    select
        (select count(*) from package p
            where p.type = 'dataset' and p.state = 'active' and p.private = FALSE)
        -(select count(*) from package p
            left outer join package_extra pe on pe.package_id = p.id
            where pe.key = 'archived' and pe.state = 'active' and pe.value = 'true'
                and p.type = 'dataset' and p.state = 'active' and p.private = FALSE)
    ''')
    result = model.Session.connection().execute(q).scalar()
    return json.dumps({'count': result})


def country():
    return json.dumps({'count': _get_count('"group"', 'group', True)})


# def organization():
#     return json.dumps({'count': _get_count('"group"', 'organization', True)})


def organization():
    """
    Count only top-level organizations (no parent orgs).
    Uses ckanext-hierarchy's 'group_tree' action.
    """
    context = {'user': 'visitor'}
    data_dict = {'type': 'organization'}
    
    try:
        # get_action('group_tree') returns a list of top-level orgs with nested children
        tree = tk.get_action('group_tree')(context, data_dict)
        top_level_count = len(tree)  # each top node = one top-level org
    except Exception as e:
        log.exception(f"Failed to get top-level org count: {e}")
        top_level_count = 0

    return json.dumps({'count': top_level_count})

def source():
    q = sqlalchemy.text('''select count(distinct(pe.value)) from package_extra pe
            inner join package p on pe.package_id = p.id
            where pe.key = 'dataset_source' and p.state='active'
            and p.private=false;''')
    result = model.Session.connection().execute(q, entity_id=id).scalar()
    # extra_src = int(config.get('hdx.homepage.extrasources', '13'))
    extra_src = 0 # DEPRECATED old behaviour above
    return json.dumps({'count': result + extra_src})


def tag():
    return json.dumps({'count': _get_count('tag', 'tag', False)})


def format():
    q = sqlalchemy.text('''select count(distinct(format)) from resource where not format is null;''')
    result = model.Session.connection().execute(q, entity_id=id).scalar()
    return json.dumps({'count': result})


def license():
    q = sqlalchemy.text('''select count(distinct(license_id)) from package where not license_id is null;''')
    result = model.Session.connection().execute(q, entity_id=id).scalar()
    return json.dumps({'count': result})


list = {
    'groups':country,
    'tags':tag,
    'organization':organization,
    'res_format':format,
    'license_id':license
}


hdx_count.add_url_rule(u'/count/dataset', view_func=dataset)
hdx_count.add_url_rule(u'/count/organization', view_func=organization)
hdx_count.add_url_rule(u'/count/country', view_func=country)
hdx_count.add_url_rule(u'/count/source', view_func=source)
