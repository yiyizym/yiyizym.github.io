---
layout: post
title: background-color 和 background-image 的定位差异细节
date: 2017-09-16 03:33:14
description: 这只是一篇读过 w3c 规范后，写就的文章
categories: frontend
---

### 序

在读[这篇文章](https://github.com/chokcoco/iCSS/issues/1)时，发现这样一句：

> background-color 是从元素的边框左上角起到右下角止，而 background-image 却不一样，他是从 padding 边缘的左上角起而到 border 的右下角边缘止

为什么会不一样呢？

### 效果
先来看看如上所述，实际效果是怎样的，代码在[这里](https://codepen.io/yiyizym/pen/XebvPm)：

![background-color 与 background-image 起始位置]({{ site.url }}/assets/background_color_image.png)*background-color 与 background-image 起始位置*

如果你平时没有觉察到 background-color 与 background-image 的定位差异，大概是因为 background-color 多出来的部分被 border 遮住了。

### W3C 规范
用 W3C 规范来解释这种定位差异最有说服力。先找到相关的[规范](https://drafts.csswg.org/css-backgrounds-3/#backgrounds)。

跟 backgrounds 相关的属性大体可分为两类。

一类是跟 background color 和 background image 都有关系的：
- background-clip

另一类是只跟 background image 有关系的：
- background-origin
- background-position
- background-repeat
- background-size
- background-attachment
- ...

在定位差异问题上，真正重要的属性有三个：

- background-clip ，它定义的是 `background painting area` ，即背景颜色、背景图绘制的区域，默认值是 `border-box`（把边框也包含在内的区域）。

- background-origin ，（当元素渲染成单个盒子时）它定义的是 `background positioning area` ，即定位参照区域，虽然没有明说，但这个属性**只影响背景图**，跟背景颜色没有关系，默认值是 `padding-box` （把边框排除在外的区域）。

- background-position ，它定义的是背景图在 `background positioning area` 的起始位置，默认值是 `0% 0%` 。

### 总结

在上述三个属性均使用默认值的情况下，背景颜色只受 background-clip 属性影响，于是背景颜色从 border 开始绘制，而背景图受 background-origin 以及 background-position 的影响，从 padding 开始绘制。这就是两者定位有差异的原因。

### 参考
- [谈谈一些有趣的CSS题目](https://github.com/chokcoco/iCSS/issues/1)
- [CSS Backgrounds and Borders Module Level 3](https://drafts.csswg.org/css-backgrounds-3/#backgrounds)