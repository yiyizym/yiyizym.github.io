---
layout: post
title:  fiddler 使用技巧及其他经验总结
date: 2017-09-02 01:19:47
description: 最近一直在用 fiddler ，分享一下使用过程中踩过的坑和经验，不定期更新
categories: frontend
---
**序**

本文适合使用过 fiddler 、对它有所了解的朋友阅读，如果你不知道 fiddler 是什么，大概没必要继续读下去。

以下内容基于：

- 操作系统：windows 10
- fiddler 版本：v4.6

**解决跨域问题**

用 fiddler 解决跨域问题的原理是通过规则来设置响应头的相应字段。
在 fiddler 右侧的 "详情和数据统计面板" 中找到 FiddlerScript 标签页，里面是一个脚本文件，语法有点像 typeScript ，不难看懂，里面只定义了一个 Handlers 类，可以通过它来编辑 fiddler 菜单栏中的 Rules 选项以及 fiddler 处理请求的回调函数。

第一步，往菜单栏的 Rules 选项中增加一个“强制启用 CORS”的规则。在 Handlers 类的开头，找到定义规则的几行代码，其中“隐藏 304 响应条目”的代码是这样写的（下面的注释是本人添加的，原代码没有）：
```
public static RulesOption("Hide 304s") // 用户在 Rules 中看到的规则名字是 "Hide 304s"
var m_Hide304s: boolean = false; // 默认关闭
```

在这几行代码后面，如法炮制，添加以下两行代码：
```
public static RulesOption("Force CORS Response") // 用户在 Rules 中看到的规则名字是 "Force CORS Response"
var m_ForceCORS: boolean = true; // 默认开启
```

![添加强制启用 CORS 规则的代码]({{ site.url }}/assets/m_ForceCORS.png)*添加强制启用 CORS 规则的代码*


![添加成功后 Rules 中会多出一条 Force CORS Response 规则]({{ site.url }}/assets/rules.png)*添加成功后 Rules 中会多出一条 Force CORS Response 规则*

第二步，往 Handlers 类的静态方法 OnBeforeResponse 中增加以下代码，目的是在把响应返回给终端之前，往响应头塞一些字段：
```
if (m_ForceCORS &&
        (
            oSession.oRequest.headers.HTTPMethod == "OPTIONS" ||
            oSession.oRequest.headers.Exists("Origin")
        )
)
{                                
    if(!oSession.oResponse.headers.Exists("Access-Control-Allow-Origin"))
        oSession.oResponse.headers.Add("Access-Control-Allow-Origin", "*");
    
    if(!oSession.oResponse.headers.Exists("Access-Control-Allow-Methods"))
        oSession.oResponse.headers.Add("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    
    if(oSession.oRequest.headers.Exists("Access-Control-Request-Headers"))
    {
        if(!oSession.oResponse.headers.Exists("Access-Control-Allow-Headers"))
            oSession.oResponse.headers.Add(
                "Access-Control-Allow-Headers"
                , oSession.oRequest.headers["Access-Control-Request-Headers"]
            );
    }
    
    if(!oSession.oResponse.headers.Exists("Access-Control-Max-Age"))
        oSession.oResponse.headers.Add("Access-Control-Max-Age", "1728000");
    
    if(!oSession.oResponse.headers.Exists("Access-Control-Allow-Credentials"))
        oSession.oResponse.headers.Add("Access-Control-Allow-Credentials", "true");
    
    oSession.responseCode = 200;
}
```

![在 OnBeforeResponse 添加相关代码]({{ site.url }}/assets/OnBeforeResponse.png)*在 OnBeforeResponse 添加相关代码*

**匹配请求**

TODO

**参考**
- [Using Fiddler to emancipate HttpOnly cookies for web app debugging](http://simplyaprogrammer.com/2013/10/using-fiddler-to-emancipate-httponly.html)
- [Using Fiddler to force a web service to support CORS for debugging](http://simplyaprogrammer.com/2013/12/using-fiddler-to-force-web-service-to.html)