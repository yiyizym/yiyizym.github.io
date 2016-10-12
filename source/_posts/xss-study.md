title: xss 一点总结
description: 整理了一下学习 xss 的头绪，只涉及 javascript/html/url ，没研究 flash
categories: frontend
tags: xss
date: 2015-10-02 14:45:41
---


# xss 一点总结

我不是很理解 xss 这个词： Cross-site scripting ，它怎么就跟跨站勾搭上了呢？


## xss 输入/输出

网页是xss的舞台，要达成 xss 攻击，首先必须找到页面中可以注入代码的地方（注入点），而且网页必须要有执行注入代码的地方（输出点）。

发现 xss 漏洞的一种方法就是在所有用户输入的地方输入一些特殊字符（字母和数字的随机组合，方便与正常文本区分开），看看页面有没有展示这些特殊字符，如果没有那肯定没戏了，如果有还可以继续测试。

## xss 类型

先看看 xss 类型。根据 要不要与后台交互 和 会不会保存到数据库 大致可以分为不需要与后台交互的 DOM XSS ，需要与后台交互但不会被保存到数据库的 反射型XSS ，以及会把注入代码保存到数据库的 存储型 XSS 。因为存储型XSS可以一处存储，多处显示，所以危害比较大。

## 输出场景/编码方式/解码顺序

之前说页面展现特殊字符可以继续测试。特殊字符可能出现的地方，有：

- HTML 标签之间 `<div>[输出]</div>`
- HTML 属性值 `<input value="[输出]">`
- javascript 代码里面 `<script type="text/javascript">val = [输出]</script>`
- CSS 代码里面 `<style type="text/css"> body {height: [输出]px;} </style>`

为什么要区分不同的地方呢？这与不同语境下不同的编码以及浏览器的解码次序有关。

先来说说编码：

- HTML 支持实体编码（如 `&lt;` 就是 '<'），十进制（&#60）、十六进制（&#x3c）ASCII编码，以及unicode字符编码（&#x3c）。
- javascript 支持 八进制（\74）、十六进制（\x3c）ASCII编码，以及 unicode字符编码（\u003c）。
- CSS 支持十六进制ASCII编码（#fff 可以写成#\66\66\66） 以及 utf-8 编码（\0066）。
- URL 支持十六进制ASCII编码 以及 utf-8 编码 和 GB2312 编码 或者还有更多。

在不同的语境下用其支持的编码有时候可以绕过后台的字符过滤。能不能绕过，得测试很多种情况，所以要借助工具。

浏览器获取源码之后，一边解析一边执行源码：

- 一开始解析 HTML 代码，如果遇到 script 标签，停止解析 HTML ，开始解析 script 内容（如果要加载远程代码，一般情况下——没有加 defer ；浏览器不作优化——在加载完成后解析），解析完毕后，继续解析 HTML 。解析 HTML 时，同时也在解析 CSS 。因为 javascript 有可能会读取样式，在解析 CSS 时怎样处理 javascript ，各浏览器有不同的实现，详见[how browsers work](http://taligarsiel.com/Projects/howbrowserswork1.htm#The_order_of_processing_scripts_and_style_sheets)。

- 解析 HTML 时，如果遇到标签属性中的事件句柄，如 onclick ，会先当作 HTML 代码解析，在事件被触发时，再调用脚本解析器解析。

    比如下面这行代码：

        <button onclick="location.href = 'http://www.yoursite.com?userName=<%= userName %>';">redirect</button>

    用户输入的 userName 到达浏览器之后，首先会被当作 HTML 解析，当 click 事件触发之后，又会被当作 script 解析，因为是 url 的一部分，最后还会被当作 url 来解析。

    **为了不出乱子（即把用户的输入当作当前环境下的代码执行），后台对 userName 的编码将是浏览器解码的逆过程，先是 url 编码，再是 script 编码，最后是 HTML 编码。**

- 解析 script 时，也有可能调用 HTML 解析器解析代码。这时先进行 script 解析，再进行 HTML 解析。

    比如下面的代码：

        <scirpt>
          var div = document.createElement('div');
          div.innerHTML = "\x3cimg src=1 onerror=alert(1)\x3e";
          // 与 div.innerHTML = "<img src=1 onerror=alert(1)>" 效果一样
          // 试试 div.innerHTML = "&#x3cimg src=1 onerror=alert(1)&#x3e"

          // 试试 div.innerHTML = "<script alert(1);" 为什么不执行？

          //document.body.appendChild(div); 不用 append 到页面中

        </script>

    会弹出提示窗。不是所有 DOM 元素调用其 innerHTML 方法都会像上面一样弹窗，比如 textarea 就不会。

## 未尽事宜

XSS 漏洞是网络攻击的第一步，黑客可以利用漏洞加载远程脚本、盗取用户信息（cookie），再配合 CSRF 实施进一步攻击。

## 参考文献

- [给开发者的终极XSS防护备忘录](http://blog.knownsec.com/2014/07/%E7%BB%99%E5%BC%80%E5%8F%91%E8%80%85%E7%9A%84%E7%BB%88%E6%9E%81xss%E9%98%B2%E6%8A%A4%E5%A4%87%E5%BF%98%E5%BD%95-v1-0/)

- [XSS编码剖析](http://www.freebuf.com/articles/web/43285.html)

- [Web前端黑客技术揭秘](http://www.amazon.cn/%E5%9B%BE%E4%B9%A6/dp/B00B14IGUK)

- [XSS零碎指南](http://www.cnblogs.com/hustskyking/p/xss-snippets.html)