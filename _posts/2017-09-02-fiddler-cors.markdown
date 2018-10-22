---
layout: post_with_octocat
title:  fiddler 使用技巧及其他经验总结
date: 2017-09-02 01:19:47
description: 最近一直在用 fiddler ，分享一下使用过程中踩过的坑和经验，不定期更新
categories: frontend
---
## 序

本文适合使用过 fiddler 、对它有所了解的朋友阅读。

以下内容基于：

- 操作系统：windows 10
- fiddler 版本：v4.6

## 解决跨域问题

### 通用情况

用 fiddler 解决跨域问题的原理是通过规则来设置响应头的相应字段。
在 fiddler 右侧的 "详情和数据统计面板" 中找到 FiddlerScript 标签页，里面是一个脚本文件，语法有点像 typeScript ，不难看懂，里面只定义了一个 Handlers 类，可以通过它来编辑 fiddler 菜单栏中的 Rules 选项以及 fiddler 处理请求的回调函数。

**第一步**，往菜单栏的 Rules 选项中增加一个“强制启用 CORS”的规则。在 Handlers 类的开头，找到定义规则的几行代码，其中“隐藏 304 响应条目”的代码是这样写的（下面的注释是本人添加的，原代码没有）：
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

**第二步**，往 Handlers 类的静态方法 OnBeforeResponse 中增加以下代码，目的是在把响应返回给终端之前，往响应头塞一些字段：

> 修正：下面代码的最初版本有问题，会导致 websocket 无法建立。原因在于建立 websocket 时发送的握手请求，头部带有 "Origin" 字段，命中了匹配条件，代码重写响应的状态码为 200 ，而建立 websocket 需要 101 状态码。因此把重写响应状态码的代码去掉。

```
if(m_ForceCORS &&
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
    
    // oSession.responseCode = 200; 见修正。
}
```

![在 OnBeforeResponse 添加相关代码]({{ site.url }}/assets/OnBeforeResponse.png)*在 OnBeforeResponse 添加相关代码*

### 特殊情况

可以看到上面的代码中只处理了响应头没有设置相应 CORS 头字段的情况，如果响应头设置了相应 CORS 字段，只是字段值不符合预期，那该怎么办呢？

你当然可以修改上面的代码，强制覆盖原来的字段值，但这又会引发新问题：如果请求头带上 cookie 等等用于认证的信息，这个请求就叫作 "credentialed" requests ，对这类请求，响应头的 `Access-Control-Allow-Origin` 字段就不能设为 `*` ，否则浏览器会丢弃响应。详见[这里](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)。

这时候可以用 AutoResponder 拦截特定请求， mock 响应 。

## AutoResponder 

### 精准匹配请求及正则匹配请求

当需要 mock 响应时，我们可以在 fiddler 左侧的 会话列表中，把目标请求按住、拖到右侧 详情和数据统计面板 中的 AutoResponder 标签页面中，这样会自动生成一条精准匹配的 rules 和与之对应的响应，如下图：
![精准匹配]({{ site.url }}/assets/exact_rules.png)*精准匹配*

当遇到请求的参数里带有时间戳或者其他情况，我们可以使用正则匹配。 fiddler 自带一些正则匹配的例子，无一例外都以`(?inx)`开头，这是在设置正则表达式的一些规则，分别是：

```
i - 忽略大小写
n - 显式捕获
x - 忽略 pattern 里的空白符以及启用注释

```
**更详细的设置项，可以查看文末给出的参考链接**

### 正则匹配的一个坑
- 当实际请求的路径中带有 id 时，如：`http://www.test.com/product/123` 
- 假设你需要用正则 rules 匹配这个请求，并返回一个事先准备好的 json 文件（文件路径是 `C:\Users\username\Desktop\product.json`）
- 那么这个正则 rules 不能这样写： `regex:http://www.test.com/product`


    如果写成这样，fiddler 能匹配请求：`http://www.test.com/product/123`，但是 json 文件的路径会不对，路径会变成：`C:\Users\username\Desktop\product.json\123` ，因为没有这个文件，响应会是 404 ，如下图：

    ![不正确的正则匹配写法]({{ site.url }}/assets/wrong_regex.png)*不正确的正则匹配写法*
    ![文件路径不正确，返回 404]({{ site.url }}/assets/wrong_response.png)*文件路径不正确，返回 404*


- 正确的写法是：`regex:http://www.test.com/product/\d+` ，如下图：

    ![正确的正则匹配写法]({{ site.url }}/assets/right_regex.png)*正确的正则匹配写法*
    ![文件路径正确，返回内容]({{ site.url }}/assets/right_response.png)*文件路径正确，返回内容*


### 伪造响应

**修改响应头**

当把匹配到的请求拖到右边，生成规则之后，右键规则，点击 `edit response` 的选项，会弹出对话框，你可以点击 `Headers` 标签页下的 `Raw` 链接来修改响应头（如下图）。

![修改响应头，方法一]({{ site.url }}/assets/fiddler_res_header_1.png)*在 `Headers` 标签页下修改响应头*

除了此之外，你还可以点击 `Raw` 标签页，同时修改响应头和响应体（如下图）
![修改响应头，方法二]({{ site.url }}/assets/fiddler_res_header_2.png)*在 `Raw` 标签页下修改响应头和响应体*

**修改响应体**

在修改响应体时，如果改变了它的长度，一定要相应地修改响应头的 `Content-Length` 字段值（这是 http 协议的规定）。要注意两点：

- 如果字段值比实际长度要小，多出来的响应体会被截断，无论是 fiddler 、 浏览器还是你自己的程序都不会报错。

- 一个英文字母长度是 1 ，而一个中文字长度是 3 。

**gzip压缩后的响应体**

如果后台启用了 gzip 压缩响应体，响应头中可能会没有 `Content-Length` 字段（因为事先并不知道压缩完成后的长度，而且服务器可以选择以 chunks 的方式分批发送响应），更重要的是你没有办法直接修改 gzip 压缩的响应体。这时候你需要在 fiddler 的 `Inspectors` 标签页先解压（解压方法如下图），再把结果复制粘贴到 `AutoResponder -> Raw` 标签页：

![解压 gzip]({{ site.url }}/assets/fiddler_response_gzip.png)*先解压，再复制粘贴到 `AutoResponder -> Raw` 标签页*

可能是 fiddler 的 bug ，解压后得到的 `Content-Length` 不一定正确，你需要在浏览器地址栏里直接输入请求的 url ，看看响应体有没有被截断，相应地修改 `Content-Length` 的值。

## 参考
- [Using Fiddler to emancipate HttpOnly cookies for web app debugging](http://simplyaprogrammer.com/2013/10/using-fiddler-to-emancipate-httponly.html)
- [Using Fiddler to force a web service to support CORS for debugging](http://simplyaprogrammer.com/2013/12/using-fiddler-to-force-web-service-to.html)
- [Regular Expression Options](https://docs.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-options)