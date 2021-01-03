# Aliyun-DDNS

获取当前公网IP动态修改阿里云DNS。

**不支持批量修改，若需要批量修改请自行调整。**

## 使用

#### 修改配置

修改`aliyun-ddns.py`中`14-24`行的域名和API AccessKey配置

```python
# 要修改的主机记录
RECORD_RR = '@'
# 要操作的域名
DOMAIN = 'aliyun.com'

# 阿里云AccessKey ID
ACCESSKEY_ID = 'hello '
# 阿里云AccessKey Secret
ACCESSKEY_SECRET = 'world.'

AREA = 'cn-hangzhou'
```

#### 运行

```shell
pip3 install -r requirements.txt
python3 ./aliyun-ddns.py
```

运行结果

```
------------------ Aliyun DDNS ------------------
-------------- 2021-01-03 15:44:00 --------------
-------------------------------------------------

=> Info:
        Domain: aliyun.com
        RR:     @

=> Record:
        Status:   ENABLE
        RR:       @
        Value:    127.0.0.1
        RecordId: 123123123123132123

=> IP: 123.11.11.11

=> Updated: True

---------------------- End ----------------------
```


#### 定时运行

如果IP频繁变更，则可以加入Cron Job中

```shell
crontab -e
# 例如，每隔4小时运行一次
# 0 */4 * * * python3 aliyun-ddns.py > /var/log/aliyun-ddns.log
```
