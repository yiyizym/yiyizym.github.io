---
layout: post
title: 一个在线 lrc 歌词生成/编辑器
date: 2018-09-13 07:20:28
excerpt: 最近有空，用 React 做了这个简单的小东西
lang: zh_CN
categories: tech
---

**前言**

虽然有在用 React Native 做项目，但好像没有怎么用 React 做过除了官方 Demo 之外的东西，心里总有种本末倒置的不安违和感。

恰好最近迷上了给网易云音乐上传日语歌的歌词，在连着用了两次这个[在线的歌词编辑器](http://heysh.xyz/hieda-lrc-editor/)后，觉得真的不错，最开始想看看里面的代码实现，然后给它加上保存功能，但可惜项目跑不起来。

这小东西应该不难，用上 React，自己做一个合乎心意的，岂不是一举两得？

于是花了点时间做出这个小东西。

**功能简介**

这个[歌词编辑器](https://judes.me/lrc_editor/)，在 UI 上借鉴了上面介绍到的那个，因为对配色没自信，所以更加简单。

页面截图如下：

![最初页面]({{ site.url }}/assets/lrc_editor_1.jpg)*最初页面*
![加载歌曲后页面]({{ site.url }}/assets/lrc_editor_2.jpg)*加载歌曲后页面*
![加载歌词后页面]({{ site.url }}/assets/lrc_editor_3.jpg)*加载歌词后页面*
![播放时的页面]({{ site.url }}/assets/lrc_editor_4.jpg)*播放时的页面*

它支持以下功能：

- 操作提示
- 上传歌曲
- 播放/暂停歌曲
- 上传带/不带时间的歌词，格式为： `[00:00.00] 歌词` 或者 `歌词`
- 导出以歌曲名为文件名的 lrc 文件
- 打时间标签
- 出错回退（回退歌曲时间，同时撤销在这段时间内所打的标签）
- 在歌词面板直接编辑歌词
- 高亮当前歌词
- 点击歌词定位歌曲时间

**技术实现**

以下是技术相关的话题，有兴趣可以看看。源码[在这里](https://github.com/yiyizym/lrc_editor)。

**框架**

框架方面的难点不在 React 或者 mobx，而是在 babel 语法插件上。因为用上了 7.0 的版本 babel，很多插件改了名字，而且有些特性开关变成了默认关闭：

- presets 中， `env`  变成了 `@babel/preset-env`。
- 要在 class 前面使用 mobx 的 `@observer` decorator ，就得安装 babel 插件 `@babel/plugin-proposal-decorators` ，并且配置 `legacy: true`。
- 要在 class 内使用 propeties，得安装 babel 插件 `@babel/plugin-proposal-class-properties` ，这个插件要写在前面插件的后面，并且配置 `loose: true` 。
- 如果用到 generator / async function ，得安装 `@babel/plugin-transform-runtime` ，并配置 `regenerator: true`

虽然 babel 能让开发者在用上最新的语言标准的同时，选择性地兼容浏览器，但得配置一堆才能跑起来，真是不友好。

**声音**

播放声音，使用的是 [howler](https://github.com/goldfire/howler.js)。文档没有说明如何加载一个文件，但 src 配置项支持 url 和 base64 data URI ，可以把用 [FileReader](https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL) 把加载后的文件转换成一个 base64 data URI，以下是部分实现代码：
```jsx
<input
    accept="audio/*"
    onChange={(e) => handleUpload(e.target.files[0])}
    type="file"
/>
```
```javascript
const handleUpload = function(file){
    return new Promise((resolve) => {
        let reader = new FileReader();
        reader.addEventListener('load', () => {
            let song = new Howl({
                src: reader.result,
                format: file.name.split('.').pop().toLowerCase()
            });
            resolve(song);
        })
        reader.readAsDataURL(file);
    })
}
```

**UI**

UI 用的是 [material-ui](https://material-ui.com/)，除了官网要梯子访问之外，一切还好。主题内置的颜色 `'@material-ui/core/colors` 和一些常量很好用，比如：`theme.spacing.unit`、`theme.palette.grey`，详细介绍可看[这里](https://material-ui.com/customization/default-theme/)。

用到 icons 的话，要安装独立的包：`@material-ui/icons`。

**实时更新**

随着歌曲播放，页面要实时更新进度条，以及高亮当前正在播放的歌词。以进度条更新为例，目前的实现方式是把进度条封装成一个 react 组件。在组件的生命周期钩子函数内用 `requestAnimationFrame` 不断更新自身的状态，在此之前，判断歌曲是否在播放状态减少更新操作。

**react hooks**

在简单的组件里面，使用了 react hooks 。

这个小工具已经开源，github 地址[在这里](https://github.com/yiyizym/lrc_editor)。