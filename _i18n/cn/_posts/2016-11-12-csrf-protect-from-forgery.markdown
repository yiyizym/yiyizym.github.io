---
layout: post
title: Rails 的 CSRF 对策
date: 2016-11-12 22:33:28
excerpt: protect_from_forgery 方法
categories: tech
tags:
- rails
- frontend
- CSRF
---

最近的工作是把原有 PC 端的一整套面向客户的询价下单流程移植到微信公众号上。

原有的流程十分复杂，移植时想着后台代码能不改就不改，前端代码能重用的就重用。

其中有一步是前端提交一个表单，后台根据处理结果，分别重定向到成功和失败页面。

在 AJAX 流行之前，这是标准的做法（简单且重定向有效防止重复提交表单）。

如今要用 AJAX 模拟表单提交很容易，但接下来要重定向页面就有点困难了。简单的做法就是创建一个表单元素，然后塞一些 input 元素进去，再调用表单元素的 submit 方法：

    var form = document.createElement('form');
    form.method = 'post'
    form.action = '/where/to/post'
    var input_1 = document.createElement('input');
    input_1.name = 'name_1';
    input_1.type = 'hidden';
    input_1.val = 'val_1';
    
    form.appendChild(input_1);
    document.body.appendChild(form);

    form.submit();

(想来想去，与其写这么多 javascript ，还不如直接在 html 里放一个隐藏的表单元素。自己纯粹就是闲的)

单看上面这段代码应该没问题，但实际上有很大的安全隐患，在 Rails 中会提交失败。

这个安全隐患就是提交到这个路径 '/where/to/post' 的表单很容易被伪造，后台没办法区分伪造的表单和正常的表单。这就是 cross site request forgery, [CSRF](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_%28CSRF%29) 。

事情得从头说起。

后台为识别用户的操作，可以在每个操作前都要求用户输入用户名和密码，这样做太麻烦了，为方便用户，后台和浏览器共同发展出一套只需输入一次用户名密码就能在一段时间内记住用户身份的 session 机制。这套机制依赖于保存在浏览器里的 cookie 。

因此如果 cookie 漏泄了，被用来伪造用户身份的话，后台没有办法区分哪些是假冒操作，哪些正常操作。

CSRF 正是利用了这个弱点。

Rails 为防止 CSRF ，默认会检查除 GET 、 HEAD 之外的其他请求当中的请求头或请求正文，看里面有没有一个 token 字段，如果没有或者跟 session 中保存的值不一致，就判定为非法请求。

Rails 的这一套机制覆盖了多种发出请求的方式：

**在前端**

- jQuery

  如果使用 jQuery 的 ajax 方法，那么需要引入 jquery-ujs.js 。这个文件调用 `jQuery.ajaxPrefilter` 方法，为所有非跨域的请求（跨域的请求，后台通过 CORS ，检查 Origin 字段避免非法请求来源），在其请求头中加入一个 X-CSRF-Token 字段。 

  X-CSRF-Token 的值来自页面中的一个 meta 标签，这个标签在 layout 中通过设置：`<%= csrf_meta_tags %>` 生成。

- 表单提交

  如果引入了 jQuery 和 jquery-ujs.js ，所有的 form 元素会在页面初始化时被塞进一个隐藏的 token 字段，它的值同样来自 meta 标签。


- form_tag

  如果没有引入 jquery-ujs.js 或不能用 javascript ，也可以使用 `form_tag`, `form_for` helper 方法，它们也会根据上述情况加入 token 字段。

**在后台**

ActionPack 提供一个 **protect_from_forgery** 方法，用脚手架生成的 Rails 应用，会在 ApplicationController 调用这个方法：

    #Prevent CSRF attacks by raising an exception.
    protect_from_forgery with: :exception

它做两件事情：

- 在处理请求前，检验请求是不是 GET 或 HEAD 请求，是不是关闭了 protect_from_forgery ，请求头中的 X-CSRF-Token 字段是否正确， 请求正文中的 authenticity_token 字段是否正确，只要满足以上四个条件的一个，校验就算通过，可以处理请求；一个都不满足的话，就抛出异常。

- 在处理完请求，返回数据前，如果是 GET 请求并且不是 xhr 请求，抛出异常，不返回数据。这样做是为了防止有人使用 script 标签加载内容，并盗窃其中敏感的信息（因为 script 加载完成后会执行）。


**总结**

Rails 应对 CSRF 的措施覆盖了大多数使用场景，帮助程序员在不知不觉间写出安全的代码，但这种贴心的保护往往使得程序员忘记各种危险，一旦脱离 Rails 代码就写得很脆弱。