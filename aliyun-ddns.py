#!/usr/bin/env python #coding=utf-8

import os
import sys
import json
import yaml
import requests
from datetime import datetime
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest

def print_header():
  print('\n------------------ Aliyun DDNS ------------------')
  print('-------------- {} --------------'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
  print('-------------------------------------------------')

def load_config():
  config_path = ''
  if len(sys.argv) > 1:
    config_path = sys.argv[1]
  else:
    config_path = os.path.join(sys.path[0], 'config.yaml')
  print('\n=> Config path:\n   ' + config_path)
  with open(config_path, encoding='utf-8') as f:
    cfg = yaml.safe_load(f)
    if cfg is not None and 'accesskey' in cfg and 'domain' in cfg:
      return True, cfg['accesskey'], cfg['domain']
    return False, None, None

def to_dict(b):
  return json.loads(str(b, encoding='utf-8'))

def fetch_ip():
  r = requests.get('https://ipv4.jsonip.com/')
  if r.status_code == 200:
    ip = r.json()['ip']
    print('\n=> IP: ' + ip)
    return True, ip
  return False, None

def fetch_records(domain :str, access_key_dict :dict, domain_dict :dict):
  item = domain_dict[domain]
  ak_ref = item['accesskey']
  ak_item = access_key_dict[ak_ref]
  client = AcsClient(ak_item['id'], ak_item['secret'], ak_item['area'])
  item['client'] = client
  request = DescribeDomainRecordsRequest()
  request.set_accept_format('json')
  request.set_DomainName(domain)
  request.set_PageNumber('1')
  request.set_Type('A')
  request.set_PageSize('500')
  all_records = []
  for host in item['hosts']:
    if item['hosts'][host] is not None:
      request.set_SearchMode('LIKE')
      request.set_KeyWord('.' + host)
    else:
      request.set_SearchMode('EXACT')
      request.set_KeyWord(host)
    try:
      resp = to_dict(client.do_action_with_exception(request))
      domain_records = resp['DomainRecords']
      if resp['TotalCount'] > 0 and domain_records is not None and len(domain_records['Record']) > 0:
        all_records.extend(domain_records['Record'])
    except ServerException as err:
      print("   ERROR: {}".format(err.get_error_msg()))
  return all_records

def diff(sub_domain :str, record_dict :dict, item :dict, ip :str):
  if sub_domain in record_dict:
    record = record_dict[sub_domain]
    if record is not None and record['Value'] != ip:
      item['updates'].append(record)
    else:
      print('     - [Skip] {}'.format(record['RR']))
  else:
    item['adds'].append(sub_domain)

def filter(item: dict, records :list[dict], ip :str):
  item['updates'] = []
  item['adds'] = []
  if len(records) > 0:
    record_dict = {}
    for record in records:
      record_dict[record['RR']] = record
    for host in item['hosts']:
      subs = item['hosts'][host]
      if subs is not None and len(subs) > 0:
        for sub in subs:
          sub_domain = ('{}.{}'.format(sub, host)).replace("@.", "")
          diff(sub_domain, record_dict, item, ip)
      elif host in record_dict:
        diff(host, record_dict, item, ip)
      else:
        print('     - [Skip] {}'.format(record['RR']))

def update_record(client, record, ip):
  request = UpdateDomainRecordRequest()
  request.set_accept_format('json')
  request.set_RecordId(record['RecordId'])
  request.set_RR(record['RR'])
  request.set_Type("A")
  request.set_Value(ip)
  response = client.do_action_with_exception(request)
  r = response is not None and 'RequestId' in to_dict(response)
  print('     - [{}] {}'.format(r, record['RR']))

def add_record(client, domain_name, host, ip):
  request = AddDomainRecordRequest()
  request.set_accept_format('json')
  request.set_DomainName(domain_name)
  request.set_RR(host)
  request.set_Type("A")
  request.set_Value(ip)
  response = client.do_action_with_exception(request)
  r = response is not None and 'RequestId' in to_dict(response)
  print('     - [{}] {}'.format(r, host))

def exec(item :dict, ip :str):
  if 'client' in item:
    client = item['client']
    updates = item['updates']
    adds = item['adds']
    if len(updates) > 0:
      print("   Update:")
      for record in updates:
        update_record(client, record, ip)
    if len(adds) > 0:
      print("   Add:")
      for host in adds:
        add_record(client, item['domain'], host, ip)

def main():
  print_header()
  ok, access_key_dict, domain_dict = load_config()
  if ok:
    ok, ip = fetch_ip()
    if ok:
      for domain in domain_dict:
        print("\n=> Domain: " + domain)
        records = fetch_records(domain,  access_key_dict, domain_dict)
        if len(records) > 0:
          filter(domain_dict[domain], records, ip)
          exec(domain_dict[domain], ip)
  print('\n-------------------------------------------------\n')

main()
