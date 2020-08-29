---
layout: post
title: 一个简单的 Promise 实现
date: 2017-03-12 02:50:26
excerpt: 这篇文章只是抄人家的原创，原本没必要写的，只是自己花了一天才看懂人家那篇文章，我觉得拿来“改善”一下形式
lang: zh_CN
categories: 
- tech
- frontend
---

介绍 Promise 实现的文章早已烂大街了，大多数文章先解读 Promise/A+ 标准，然后用一行行代码实现标准。能用代码实现标准是件了不起的事，但我很讨厌这样，那些文章我都没能读完。

既然读者来看实现，就可以假设他们都已熟悉 Promise 的使用方法。能不能换个角度，从使用出发，逐步实现一个简单可用的 Promise 呢？

最近我就看到一篇这样思路的[文章](http://tech.meituan.com/promise-insight.html)，以及它的[参考文章](http://www.mattgreer.org/articles/promises-in-wicked-detail/)。下面，我试着整合两篇文章，聊聊一个简单的 Promise 实现。

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

可以看到 Promise 实例化时需要传入一个函数：fn ， Promise 在实例化时会调用 fn ；Promise 有一个实例方法 then ，以及一个私有方法 resolve ，可以写一个简单的构造函数：

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

运行上面这段代码会报错，因为在执行 fn(resolve) 时， Promise 实例化还没完成， this.then 没有执行，callback 是 null 。这个问题可以用 setTimeout 把 callback 的执行时间推迟到下一个事件循环里来解决：

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
用上 setTimeout 后，还支持先生成 Promise 实例，过些时候再调用 then ：

```
var promise = getUserId()

promise.then(showUserId)

```

我们经常会给 Promise 实例添加多个回调，举个例子：

```
var promise = getUserId()

promise.then(showUserId)
promise.then(showUserIdAgain)

function showUserIdAgain(id){
  console.log('again ! ', id)
}

```

可以用一个数组记下用 then 添加的回调，然后在 resolve 时遍历调用数组中的回调：

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

一般情况下，我们用同步的方式调用 then ，但有时候我们也会异步调用 then 。比如此刻你忽然想吃泡面：先烧壶水，在水烧开前这段时间到便利店买泡面，回到家水已经烧开了，这时再用开水泡面：

```
function boilWater(){
  return new Promise(function(resolve){
    setTimeout(function(){
      resolve('开水')
    }, 1000)
  })
}

function buyInstantNoodle(){
  return new Promise(function(resolve){
    setTimeout(function(){
      resolve('泡面')
    }, 2000)
  })
}

var promiseOfBoilWater = boilWater()
buyInstantNoodle().then(function(instantNoodle){
  promiseOfBoilWater.then(function(boiledWater){
    console.log('你用' + boiledWater + '泡' + instantNoodle)
  })
})
```

要让 promise 在调用 resolve 之后，还能执行通过 then 添加的回调方法，需要用一个标记区分 promise 的状态，调用 resolve 之前是 pending 状态，之后是 fulfilled 。在 pending 状态调用 then 会把方法放进回调数组中，而在 fulfilled 状态下调用 then 则会直接调用方法。

```
function Promise(fn){
  var callbacks = []
  var state = 'pending'
  var value = null
  this.then = function(cb){
    if(state === 'pending'){
      callbacks.push(cb)
    }
    else{
      cb(value)
    }
    return this
  }
  function resolve(newValue){
    value = newValue
    state = 'fulfilled'
    setTimeout(function(){
      callbacks.forEach(function(callback){
        callback(value)
      })
    }, 0)
  }
  fn(resolve)
}
```

我们经常会像下面这样链式调用 then ，假设你家里有泡面，不用下楼买，只需要烧开水 :

```
var promiseOfBoilWater = boilWater()

promiseOfBoilWater
  .then(takeOutInstantNoodle)
  .then(eat)

function takeOutInstantNoodle(boiledWater){
  return boiledWater + '煮泡面'
}

function eat(noodle){
  console.log(noodle + ' 味道就是好！')
}

```

要实现这点,在调用 then 时，需要返回一个 Promise 实例。这个实例要做的事情是：

1. 在上一个 promise 执行 resolve 后，先调用 onResolved 回调；
2. 把得到的结果作为参数放到自身的 then 回调中执行。

```
function Promise(fn){
  var handlers = []
  var state = 'pending'
  var value = null
  this.then = function(onResolved){
    return new Promise(function(resolve){
      handle({
        onResolved: onResolved,
        resolve: resolve
      })
    })
  }
  function handle(handler){
    if(state === 'pending'){
      handlers.push(handler)
    }
    else{
      if(handler.onResolved){
        var ret = handler.onResolved(value)
        handler.resolve(ret)
      }
      else{
        handler.resolve(value)
      }
    }
  }
  function resolve(newValue){
    value = newValue
    state = 'fulfilled'
    setTimeout(function(){
      handlers.forEach(function(handler){
        handle(handler)
      })
    }, 0)
  }
  fn(resolve)
}
```

有了链式调用 then 的基础，回头看之前“烧开水——买泡面——泡泡面”的代码，我们一般不会那样写，而会这样写：

```
boilWater()
  .then(buyInstantNoodle)
  .then(eat)

function boilWater(){
  return new Promise(function(resolve){
    setTimeout(function(){
      resolve('开水')
    }, 1000)
  })
}

function buyInstantNoodle(boiledWater){
  return new Promise(function(resolve){
    setTimeout(function(){
      resolve(boiledWater + '煮泡面')
    }, 2000)
  })
}

function eat(noodle){
  console.log(noodle + ' 味道就是好！')
}

```

传入 then 的参数 buyInstantNoodle 会返回一个 promise 。我们先看看，在不改变 Promise 构造函数的基础上，要怎样写才能让程序正常执行：

```
boilWater()
  .then(buyInstantNoodle)
  .then(function(promiseOfBuyInstantNoodle){
    // 要让使用的人自己处理返回的 promise
    promiseOfBuyInstantNoodle.then(eat)
  })
```

为了方便使用的人，要在 Promise 构造函数的 resolve 方法里判断参数是不是 promise 实例，是的话就先调用实例的 then 方法。

```
function Promise(fn){
  var handlers = []
  var state = 'pending'
  var value = null
  this.then = function(onResolved){
    return new Promise(function(resolve){
      handle({
        onResolved: onResolved,
        resolve: resolve
      })
    })
  }
  function handle(handler){
    if(state === 'pending'){
      handlers.push(handler)
    }
    else{
      if(handler.onResolved){
        var ret = handler.onResolved(value)
        handler.resolve(ret)
      }
      else{
        handler.resolve(value)
      }
    }
  }
  function resolve(newValue){
    if(typeof newValue === 'object' && typeof newValue.then === 'function'){
      // resolve 就是当前这个定义的函数
      newValue.then(resolve)
    }
    else{
      value = newValue
      state = 'fulfilled'
      setTimeout(function(){
        handlers.forEach(function(handler){
          handle(handler)
        })
      }, 0)
    }
  }
  fn(resolve)
}
```

稍微扩展一下上面的代码，就能处理 reject 的情况：

```
function Promise(fn){
  var handlers = []
  var state = 'pending'
  var value = null
  this.then = function(onResolved, onRejected){
    return new Promise(function(resolve, reject){
      handle({
        onResolved: onResolved,
        onRejected: onRejected,
        resolve: resolve,
        reject: reject
      })
    })
  }
  function handle(handler){
    if(state === 'pending'){
      handlers.push(handler)
    }
    else if(state === 'fulfilled'){
      if(handler.onResolved){
        var ret = handler.onResolved(value)
        handler.resolve(ret)
      }
      else{
        handler.resolve(value)
      }
    }
    else{
      if(handler.onRejected){
        var ret = handler.onRejected(value)
        // 因为前一个 promise 中有处理 reject 的情况
        // 所以要调用下一个 promise 的 resolve
        handler.resolve(ret)
      }
      else{
        handler.reject(value)
      }
    }
  }
  function resolve(newValue){
    if(typeof newValue === 'object' && typeof newValue.then === 'function'){
      // resolve 就是当前这个定义的函数
      newValue.then(resolve, reject)
    }
    else{
      value = newValue
      state = 'fulfilled'
      setTimeout(function(){
        handlers.forEach(function(handler){
          handle(handler)
        })
      }, 0)
    }
  }
  function reject(reason){
    value = reason
    state = 'rejected'
    setTimeout(function(){
      handlers.forEach(function(handler){
        handle(handler)
      })
    }, 0)
  }
  fn(resolve, reject)
}
```

最后还得处理异常情况：

```
function Promise(fn){
  var handlers = []
  var state = 'pending'
  var value = null
  this.then = function(onResolved, onRejected){
    return new Promise(function(resolve, reject){
      handle({
        onResolved: onResolved,
        onRejected: onRejected,
        resolve: resolve,
        reject: reject
      })
    })
  }
  function handle(handler){
    if(state === 'pending'){
      handlers.push(handler)
    }
    else if(state === 'fulfilled'){
      if(handler.onResolved){
        try {
          var ret = handler.onResolved(value)
          handler.resolve(ret)
        }
        catch(e){
          handler.reject(e)
        }
      }
      else{
        handler.resolve(value)
      }
    }
    else{
      if(handler.onRejected){
        try {
          var ret = handler.onRejected(value)
          // 因为前一个 promise 中有处理 reject 的情况
          // 所以要调用下一个 promise 的 resolve
          handler.resolve(ret)
        }
        catch(e){
          handler.reject(e)
        }
      }
      else{
        handler.reject(value)
      }
    }
  }
  function resolve(newValue){
    try {
      if(typeof newValue === 'object' && typeof newValue.then === 'function'){
        // resolve 就是当前这个定义的函数
        newValue.then(resolve, reject)
      }
      else{
        value = newValue
        state = 'fulfilled'
        setTimeout(function(){
          handlers.forEach(function(handler){
            handle(handler)
          })
        }, 0)
      }
    }
    catch(e){
      reject(e)
    }
  }
  function reject(reason){
    value = reason
    state = 'rejected'
    setTimeout(function(){
      handlers.forEach(function(handler){
        handle(handler)
      })
    }, 0)
  }
  fn(resolve, reject)
}

```

全文完。