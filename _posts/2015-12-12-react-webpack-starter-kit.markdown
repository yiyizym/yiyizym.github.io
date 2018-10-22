---
layout: post_with_octocat
title: react_webpack_starter_kit
description: 这是一个纯前端 react webpack 启动项目，以此为基础可以快速入坑~
categories: frontend
tags: 
- react
- webpack
date: 2015-12-12 15:40:40
---


## Talk is cheap, show you the code [here](https://github.com/yiyizym/react_starter_kit)

## 一些说明

- **react 以及 react-bootstrap 都没有发布稳定版，将来 API 可能会大变，用于学习时以最新版为宜**

- npm 用起来有时会有点慢，建议使用[淘宝镜像](http://npm.taobao.org/)

- 项目的文件组织风格及 webpack config ~~抄袭~~借鉴 [material-ui](https://github.com/callemall/material-ui)

- 对所有的CSS样式文件默认开启了 [CSS Modules](https://github.com/css-modules/css-modules)

- 出于方便引入全局 bootstrap 样式，且方便覆盖样式的考虑，对所有SCSS样式文件默认不开启 CSS Modules ，我强烈建议所有人除非必要，在写 scss 样式文件时，一律将代码包在 :local 里面

- 因为不想在服务器端处理路由，没有开启 history 的 [createBrowserHistory](https://github.com/rackt/react-router/blob/master/docs/guides/basics/Histories.md) ，采用了 HashHistory

## Many thanks to

- 以上链接

- [react-bootstrap](https://react-bootstrap.github.io/)