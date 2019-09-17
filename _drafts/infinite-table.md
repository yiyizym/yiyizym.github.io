---
layout: post
title: 基于 ant design table 实现的虚拟滚动列表
date: 2019-09-17 10:20:28
excerpt: 只是一种思路，不支持无限滚动且有很多未知 bug
categories: 
- frontend
---

不少用过 ant design table 的朋友，可能都会遇到过当一页加载的数量超过 150 条时，table 组件渲染慢且后续操作（如点击勾选框）反应慢的情况。

ant design table 组件功能强大，而性能往往跟功能此消彼长；功能强大通常意义着复杂度高，相当难以改动。

社区早就有人提出优先长列表渲染性能的 [issue](https://github.com/ant-design/ant-design/issues/3789) ，针对 table 的性能优化，官方也计划于今年第四季度推出的 ant design 4.0 版本支持 [虚拟滚动](https://github.com/ant-design/ant-design/issues/16911)。但是我有点担心进度能不能赶上，毕竟还有两个星期就到第四季度了，实现虚拟滚动的 table 预览版都还没有出来。

另一方面，因为在 table 里面加过不少功能，踩过不少坑，看过几个虚拟滚动的实现，也看过 rc-table 的源码，我觉得不从底层重新实现 table （不再使用 table/thead/tbody 等等原生元素），很难解决虚拟滚动将要面临的问题。

闲话到此为止。

虚拟滚动的原理

具体实现虚拟滚动的方式

结合 ant design table 考虑实现方式

基于现有组件接口的突破点： components

再优化： pureComponent ，优化的尽头

暂时不明所以的坑，以及绕过的办法

源码和提醒