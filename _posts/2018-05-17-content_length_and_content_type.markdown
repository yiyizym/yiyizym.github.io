---
layout: post
title: 一个由 Content-Length 与 Content-Type 引发的问题
date: 2018-05-17 01:14:37
excerpt: 很早之前我就发觉在用 fiddler 伪造请求时，不好好设置 Content-Length 是不行的。但当响应 body 里面有中文时，这就成了一道考察细心的小学数学题。
lang: zh_CN
categories: tech
---

**问题**

在之前介绍 fiddler 使用技巧的文章中，我提到伪造 json 返回响应时，要设置正确的 Content-Length 。

[规范](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html)定义了在大多数情况要设置 Content-Length ，只有少数情况例外。在浏览器实现上，如果设置了比正确数量要少的 Content-Length ，那么内容会被截断，若比正确数量要多，那么会一直处在等待加载更多内容的状态。

之前也提到过，如果伪造的 json 中只有英文和数字，选中它们后，编辑器上显示选中多少字符， Content-Length 就设为多少。如果 json 中还有中文，那么一个中文字符就要当成三个英文字母来计算。

为什么是这样？

**答案**

首先从规范中摘取 Content-Length 部分定义：

> The Content-Length entity-header field indicates the size of the entity-body, in decimal number of OCTETs...

上面的 OCTET 指的是 [<any 8-bit sequence of data>](https://www.w3.org/Protocols/rfc2616/rfc2616-sec2.html#sec2.2)， 任意连续的八比特数据，可以近似理解为一个字节。

也就是说 Content-Length 指的是响应 body 的字节长度，而不是字符串长度。

同一个字符，在不同的编码规则下，有可能会有不同的字节长度。比如下面展示的大写字母 "A" 的情况：

| 字符 | ASCII | UTF-16 | UTF-8 |
|:--- | :--- | :--- | :--- |
| A | 01000001 | 00000000 01000001 | 01000001 |

正因如此，服务器应该在设置 Content-Length 的同时，也设置字符编码 charset 。根据[这里](https://www.w3.org/International/articles/http-charset/index)所说，如果不设置，在 HTTP 1.1 中 charset 默认为 ISO-8859-1 。

在响应头的 Content-Type 字段，可以设置 charset ，通用的做法是设置为 UTF-8 。UTF-8 兼容 ASCII 字符集，同时采用变长编码方式，节省网络流量。

在 UTF-8 变长编码方式下，英文和数字用一字节编码，绝大部分汉字用三字节编码。这就是为什么一个中文字符要当成三个英文字母。

**工具**

如果你很不幸像我一样要经常计算带有中文的 Content-Length ，可以尝试用 javascript 代码帮你计算字符串的字节长度：

```javascript
//https://stackoverflow.com/questions/5515869/string-length-in-bytes-in-javascript
function byteLength(str) {
  // returns the byte length of an UTF-8 string
  var s = str.length;
  for (var i=str.length-1; i>=0; i--) {
    var code = str.charCodeAt(i);
    if (code > 0x7f && code <= 0x7ff) s++;
    else if (code > 0x7ff && code <= 0xffff) s+=2;
    if (code >= 0xDC00 && code <= 0xDFFF) i--; //trail surrogate
  }
  return s;
}
```
javascript 用的是 Unicode 字符集，上面的代码用 charCodeAt 获取字符的 Unicode 编码值，然后根据值所在的区间和 Unicode 与 UTF-8 的对应关系，推算字节数。

**更多参考**

- [Unicode、UTF、ASCII —— 字符集编码那些事儿](https://my.oschina.net/micromemory/blog/655243)
- [通过javascript进行UTF-8编码](https://segmentfault.com/a/1190000005794963)
- [UTF-8-Wikipedia](https://en.wikipedia.org/wiki/UTF-8#Description)
