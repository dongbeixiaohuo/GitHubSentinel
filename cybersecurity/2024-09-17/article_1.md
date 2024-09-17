# CVE-2024-21096：MySQLDump提权漏洞分析

链接：https://www.freebuf.com/vuls/411090.html

时间：2024-09-14

内容：CVE-2024-21096是一个中等严重性的漏洞，它影响Oracle MySQL Server产品中的mysqldump组件。成功利用此漏洞的未认证攻击者可能对MySQL Server的数据进行未授权的更新、插入或删除操作，还可以读取MySQL Server可访问数据的一部分，并可能导致MySQL Server部分拒绝服务（partial DOS）。利用该漏洞的攻击需要在MySQL Server的本地进行，因此利用条件有限，利用复杂性也较高，该漏洞主要影响8.0.0版本至8.0.36版本之间的MySQL Server。

mysqldump是MySQL的一个组件，可以用于将 MySQL 数据库的数据和结构导出到一个文本文件中，该文件通常是 SQL 格式。这个文件随后可以被用来备份数据库、迁移数据或在另一个 MySQL 服务器上重建数据库。

比如用mysqldump导出MySQL数据库中的某个数据库，可以在MySQL Server本地用以下命令：
