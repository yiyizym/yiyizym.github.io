---
layout: post_with_octocat
title: from nodejs request to promise
date: 2016-04-16 19:50:24
description: 把 nodejs 中的 request 模块 转换为 es2015 的 Promise
categories: frontend
tags: 
- request
- promisify
- node
- es2015
---

## 声明 

文中的 promisify 函数原型出自 月影 的[这篇博客](http://blog.h5jun.com/post/decorator-functional.html)。

## 了解[Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)

```
  // 初始化时接收一个方法，此方法接收另外两个方法
  new Promise(function(resolve, reject){
  //在此方法中做一些异步操作
  //在异步操作的回调方法中根据情况，分别调用 resolve 或者 reject
  });
```

## 了解[request](https://github.com/request/request)

```
  'use strict';
  let request = require('request');
  //request 最简单的用法
  request(url, function(err, response, body){
    if(err){
      //处理错误
    } else if(response.statusCode == 200){
      //处理成功响应
    }
  });
```

## 把 request 转换为 promise 的用例

```
  'use strict';
  let request = require('request');
  //把 request 通过 promisify 转换后
  getData = promisify(request);
  //就可以使用 promise 的方法
  getData('http://www.bing.com').then(function(){
    //成功回调
  })
```

## promisify 实现

```
  //接收一个方法，此处即是 request
  function promisify(func){
    //返回另一个方法，此方法接收 url
    return function(url){
      let requestArgs = arguments;
      //返回一个 Promise
      return new Promise(function(resolve, reject){
        //在方法体内做异步操作，即调用 request
        //不要忘记 request 接收一个 url 以及一个回调函数
        //也不要忘记要在回调函数里根据情况分别调用 resolve 和 reject
        //所以要把 resolve 和 reject 塞进 request 的回调函数中
        let newArgs = Array.prototype.slice.call(requestArgs);
        newArgs.push(function(err, response, body){
          if(err){
            reject(err);
          } else if(!err && response.statusCode == 200) {
            resolve(body);
          }
        });
        //newArgs 是一个数组，第一个元素是 url ，第二个是回调函数
        func.apply(this, newArgs);
      });      
    }
  }
```

## 完整示例

```
  'use strict';
  let request = require('request');
  //接收一个方法，此处即是 request
  function promisify(func){
    //返回另一个方法，此方法接收 url
    return function(url){
      let requestArgs = arguments;
      //返回一个 Promise
      return new Promise(function(resolve, reject){
        //在方法体内做异步操作，即调用 request
        //不要忘记 request 接收一个 url 以及一个回调函数
        //也不要忘记要在回调函数里根据情况分别调用 resolve 和 reject
        //所以要把 resolve 和 reject 塞进 request 的回调函数中
        let newArgs = Array.prototype.slice.call(requestArgs);
        newArgs.push(function(err, response, body){
          if(err){
            reject(err);
          } else if(!err && response.statusCode == 200) {
            resolve(body);
          }
        });
        //newArgs 是一个数组，第一个元素是 url ，第二个是回调函数
        func.apply(this, newArgs);
      });      
    }
  }
  //把 request 通过 promisify 转换后
  var getData = promisify(request);
  //就可以使用 promise 的方法
  getData('http://www.bing.com').then(function(content){
    console.log(content);
    //成功回调
  }).catch(function(reason){
    //异常回调
    console.log(reason);
  });

```