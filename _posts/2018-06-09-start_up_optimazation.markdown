---
layout: post
title: 一次页面启动优化实践
date: 2018-06-09 04:20:28
description: 纸上得来终觉浅，绝知此事要躬行
categories: frontend
---

**前言**

看过不少优化 web 页面加载相关的知识和分享，但没有多少机会实践一番。

有时候会觉得业务简单不用优化，有时候会抱怨进度紧张、忙于搬砖没空优化，有时候会认为低端的硬件慢正常、办公网络环境差加载慢也正常。

有时候上面的理由是真理，有时候却是借口。

幸好我没有习惯性地把它们统统当作借口。

有一天测试同事向另一个开发同事提了个 BUG 反映某个活动首页加载有 3.X 秒的空白。开发同事发现在他的手机上没法复现，并且指出要是测试时手机不连接 fiddler 代理请求，直连的话会快很多，只要 1.X 秒。

测试同事面临的问题真实存在，而开发同事说的也是事实。我恰恰解决完手头上的 BUG ，有点时间，于是 BUG 转到我头上。

**正文**

问题是这样：从某个原生链接跳转打开活动首页有 3.X 秒白屏。

猜想造成问题的原因有：原生跳转到 web 慢；网速慢；渲染要用到的关键资源体积大。

但这个问题在硬件较好手机上不能复现。上面列举的都不像是真正原因。

要用 chrome://inspect 调试看看。

回想 web 页面加载的技术指标有好几个：first paint (FT) / first contentful paint (FCT) / time to interactive (TTI) ，详见[这里](https://developers.google.com/web/fundamentals/performance/user-centric-performance-metrics)。既然是白屏，不管真正原因是什么，应该关注 FT 和 FCT 。

**第一回合，以为轻松解决问题**

最初没有拿到测试同事那台复现问题的手机，用的是自己的测试手机。

我司浏览器用的内核比较老，大约是基于 chrome 40+ ，调试面板看起来跟最新版本 chrome 的不一样，功能也有点落后。

首先在 Timeline 面板，点击 记录 按钮的同时，在手机上按刷新页面的按钮，待页面完全显示出来后停止记录。

研究资源加载的时间记录，很快发现问题：活动首页用到两个 JS 文件，而它们竟然是串行先后加载的，加载时间的 99+% 都耗在 [TTFB](https://en.wikipedia.org/wiki/Time_to_first_byte) 上面。

前端改善单个 TTFB 的办法不多，但可以合并多个请求，或者让请求并发，减少 TTFB 的数量。

因为整个技术栈是我选定的，稍微一想就知道这两个 JS 文件都是些什么东西，以及为什么会先后串行加载。

第一个 JS 文件是 vue + vuex + vue-router + 其他插件 + main.js + app.vue 的内容，而第二个文件是首页命中的路由对应的页面文件 home.vue 。

之所以这样，是因为用了 vue-router 的 [lazy loading routes](https://router.vuejs.org/guide/advanced/lazy-loading.html#grouping-components-in-the-same-chunk)，比如在 router.js 里这样写：

```javascript
// router.js
// ...
import Foo from './Foo.vue'
const router = new VueRouter({
  routes: [
    { path: '/foo', component: Foo }, // 在打包好的文件里直接包含这个模块的内容
    { 
      path: '/bar', 
      component: () => import('./Bar.vue') // 在命中路由后才用 Ajax 加载这个模块的内容，需要相应的 webpack/babel 支持
    }
  ]
})
```

我错误地把首页也用上了 lazy loading routes ，令首页加载多了一个 TTFB （这个例子里是 600ms 以上）的时间。

以为这样就轻松解决问题，没高兴多久，测试同事又重新打开了这个 BUG ，在她的手机上问题没改善。

**第二回合，耐心加点运气**

有点得意忘形了：刚刚只是解决了一个普适问题，并没有找到在测试同事的手机上加载慢的原因。

于是拿来出问题的手机，再跑一遍 Timeline 记录，发现 javascript 的 evaluate 时间是惊人的 5+s （显然不止之前所说的 3s ），而这在我的手机上只有 800+ms 。

虽然找到问题的原因，但这种情况却有点无能为力了。

javascript 的 evaluate 时间分为 parse / compile / execution 三个阶段。从不同手机有不同表现来看，问题大概率出现在 parse 和 compile 上面，拿 iPhone 8 (A11) 跟 Moto G4 (Snapdragon 617) 来说，前者在[这种情况](https://medium.com/dev-channel/the-cost-of-javascript-84009f51e99e)下会快 9s 左右。

这就是低端机跟高端机的实力差距。

当时很想就此放弃，但一想到我司就靠这低端机活着，活动面向人群大部分用的是低端机，就精神紧张起来：这个问题不解决，让几百万用户在白屏前面都等上 5+s ，自己可以引咎辞职了。

既然是 javascript 耗时严重，那就看看都耗在哪里吧。打开 Profiles 面板，记录 javascript 占用 CPU 的时间：

![优化前 CPU Profiles]({{ site.url }}/assets/start_up_optimization_before.png)*优化前 CPU Profiles*

在 total 一列选择从多到少排列占用时间最多的 function ，可以看到占用时长最多的足足有 5258.9 ms 。在把这个 function 展开 30+ 层之后，发现占用时长最多的原因在于 vuex Store 遍历 DOM 、收集依赖以实现响应式编程。

莫非要在 deadline 前两天把核心框架给换了？

一个个地点开 defineReactive / _withCommit / replaceState / Store 这些方法对应源码所在位置，越发相信这就是框架的问题，但在网上搜索不到有人吐槽 vuex 慢啊，这次真的接近绝望了。

给我带来曙光的是最后一次点击：位于 Store 方法上面两层的 \_\_webpack_require\_\_ 方法。这个到处都有的方法只是加载某个模块，在这个上下文它加载的应该是 vuex 。然而它加载的竟然是一个用于刷新页面后保留状态的 vuex 插件： vuex-persistedstate 。正是加载了这个插件，然后这个插件运行了一些方法占用了 4538 ms ， 44.64% 的 CPU 时间。

![问题所在]({{ site.url }}/assets/start_up_optimization_problem.png)*问题所在*

把这个插件去掉，再跑一遍，证实就是它的问题。

好了，现在有三条路可以选：用另一个同类插件替换；自己写一个实现简单的类似功能的插件；把这个功能砍掉，用户刷新页面的后果自负。

先走第一条路，很快找到另一个插件：[vuex-persist](https://github.com/championswimmer/vuex-persist) ，替换后再跑一遍，结果：

![优化后 CPU Profiles]({{ site.url }}/assets/start_up_optimization_after.png)*优化后 CPU Profiles*

最耗时的 function 仅有 1136.2 ms ，而且占去了 15.7% 的 CPU 时间。我当时高兴得跳起来，工作保住了，良心不会再痛了！

**后记**

没想到最后解决问题的方法这么没有技术含量，这让我想起 画一条线一万美元 的故事，知道为什么要换插件比换插件本身有价值得多。

**参考**

[JavaScript Start-up Optimization](https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/javascript-startup-optimization/#parsecompile)