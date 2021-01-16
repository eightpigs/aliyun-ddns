# Aliyun-DDNS

获取当前公网IP并动态修改阿里云DNS。

## 使用

请阅读 [example config.yaml](./config.yaml)

#### 运行

```shell
pip3 install -r requirements.txt
# 可指定配置文件路径
python3 ./aliyun-ddns.py [~/.config/ddns-config.yaml]
```

运行结果

```
------------------ Aliyun DDNS ------------------
-------------- 2021-01-01 01:01:01 --------------
-------------------------------------------------

=> Config path:
   ./config.yaml

=> IP: 111.111.111.111

=> Domain: aliyun.com
     - [Skip] www
   Update:
     - [True] @
     - [True] api
   Add:
     - [True] console
     - [True] dns.console
     - [False] ecs.console

=> Domain: baidu.com
   ...

=> Domain: qq.com
   ...
-------------------------------------------------
```

#### 定时运行

如果IP频繁变更，则可以加入Cron Job中

```shell
crontab -e
# 例如，每隔4小时运行一次
# 0 */4 * * * python3 aliyun-ddns.py > /var/log/aliyun-ddns.log
```
