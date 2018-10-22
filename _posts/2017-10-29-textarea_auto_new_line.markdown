---
layout: post_with_octocat
title: 输入框高度自适应及其它细节实现
date: 2017-10-29 03:07:38
description: 工作原因，稍微实现了一下
categories: frontend
---

## 闲话
最近偶尔被墙，不得已用了下 bing ，其搜索质量跟 google 相比差一两个档次（百度就更不用说），于是敲代码的效率严重下降。

唉，谁叫我是一个 google/stackoverflow 搬运工呢，要是哪一天完全翻不动，就不干程序员了！不过在此之前，我想着能留下点什么有用的给后人就好，所以写下这篇文章。

## 序言
因工作要实现一个高度自适应的输入框，要是能用插件的话，我会用 [autosize](https://github.com/jackmoore/autosize) 。

不过考虑了下，还是不用插件。

原因是：兼容性要求不高（自家浏览器没问题就行），代码要尽量少；单行时的行高跟多行时的行高不一样，达到一定行数后出现滚动条，要是插件实现不了这两点的话，还得改插件，这很麻烦；

## 大致思路
参考这篇[文章](https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize)，实现输入框高度自适应大致思路是：
- 用 textarea 实现输入框，在用户输入时，设置输入框的高度为 auto
- 然后取出输入框的 scrollHeight ，这个属性是指，在不出现滚动条的情况下把元素的内容(包含 padding )全部显示出来的最小高度
- 最后重新设置输入框的高度为 scrollHeight

## 实际情况及调整

- 在用户输入时，首先设置输入框的高度变为 0 ，而不是 auto 。原因是 textarea 的 rows 默认值为 2 ，如果设置高度为 auto ，则 scrollHeight 的值为： 行高 * 2 + 上下 padding 。这样的话可以看到在用户输入第一个字后，输入框变高。在不设置 rows 为 1 的情况下，可以把输入框的 height 为 0 。

- 当输入框有上下 padding 且 box-sizing 为默认值 content-box 时，可以看到用户输入第一个字后，输入框的高度还是会变高，原因是在计算 scrollHeight 时包含了 padding ，而 box-sizing 为 content-box 时的 height 属性是不包含 padding 的，这就导致重新设置后，输入框的高度增加了上下 padding 的值。不想改变 box-sizing 的值的话，可以先从 scrollHeight 中减去 padding 的值再设置 height 。

- 单行时的行高与多行时的行高不一样。可以比较 scrollHeight 跟 上下 padding + 行高 两者的值，根据结果添加或删除输入框的相应类，然后给相应的类设置行高来实现这点。

- 设置最多显示行数，达到最大行数会出现滚动条。与前面类似，比较 scrollHeight 跟 最大行数 * 行高 两者的值，如果 scrollHeight 比较大，就设置输入框的高度为 最大行数 * 行高 ，同时设置 overflowY 为 scroll ，否则用之前的规则设置高度值。

## 代码

简单的代码放在[这里](https://gist.github.com/yiyizym/6e9eb583dafe1d0a335235a3de18157f)