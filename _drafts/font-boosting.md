---
layout: post
title: font boosting
description: 在手机端字体被无故放大？原来是 font boosting 惹的祸
categories: frontend
---

前几天踩到一个坑，弹窗里的文字稍微多了一点，字体就会变大：

![文字少的表现]({{ site.url }}/assets/font_boosting_1.png)*文字少的表现*
![文字多的表现]({{ site.url }}/assets/font_boosting_3.png)*文字多的表现*

可以看到第二张图中的文字只比第一段的多一个 "abcd" ，但字体明显不一样大。查看具体的 style 值，发现就算是应用了同样的 `0.6222rem` ，算出来的值都不一样：

![文字少的 fontSize]({{ site.url }}/assets/font_boosting_2.png)*文字少的 fontSize*
![文字多的 fontSize]({{ site.url }}/assets/font_boosting_4.png)*文字多的 fontSize*

这么诡异的问题，应该不止我一个遇到！很快我就从网上搜到事情的真相。如果你英文较好，有耐心，又有梯子的话，可以直接看原文:[Chromium’s Text Autosizer](https://docs.google.com/document/d/1PPcEwAhXJJ1TQShor29KWB17KJJq7UJOM34oHwYP3Zg/edit#)

原来这个自动放大文字的特性名字叫做 `font bosting` 或者 `font inflation`，只在移动端的浏览器上出现，旨在提升那些按 PC 端大小展示的页面的文字的可读性。

这个特性不会应用在下面的元素中：

- 显式声明高度的区块（因为在这时增大字体有可能会超出区块）
- 表单的控制元素（form controls: text fields, buttons, checkboxes, range controls, or color pickers, etc.）
- 排成多排（列）的超链接（navigation headers）
- 带上 `white-space: nowrap` 样式的区块
- 只包含少量文字的簇（clusters, 可以理解为结构层次相似的几个区块。所有元素都会被划分到特定的簇当中，每个簇都有特定的字体放大比率）