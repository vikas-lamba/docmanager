#!/usr/bin/python3

import json
import pytest
from docmanager import parsecli
from docmanager.action import Actions

def test_docmanager_jsonout(tmp_valid_xml, capsys):
    """ Test the json output format """
    tmp_file = tmp_valid_xml.strpath

    # set some test values
    clicmd = 'set -p hello=world -p suse=green -p json=test {}'.format(tmp_file)
    Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()

    # read only 2 properties
    clicmd = 'get -p hello -p suse {} --format json'.format(tmp_file)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()

    not_json = False
    try:
        out_json = json.loads(out)
    except ValueError as e:
        not_json = True

    assert not_json == False, "Output is not JSON."

    json_inv_data = "Returned JSON contains invalid data."

    assert out_json[tmp_file]['hello'] == 'world', json_inv_data
    assert out_json[tmp_file]['suse'] == 'green', json_inv_data

    # read all properties
    clicmd = 'get {} --format json'.format(tmp_file)
    a = Actions(parsecli(clicmd.split()))
    out, err = capsys.readouterr()

    not_json = False
    try:
        out_json = json.loads(out)
    except ValueError as e:
        not_json = True

    assert not_json == False, "Output is not JSON."

    json_inv_data = "Returned JSON contains invalid data."
    
    assert out_json[tmp_file]['hello'] == 'world', json_inv_data
    assert out_json[tmp_file]['suse'] == 'green', json_inv_data
    assert out_json[tmp_file]['json'] == 'test', json_inv_data
