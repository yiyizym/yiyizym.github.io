---
layout: post
title: 一个简单的 Promise 实现
date: 2017-03-12 02:50:26
description: 这篇文章只是抄人家的原创，原本没必要写的，只是自己花了一天才看懂人家那篇文章，我觉得拿来“改善”一下形式
categories: 
- tech
- frontend
---

介绍 Promise 实现的文章早已烂大街了，但大多数文章都是先解读 Promise/A+ 标准，然后用一行行代码实现标准。能用代码实现标准是件了不起的事，但我很讨厌这样，那些文章我都没能读完。

既然读者要看实现，那就可以假设他们都已熟悉 Promise 的使用方法。能不能换个角度，从使用出发，逐步实现一个简单可用的 Promise 呢？

最近我就看到一篇这样的[文章](http://tech.meituan.com/promise-insight.html)，以及它的[参考文章](http://www.mattgreer.org/articles/promises-in-wicked-detail/)。下面，我就试着整合两篇文章，聊聊一个简单的 Promise 实现。

*简单的使用方法*

先来看一个简单的 Promise 使用例子，暂时不考虑 reject 和异常的情况。

```
getUserId().then(showUserId)

function getUserId(){
  return new Promise(function(resolve){
    setTimeout(function(){
      resolve(1)
    }, 2000)
  })
}

function showUserId(id){
  console.log(id)
}
```

可以看到 Promise 实例化时需要传入一个函数（fn）， Promise 在实例化时会调用 fn ；Promise 有一个实例方法 then ，以及一个私有方法 resolve 。

```
function Promise(fn){
  var callback = null
  this.then = function(cb){
    callback = cb
  }
  function resolve(value){
    callback(value)
  }
  fn(resolve)
}
```

*then 与 resolve 的调用顺序*

运行上面这段代码会报错，因为在执行 fn(resolve) 时， Promise 实例化还没完成， this.then 没有执行，callback 是 null 。用 setTimeout 把 callback 的执行时间推迟到下一个事件循环里来解决这个问题：

```
function Promise(fn){
  var callback = null
  this.then = function(cb){
    callback = cb
  }
  function resolve(value){
    setTimeout(function(){
      callback(value)
    }, 0)
  }
  fn(resolve)
}
```
用上 setTimeout 后，还支持先生成 Promise 实例，在后面再调用 then ：

```
var promise = getUserId()

promise.then(showUserId)

```

*多次调用 then*

我们经常会给 Promise 实例添加多个回调，举个例子：

```
var promise = getUserId()

promise.then(showUserId)
promise.then(showUserIdAgain)

function showUserIdAgain(id){
  console.log('again ! ', id)
}

```

用一个数组记下用 then 添加的回调，在 resolve 时遍历调用数组中的回调：

```
function Promise(fn){
  var callbacks = []
  this.then = function(cb){
    callbacks.push(cb)
  }
  function resolve(value){
    setTimeout(function(){
      callbacks.forEach(function(callback){
        callback(value)
      })
    }, 0)
  }
  fn(resolve)
}

```

*链式调用 then*

我们经常会像下面这样链式调用 then :

```
var promise = getUserId()

promise
  .then(showUserId)
  .then(showUserIdAgain)

```

只要在调用 then 时，返回 Promise 实例的引用就能满足这点：

```
function Promise(fn){
  var callbacks = []
  this.then = function(cb){
    callbacks.push(cb)
    return this
  }
  function resolve(value){
    setTimeout(function(){
      callbacks.forEach(function(callback){
        callback(value)
      })
    }, 0)
  }
  fn(resolve)
}
```


** TODO **

*异步调用 then*

一般情况下，我们用同步的方式调用 then ，但有时候我们也会异步调用 then ：



*then 返回 Promise 实例*

*处理失败与异常*