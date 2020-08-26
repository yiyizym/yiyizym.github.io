---
layout: post
title: 从头搭建一个使用 react+redux+react-router 实现简单功能的页面有多难
date: 2019-03-01 17:20:28
excerpt: 直到掉进坑里，我都以为不难。
categories: 
- tech
- frontend
---

**缘由**

对一个稍微接触过 React 的人来说，要在 2019 年初从头开始搭建一个使用 react+redux+react-router 实现简单功能的页面有多难？

我还以为不难，直到掉进坑里。

只记得自己一上来就采用声称拥有 highly scalable, best developer experience and best practices 的 [react boilerplate](https://github.com/react-boilerplate/react-boilerplate)，结果浪费了整整两天，一行业务代码都没写出来。

对一个接触 React 不久的人来说，这个采用了诸多模组的模板一点都不友好，因为每个模组都有自己的一套概念，整理这些概念，以及搞清楚模组之间怎样接合起来，快的话都得花上一两天。

当真正动手去写代码时，为实现一个小功能，几乎要往每个模组都加点「流程代码」，到头来「流程代码」比「业务代码」还要多。

因此如果只是想通过实现一个简单的功能页面，找 boilerplate 会得不偿失。

自己从头开始搭，最大的问题是不知道会花多少时间。

我刚尝试完，对一个接触过 React ，但对 React 生态圈中其它东西不熟的人（比如我）来说，大约要花 1 天。

以下是我的具体目标和实战记录，希望后来者有帮助。

**目标**

在 2019 年初，从零开始使用 react+redux+react-router 实现一个简单的需要登录的站点页面

具体功能：
  - 可以在登录页面登录，登录成功后跳转到主页
  - 主页需要登录才能看到，未登录时进入主页会重定向到登录页面
  - 在主页可以登出，登出成功则会重定向到登录页面
  - 进入其他页面，会展示 404 页面

**实战记录(大致操作及参考信息)**

以下给出的链接可能会过时，但核心思路是找到相应库/工具的官网，认真读一读。

从零到可以运行：

- npm init // 初始化 npm
- git init // 初始化 git
  - .gitignore // 添加文件
- Install dependencies // 添加依赖
  - react
  - react-dom
  - react-router-dom
    - 注意 react-router 与 react-router-dom 的关系
  - redux
    - 注意 redux 与 react 的关系
  - webpack
    - webpack.config.js
      - mode development
  - webpack-cli
    - 在 webpack v4 开始，`npm i webpack` 并不会同时安装 `webpack-cli`
  - babel-loader
    - [babel-loader](https://github.com/babel/babel-loader)
    - [babel-preset-react](https://babeljs.io/docs/en/babel-preset-react)
      - 在这里找到处理 jsx 的 preset
      - .babelrc
  - babel/core
  - babel/preset-env
- /src/index.js/app.js
  - source files
- /dist/index.html 
  - output directory
- package.json 
  - scripts 字段

处理 react / react-router / redux 的关系:

- react-router
  - [react-router docs](https://github.com/ReactTraining/react-router/tree/master/packages/react-router)
    - react-router 是实现路由功能的核心
    - 这里说如果是在 web 上用 react-router 应该安装 react-router-dom ，后者会安装 react-router 作为依赖
  - [react-router project page](https://github.com/ReactTraining/react-router)
    - BrowserRouter 与 HashRouter 的区别
    - 这里有提示到 Redux Integration 看看
      - [redux-integration](https://reacttraining.com/react-router/web/guides/redux-integration)
      - 有一个 blocked updates 的问题
- redux with react
  - [usage-with-react](https://redux.js.org/basics/usage-with-react)
  - [react-redux](https://react-redux.js.org/)
- redux with react-router
  - [usage-with-react-router](https://redux.js.org/advanced/usage-with-react-router)
    - config server
      - webpack-dev-server
        - [devserver](https://webpack.js.org/configuration/dev-server/#devserver)

搭一个简单的后台:

- expressjs
  - [expressjs](https://expressjs.com/)
  - 处理 post 请求: LOGIN / LOGOUT
    - [get parameters](https://scotch.io/tutorials/use-expressjs-to-get-url-and-post-parameters)
  - run multiple npm scripts 
    - [stackoverflow](https://stackoverflow.com/questions/30950032/how-can-i-run-multiple-npm-scripts-in-parallel)


发送请求与后台接口

- axios
- 异步 acitons
  - [async-actions](https://redux.js.org/advanced/async-actions)
  - redux-thunk
  - redux-logger
- 用代码实现登录重定向
  - [history](https://reacttraining.com/react-router/web/api/history)
  - history 对象存在于用 Route 对应生成的 Component 的 props 中

**项目的代码**
- [github](https://github.com/yiyizym/react_from_scratch)