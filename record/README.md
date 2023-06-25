# 直播信息录制
1. 数据库导入表结构`sql_structure.sql`  
   表名为 `直播房间号+"_all_"+当前日期`（如果只保存已知字段，则表名为`直播房间号+"_"+当前日期`）  
   数据库名为`bilibili_live_monitor_backup`
2. 复制一份`config_default.ini`并重命名为`config.ini`，填入数据库配置
3. 运行`record.py`，指定直播房间号与是否只保存已知字段，开始录制直播信息
4. 打开直播间页面控制台，粘贴`record_popularity.js`内代码，调用`recordPopularity()`方法开始录制人气，人气数据可在`本地储存空间 - temp_popularity`查看