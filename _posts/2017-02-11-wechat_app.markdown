---
layout: post
title: 微信小程序组件开发示例
date: 2017-02-11 03:09:57
description: 最近开始折腾小程序了
categories: tech
tags:
- 微信小程序
- 插件
---

**本文介绍微信小程序 （自制）上传图片组件 的关键实现，喜欢通过代码学习的朋友，可以直接看 [github 源码](https://github.com/yiyizym/wechat_mini_program_upload_img_module){:target="_blank"}**

## 缘由 

最近在微信小程序上要实现上传图片的功能，因为多个页面都会用到这个功能，我试着就像网页开发一样，写一个能复用的组件。

上传图片的功能，微信小程序已经提供了相应的组件和API，结合 weui 样式，如果不考虑复用的话，很容易实现（官方 demo 就可以拿来用 ^_^ ）。

如果要复用，可以利用模板，但是会面临微信小程序的很多限制。

## 限制 

举个例子，下面是一个模板文件 customer.wxml （ 注意模板文件里绑定了一个回调函数 sayHello ）

```
<template name="customer" data-customerid="{{id}}" bindtap="sayHello">
  <text>{% raw  %}{{ name }}{% endraw %}</text>
  <text>{% raw  %}{{ gender }}{% endraw %}</text>
  <text>{% raw  %}{{ age }}{% endraw %}</text>
  <block wx:for="orders" wx:for-item="order">
    <view>{% raw  %}{{order.id}}{% endraw %}</view>
    <view>{% raw  %}{{order.detail}}{% endraw %}</view>
  </block>
</template>
```

页面 A.wxml 引用了这个模板文件 :

```
<import src="path/to/customer.wxml">
<template is="customer" data="{% raw  %}{{...customer}}{% endraw %}"></template>
```

如果要显示模板里的 `orders` 部分，页面 A 的 js 文件里 data 必须有一个名为 `customer` 的 key （否则会报错： `firstRender not the data from Page.data` ，应该是因为 `setData` 在模板解析之后执行），如果要调用模板里的回调函数 `sayHello` ，同样必须在页面 A 的 js 文件里先定义它：

```
// A.js
Page({
  data: {
    customer: {} // 可以先写成空 hash ，稍后更新，但 key 必须先存在
  },
  sayHello: function(e){
    // say hello
    // e.target.dataset.customerid
  }
})
```

## 解决办法

因为这两个限制，必须找出一个办法让模板文件能动态改变引用它的文件（以下称为宿主）的作用域下的一些变量和方法，如下：

```
// A.js
require('path/to/customer.js');

Page({
  data: {
    customer: {}
  }
  onLoad: function(){
    // this 是宿主的执行上下文环境
    // this.data 可以访问 data
    // this.setData 可以更新 data
    // this.func = function() {} 可以往宿主增加新方法
    new Customer(this);
  }
})
```

```
// customer.js
// 这里用到 es6 的类定义语法

class Customer {
  constructor(pageContext){
    this.page = pageContext
    this.page.sayHello = this.sayHello
  }

  sayHello(e){
    // say hello
    // e.target.dataset.customerid
  }
}

module.exports = Customer

```

本文关于微信小程序的组件开发关键点介绍完毕，[源码](https://github.com/yiyizym/wechat_mini_program_upload_img_module){:target="_blank"} 还展示了如何 设置组件的默认配置以及更改组件的回调方法。