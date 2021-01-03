#!/usr/bin/env python #coding=utf-8

import json
import requests
from datetime import datetime
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest

FETCH_IP_URL = 'https://ipv4.jsonip.com/'

# 要修改的主机记录
RECORD_RR = '@'
# 要操作的域名
DOMAIN = 'aliyun.com'

# 阿里云AccessKey ID
ACCESSKEY_ID = 'hello '
# 阿里云AccessKey Secret
ACCESSKEY_SECRET = 'world.'

AREA = 'cn-hangzhou'

client = AcsClient(ACCESSKEY_ID, ACCESSKEY_SECRET, AREA)

def print_header():
    print('\n------------------ Aliyun DDNS ------------------')
    print('-------------- {} --------------'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print('-------------------------------------------------')
    print('\n=> Info:\n\tDomain: {}\n\tRR: \t{}'.format(DOMAIN, RECORD_RR))

def to_dict(b):
    return json.loads(str(b, encoding='utf-8'))

def fetch_ip():
    r = requests.get(FETCH_IP_URL)
    if r.status_code == 200:
        ip = r.json()['ip']
        print('\n=> IP: {}'.format(ip))
        return ip
    return None

def fetch_record():
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    
    request.set_DomainName(DOMAIN)
    request.set_PageNumber('1')
    request.set_PageSize('100')
    request.set_RRKeyWord(RECORD_RR)
    
    response = client.do_action_with_exception(request)
    resp = to_dict(response)
    
    records = resp['DomainRecords']
    if resp['TotalCount'] >= 1 and records is not None and len(records) > 0 and len(records['Record']) > 0:
        record = resp['DomainRecords']['Record'][0]
        print('\n=> Record: \n\tStatus:   {}\n\tRR: \t  {}\n\tValue: \t  {}\n\tRecordId: {}'.format(
                record['Status'],
                record['RR'],
                record['Value'],
                record['RecordId']
                ))
        return record
    return None

def update_record(record, ip):
    if record['Value'] == ip:
        print('\n=> Exited: The DNS record already exists.')
    else:
        request = UpdateDomainRecordRequest()
        request.set_accept_format('json')

        request.set_RecordId(record['RecordId'])
        request.set_RR(RECORD_RR)
        request.set_Type("A")
        request.set_Value(ip)

        response = client.do_action_with_exception(request)
        r = response is not None and 'RequestId' in to_dict(response)
        print('\n=> Updated: {0}'.format(r))

def main():
    print_header()
    record = fetch_record()
    if record is None:
        print('\n=> Exited: Record is None.')
    else:
        ip = fetch_ip()
        if ip is None:
            print('\n=> Exited: IP is None.')
        else:
            update_record(record, ip)
    print('\n---------------------- End ----------------------\n')

main()
