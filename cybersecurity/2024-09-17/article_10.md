# 从蓝队流量角度分析Shiro-550反序列化漏洞

链接：https://www.freebuf.com/vuls/410346.html

时间：2024-09-05

内容：Apache Shiro是一个强大且易用的Java安全框架，执行身份验证、授权、密码和会话管理。Shiro的优势在于轻量级，使用简单、上手更快、学习成本低。

Shiro反序列化原理：Apache Shiro框架提供了 RememberMe 功能，用户登陆成功后会生成经过加密并编码的cookie，在服务端接收cookie值后，Base64解码–>AES解密–>反序列化。因此攻击者只要找到AES加密的密钥，就可以构造一个恶意对象，对其进行序列化–>AES加密–>Base64编码，然后将其作为cookie的rememberMe字段发送，Shiro将rememberMe进行解密并且反序列化，最终造成反序列化漏洞。

在 Apache Shiro<=1.2.4 版本中 AES 加密时采用的 key 是硬编码在代码中的，这就为伪造 cookie 提供了机会。只要 rememberMe 的 AES 加密密钥泄露，无论 shiro 是什么版本都会导致反序列化漏洞
