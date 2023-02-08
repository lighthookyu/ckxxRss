# ckxxRss
该项目为《参考消息》RSS服务端，以flask建立服务器，访问后实时爬取参考消息官网不同板块的信息，编制成xml返回

RSS客户端中填写的地址为：

    0.0.0.0:9000/get?block=板块
    
  其中不同板块分别为：
  
|填入  |  释义|
|--|--|
|yaowen  | 要闻   |
|zhongguo|中国|
|guancha|观察中国|
|guoji|国际|
|luntan|论坛|
|jingji|经济|
|zhiku|智库|

示例：

     0.0.0.0:9000/get?block=yaowen

