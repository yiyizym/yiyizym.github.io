---
layout: post
title: CSS 样式应用优先级
date: 2015-09-13 10:51:45
excerpt: 可以用来面试（别人），总结自一篇讲浏览器工作原理的文章。
categories: frontend
tags: CSS
---

CSS 是 Cascading Style Sheet 的缩写，可以翻译成 层叠样式表。

样式可以定义在多个文件中，每个文件也有多个样式，根据 CSS2 的定义，样式的 层叠 顺序（优先级从低到高）如下：

- 浏览器声明的样式。浏览器会给某些元素添加默认样式；
- 用户声明的“普通”样式（normal declarations）。用户可以让浏览器加载自己写的样式表，很少会用到；
- 页面作者声明的“普通”样式；
- 用户声明的带 !important 的样式（important declarations）；
- 页面作者声明的带 !important 的样式。

处在同一优先级（上述五个之一）的样式，根据 CSS2 的定义，其层叠优先级大致可以用一个4位十进制数（数值越大，优先级越高）表示：

- 如果样式通过 style 属性声明，标记千位为1，否则标记千位为0；
- 计算样式选择器中 ID 选择器的数量，标记在百位，没有的话标记百位为0；（不要吐槽我超过10个怎么办）
- 计算样式选择器中 类、[伪类](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Pseudo-classes)、属性 选择器的数量，标记在十位，没有的话标记十位为0；
- 计算样式选择器中 元素、[伪元素](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Pseudo-elements) 选择器的数量，标记在个位，没有的话标记个位为0；

数值相同的样式，出现在后面的优先级高。

上面三个规则可以处理大多数情况。补充一点，有些HTML元素属性（原文中为 visual attributes），比如 bgcolor/dir/hidden 也会被转换为页面作者声明的“普通”样式，优先级比真正的页面作者声明的“普通”样式要低。

参考链接

- [原文](http://taligarsiel.com/Projects/howbrowserswork1.htm)