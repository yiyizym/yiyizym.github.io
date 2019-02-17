---
layout: post
title: anu 源码阅读 01
date: 2019-1-09 07:20:28
excerpt: anu 是一个类似 react 的框架，阅读它的源码可以学到很多
categories: tech
---

**序**

世事无常，年底「会社をクビになった」，因此有大量空闲时间，恰恰之前算有认真读过 anu 的源码，如今强逼自己整理一下，算是一个分享。

这是一系列的文章的第一篇，写到哪算哪，尽量不坑。

**说明**

如果没有听过 anu ，建议先到[官网](https://rubylouvre.github.io/anu/ch/index.html)了解一下。

本文用的的源码基于这个 commit `9d9cacf7` 。

我源码阅读的方式就是用最笨的办法：写一个能跑起来的简单的例子，然后打断点逐步调试，同时用个小本把关键函数跟调用流程记下来。

**正文**

先说说目录结构？

从 package.json 的 scripts 中的 build 命令入手，看得出使用 rollup 打包。而且会打出适用于各种场景的包：兼容 ie 的包，可在微信、快应用中使用的包等等。只看最通用的情况。

从 `scripts/build/rollup.js` 中看到，入口文件是 `packages/render/dom/index.js`，可以看到作者——通过在 .bablrc 文件中取别名——有意在命名上跟 React 一样。

首先在根目录新建一个 index.html 文件，内容[在此]()，可以借鉴同级目录下的 index3.html 文件的内容；记得在 `ReactDOM.render` 前一行添加 `console.log` 作为打断点的最开始。

说说 bable 转译 jsx ?

从大的流程来说，无论是 React 还是 anu ，最初都是先生成 vnode ，再把 vnode 渲染成 DOM 节点。

