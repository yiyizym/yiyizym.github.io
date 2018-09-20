---
layout: post_with_octocat
title: webpack 踩坑记
description: 因为奇葩的需求，踩了 webpack 里面的一些坑
categories: frontend
tags: webpack
date: 2015-11-21 11:00:58
---


我公司用的开发框架是 ruby on rails ，话说这套框架真的很不错，只要遵守约定，很多必要但是琐碎的事情对你来说都是透明的。比如说静态资源的压缩、打包、打指纹这三大必要步骤，rails 对开发者就很友好：在 development 环境下，更改前端任何一个静态文件，保存之后，文件都会被重新打指纹；开发完成之后，部署到 production 时，自动帮你压缩、打包、打指纹，再也不用管这些破事儿了。

你会问，既然这么好，为什么要踩 webpack 的坑呢？rails 能满足绝大部分情况下的需求，剩下的一小部分是自己折腾出来的：比如说公司要做官网展示页面，是静态页面，有人希望静态页面只需经 nginx 就直接返回，不需要再转发到 rails 。我也认同这种做法，但这样就用不上 rails 的种种好处了。

静态资源的压缩、打包、打指纹都没有了。我得找一种替代品。

以前用过 gulp ，它对文件处理比较好，但依赖加载要另外处理；图片打指纹这种事只能自己动手，不能一视同仁地对待各种静态资源。 webpack 恰恰没有这些不足。

但 webpack 也不是百分百满足我的奇葩需求，比如说我要用它来做的是多个静态页面而不是单页应用；要兼容 IE8 ；要全局使用 jQuery ；要处理原有页面，确保它能找到打上指纹后的图片。

这些需求对当时——完全没用过 webpack 的我来说——都是一个个的坑。

好，跟着我来踩坑吧。安装、跑个最简单的例子什么的就不说了。虽然我觉得 webpack 官网不咋的，但还是推荐 官网的[这篇](https://webpack.github.io/docs/installation.html)和[这篇](http://webpack.github.io/docs/tutorials/getting-started/)，跟着动手，一切 OK ，之后的坑就要靠多看看 [configuration](https://webpack.github.io/docs/configuration.html) 了。 

**以下步骤都有对应源码，已上传到 github ，还有对应的 tag ，方便一步步跟踪。**

## 先挑软柿子 jQuery 来捏。

使用 resolve 配置项加载 jQuery ，要注意两点：一，jQuery 的版本要够新，得支持 `module.exports` 导出 jQuery ，这是 Node 的 commonjs 模块加载形式（其实不支持也没关系，只是使用require语法会把 $/jQuery 挂到 window 变量下，被 require 赋值的变量为 `undefined`而已）；二，也不能太新，以至于不支持 IE8 。（相关代码见 tag v1.0）

还可以在 resolve 基础上使用插件 ProvidePlugin 预先加载 jQuery ，这样就不用在每个使用 jQuery 的文件前面显式 require 加载了。（见 tag v1.1）

## 再兼容 IE 8

在 IE8 下使用 webpack 加载依赖可能会遇到某些函数 undefined 报错的情况，你需要在 webpack 打包好的文件执行之前加载 es5 polyfill 。另外要在 IE8 下使用 CSS3 的媒体查询特性，就必须使用 respond.js ，如果你没留意 respond.js 的工作原理，就不会知道它要求样式文件要用 link 标签加载，使用 style 标签的行内样式会被忽略。webpack 恰恰会默认把样式塞到 style 标签中（把资源都一次性加载过来，作者显然已经抛弃了 IE8 ）。

首先解决 polyfill 问题，在每个 js 文件最前面用 script-loader 加载 polyfill 。这个办法有点麻烦，而且不论是现代浏览器还是 IE8 都会加载 polyfill ，所以最简单的做法就是把 polyfill 用 script 标签加到 index.html 文件里面。

同理， respond.js 和 html5shim 也可以用标签加载。

接下来就是要把 css 由行内形式变为嵌入形式，你需要用到 extract-text-plugin ，具体用法参见[这篇文章](http://webpack.github.io/docs/stylesheets.html#separate-css-bundle)。

首先安装这个插件，然后修改 webpack.config.js 文件，最后修改 index.html 文件，在 head 标签里加上 `<link rel="stylesheet" type="text/css" href="bundle.css">` ，注意要放在 respond.js 之前。（见 tag v1.2）

## 接着给图片打指纹

webpack 会自动对样式文件中引用的图片打指纹，所以使用 img 的 content 属性可以做到加载图片，其他元素可以使用 backgound 属性加载。问题是 IE8 不支持 img 的 content 属性。

webpack 的[样板做法](https://github.com/petehunt/webpack-howto#5-stylesheets-and-images)是先 require 图片资源，取得带有指纹的图片地址（或者直接是base64编码的图片），然后用 javascript 手动设置 img 标签的 src 属性。

在找不到合适插件的情况下，只能这样做了：

1. 把 html 文件里 img 的 src 属性改为 data-src ，否则浏览器会在 javascript 执行之前加载图片，而图片不存在，会报错；
2. 用 javascript 获取 data-src 属性值，然后加载对应的图片，再设置 src 属性。

在实践过程中，发现使用 webpack 编译时工作量十分大，最后报错提示要加载的图片地址需要“计算”得出。因为这个地址需要在执行 javascript 时取出来，所以实际上 webpack 计算不到，它遍历了当前目录所有文件，包括 node_modules 目录下的文件。

不得已，我重新安排了文件的目录，限定了图片查找范围。最后出来的效果还不错。（见 tag v1.3）


## 最后，还记得要生成多个静态页面吗？

这可以用插件 [html-webpack-plugin](https://github.com/ampedandwired/html-webpack-plugin) 解决，真是太好了。具体用法很简单，看插件的 github page 或者（见 tag v1.4）


## 本文对应 [github 仓库](https://github.com/yiyizym/try_webpack/tree/master)

## 参考文章

- [Managing Jquery plugin dependency in webpack](http://stackoverflow.com/questions/28969861/managing-jquery-plugin-dependency-in-webpack)
- [content attribute of img elements](http://stackoverflow.com/questions/11173991/content-attribute-of-img-elements)