---
layout: post
title: 微信浏览器 location reload 失效解决办法
date: 2016-07-02 22:45:16
description: 微信自家浏览器总有莫名其妙的 bug
categories: frontend
tags: 
- 微信
- 浏览器
- reload
---

公司在微信企业号上开发了一个功能，用户通过这个功能完成一个个任务后可以获取奖励：

- 用户首先进入页面 A 查看任务列表，列表中每一个任务都有各自的状态，一共有 5 个： 从状态 1 到状态 5 ；
- 用户点击页面 A 中的某个条目进入页面 B 查看任务详情，用户需要在 B 页面先后进行 5 个操作更新任务状态，每个操作都会刷新页面 B 。

在微信开发者工具上测试一切正常。但测试 Android ——苹果上没有问题—— 真机就发现一个很严重的 BUG ：每个操作成功后页面 B 并不刷新。

刷新用的方法是简单的 `location.reload()` ，据网友反馈，失败的原因是微信浏览器缓存了 reload 请求。

一提到解决浏览器缓存问题，自然会想到给资源加上指纹。

这能解决问题，不过不管怎么说都是特殊处理，最好只针对 Android 微信浏览器使用，所以：

首先判断请求是否来自 Android 微信浏览器：

    var isAndroidWechat = function(){
      return (/android/i).test(window.navigator.userAgent) && (/micromessenger/i).test(window.navigator.userAgent)
    };

如果 isAndroidWechat 为 true ，则在 url 上加上指纹：

    var reload = function(){
      var hash = +(new Date());
      var new_search = (/wechat_hash/).test(location.search) ? 
        // 如果之前有添加过指纹，就更新它
        location.search.replace(/wechat_hash=\d+(&?)/,'wechat_hash=' + hash + '$1') :
        // 如果 search 为空
        location.search == "" ?
        '?wechat_hash=' + hash :
        // 如果 search 不为空
        location.search + '&wechat_hash=' + hash;
      // 重新加载页面
      location.reload(true);
    }

这样看着还不错，不过很快就遇到新问题：如果在页面 B 先后进行了 4 次操作，这时点击后退按钮 ，还是会停留在页面 B ，要点击 4 次才能回到页面 A 。浏览器历史忠实地记录了我们先后 4 次更改 location.search 的操作。要立即返回页面 A ，我们还得更改历史：

    var reload = function(){
      var hash = +(new Date());
      var new_search = (/wechat_hash/).test(location.search) ? 
        // 如果之前有添加过指纹，就更新它
        location.search.replace(/wechat_hash=\d+(&?)/,'wechat_hash=' + hash + '$1') :
        location.search == "" ?
        // 如果 search 为空
        '?wechat_hash=' + hash :
        // 如果 search 不为空
        location.search + '&wechat_hash=' + hash;
      // 修改浏览器历史
      var current_title = document.title;
      var new_uri = location.origin + location.pathname + new_search;
      history.replaceState(null, current_title, new_uri);
      // 重新加载页面
      location.reload(true);
    };

最后，完成的代码及测试例子已上传到 [github](https://github.com/yiyizym/wechat_reload) 。