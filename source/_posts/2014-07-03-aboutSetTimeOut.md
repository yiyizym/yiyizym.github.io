---
layout: post
title: 关于setTimeout二三事
description: "定时器与javascript引擎、浏览器及eval函数"
keywords: 定时器, javascript引擎, 线程、eval
categories: frontend
---

浏览器中的javascript引擎是单线程的，如果在setTimeout设定的时间到达时，javascript引擎还在处理另外的代码，那么setTimeout设定的事件就只有排队等待了。所以一般来说setTimeout设定的时间都是不准确的，会比设定的晚。就算setTimeout时间设定为0,也不一定马上执行，这样设定是把想执行的函数放在javascript引擎执行队列的末尾。

浏览器内部是多线程的，包括：GUI线程、javascript引擎线程、定时器线程、事件线程、http请求线程等。我们能使用定时器是因为浏览器会为setTimeout开一个定时器线程。我们能使用ajax实现异步请求也是因为浏览器能为其开一个http异步请求的线程。

setTimeout和setInterval接受的第一个参数可以是字符串，javascript会隐式调用eval函数来解析这个字符串，这种情况下解析后的字符串将在全局作用域中执行。会产生意想不到的后果。而且定时器（包括setTimeout和setInterval）不是ECMAScript的标准。各家浏览器在一些实现的细节上各有不同，比如如何解析字符串参数在不同的javascript引擎实现中可能不同。所以十分不建议使用字符串作为定时器的第一个参数。


**参考文献**


- [How JavaScript Timers Work](http://ejohn.org/blog/how-javascript-timers-work/)
- [JavaScript 工作线程实现方式](http://www.ibm.com/developerworks/cn/web/1105_chengfu_jsworker/index.html)
- [JavaScript可否多线程? 深入理解JavaScript定时机制](http://www.phpv.net/html/1700.html)
- [JavaScript 秘密花园](http://bonsaiden.github.io/JavaScript-Garden/zh/#intro)