import json

import ckan.plugins.toolkit as tk

import ckanext.hdx_package.helpers.custom_validator as vd
from ckan.lib.navl.dictization_functions import Missing
import logging

log = logging.getLogger(__name__)
h = tk.h
_get_action = tk.get_action


class ContributeFlowReadLogic(object):
    def __init__(self, dataset_dict):
        self.dataset_dict = dataset_dict

    def process_all(self):
        self.process_groups()
        self.process_tags()
        self.process_dataset_preview_edit()
        self.process_custom_viz()
        self.process_resource_grouping_edit()
        self.pre_process_dataset_date()
        self.process_maintainer()

    def process_groups(self):
        if self.dataset_dict and not self.dataset_dict.get('locations'):
            self.dataset_dict['locations'] = [item.get('name') for item in self.dataset_dict.get("groups")]

    def process_tags(self):
        if not self.dataset_dict:
            return

        tags = self.dataset_dict.get('tags', Missing)
        if tags is Missing or not tags:
            self.dataset_dict['tag_string'] = ''
            return

        # get closed vocabulary ID
        try:
            vocab = tk.get_action('vocabulary_show')({}, {'id': 'closed_tags'})
            closed_vocab_id = vocab['id']
        except tk.ObjectNotFound:
            closed_vocab_id = None

        # get dataset category vocabulary ID
        try:
            vocab = tk.get_action('vocabulary_show')({}, {'id': 'dataset_categories'})
            dataset_category_id = vocab['id']
        except tk.ObjectNotFound:
            dataset_category_id = None

        # keep only free tags
        free_tags = [t['name'] for t in tags if t and t.get('vocabulary_id') != closed_vocab_id and t.get('vocabulary_id') != dataset_category_id]
        self.dataset_dict['tag_string'] = ', '.join(free_tags)

    def pre_process_dataset_date(self):
        if self.dataset_dict and 'dataset_date' in self.dataset_dict:
            if 'TO' in self.dataset_dict.get('dataset_date'):
                _date = self.dataset_dict.get('dataset_date')
                _date_list = str(_date).replace('[', '').replace(']', '').replace(' ', '').split('TO')
                result = []
                for item in _date_list:
                    result.append(item.split('T')[0])
                self.dataset_dict['dataset_date'] = 'TO'.join(result)
                if '*' in self.dataset_dict['dataset_date']:
                    self.dataset_dict['ui_date_ongoing'] = "1"
                self.dataset_dict['dataset_date'] = self.dataset_dict['dataset_date'].replace('*','')
            else:
                _date_list = self.dataset_dict['dataset_date'].split('-')
                if len(_date_list) == 2:
                    self.dataset_dict['dataset_date'] = 'TO'.join(_date_list)
                else:
                    self.dataset_dict['dataset_date'] = _date_list[0]+'TO'+_date_list[0]

    def process_dataset_preview_edit(self):
        if self.dataset_dict:
            dataset_preview = self.dataset_dict.get('dataset_preview', vd._DATASET_PREVIEW_FIRST_RESOURCE)
            if dataset_preview and \
                (dataset_preview == vd._DATASET_PREVIEW_FIRST_RESOURCE
                 or dataset_preview == vd._DATASET_PREVIEW_RESOURCE_ID):
                self.dataset_dict['dataset_preview_check'] = '1'

    def process_custom_viz(self):
        if self.dataset_dict.get('customviz'):
            custom_url_list = [item.get('url') for item in self.dataset_dict.get('customviz')]
            self.dataset_dict['customviz_list'] = json.dumps(custom_url_list)

    def process_resource_grouping_edit(self):
        if self.dataset_dict.get('resource_grouping'):
            self.dataset_dict['resource_grouping'] = u', '.join(self.dataset_dict.get('resource_grouping'))

    def process_maintainer(self):
        maintainer_dict = _get_action('user_show')({'ignore_auth': True}, {'id': self.dataset_dict.get('maintainer', None)})
        if maintainer_dict:
            self.dataset_dict['maintainer'] = maintainer_dict.get('name', None)
