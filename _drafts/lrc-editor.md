---
layout: post
title: 一个在线的 lrc 歌词生成/编辑器
date: 2018-09-13 07:20:28
excerpt: 最近有空，用 React 做了这个简单的小东西
categories: tech
---

**前言**

虽然有在用 React Native 做项目，但好像没有怎么用 React 做过除了官方 Demo 之外的东西。于是心里总有种本末倒置的不安违和感。

恰好最近迷上了给网易云上传日语歌的歌词，在连着用了两次这个[在线的歌词编辑器](http://heysh.xyz/hieda-lrc-editor/)后，觉得真的不错，最开始想看看里面的代码实现，然后给它加上保存功能，但可惜项目跑不起来。

想想这小东西不难，自己做一个理想的，然后用上 React，岂不是一举两得？

**功能简介**

这个[歌词编辑器](https://judes.me/lrc_editor/)，在 UI 上借鉴了上面介绍到的那个，因为对配色没自信，所以更加简单。

- 最初页面
- 加载歌曲后页面
- 加载歌词后页面
- 播放时的页面

支持以下功能：

- 操作提示
- 上传歌曲
- 播放/暂停歌曲
- 上传带/不带时间的歌词，格式为： `[00:00.00] 歌词` 或者 `歌词`
- 导出以歌曲名为文件名的 lrc 文件
- 打时间标签
- 出错回退（回退歌曲时间，同时撤销在这段时间内所打的标签）
- 高亮当前歌词
- 点击歌词定位歌曲时间

**技术实现**

以下是技术相关的话题。

难点不在 React 或者 mobx，而是在 babel 语法插件上：

- 用上了 babel@7.0 ，一堆插件改名了，插件配置也变了

播放声音，加载文件

material-ui/便利性/className

实时更新进度条/更新当前播放对应歌词 component life circle/requestAnimationFrame

[github 地址](https://github.com/yiyizym/lrc_editor)