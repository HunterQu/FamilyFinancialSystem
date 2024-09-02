# FamilyFinancialSystem

- 本项目使用 BootStrap + Django + Mysql, Echarts🤗
- doc📖: [飞书](https://rcnnsv5zghgq.feishu.cn/wiki/HL75wi4xui8n20kOFtOcZeSGnOc?from=from_copylink)

## python依赖安装

**Python版本为3.8.10**

```bash
#在你的虚拟环境中安装依赖
pip install -r requirements.txt
```

## 启动服务器
> **注意运行前请配置config\config.json,具体操作教程见config目录下readme.md**
> 
```bash
python manage.py runserver
```

## 创建管理员用户

```bash
#先进行数据库迁移
python manage.py migrate

#创建用户（输入命令后根据提示创建）
python manage.py createsuperuser
```

创建完成后即可访问`http://127.0.0.1:8000/admin/` 登录管理页面

![Alt](https://repobeats.axiom.co/api/embed/d9e762e476542e1591b20afca0d1d61a434bee2b.svg "Repobeats analytics image")