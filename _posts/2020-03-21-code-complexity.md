---
layout: post
title: 代码复杂度分析
date: 2020-03-21 08:20:28
excerpt: 一个杠精对两种理论的偏心比较
categories: 
- tech
- frontend
---

衡量代码的好坏，有很多标准，比如 bug 率，时间复杂度，理解的难易程度等等。 bug 与时间复杂度的多少很容易衡量，唯独「理解的难易程度」没有一套大家都知道而且通用的测量方法。

闲逛时发现一个用来测量代码复杂度的 vscode [插件](vscode-codemetrics)，它的理论基础是 [Cyclomatic Complexity](Cyclomatic_complexity)，以下翻译成`循环复杂度`。

循环复杂度理论有几条数学公式，应用起来却很简单：

- 每一个方法的起始复杂度为 1 
- 按顺序从上到下看方法内部可执行的代码。只要遇到一个 判断操作 就增加 1 复杂度
- 判断操作包括 if/while/&&/\|\|/for/case/ternary operator 等等

本文的重点不在循环复杂度，想深入了解的话请看这篇[文章](chinese-version-cyclomatic-complexity)。

我比较关心的是，为什么它在前端界不流行。理由应该不是大家不关心代码的好坏，而是这种衡量方式存在问题。

用 `code complexity javascript` 之类的关键词搜了下，发现 eslint 早就可以配置 [complexity](eslint-complexity) 规则。

作为一个坚持己见的人，接受不了它早就被广泛接受的事实，我点开 eslint complexity 页面中每一条参考链接，最终看到这篇对循环复杂度提出异议的[文章](complexity-for-javascript)。

作者从多个角度评价这套理论：

- 复杂度相同的两段代码，理解难易程度可以相差很远；因为有多少个判断分支就会相应增加多少复杂度，循环复杂度衡量的是“代码有多难测试”，而不是“代码有多难读懂”；
- 循环复杂度于 1976 年面世，当时的编程语言很简单，今天的 Javascript 远远比那时循环复杂度的应用对象——Fortran——复杂得多，比如异步编程、闭包等等；
- 同样是判断逻辑，嵌套的判断语句，比不嵌套的判断语句要更难懂。两者不应该拥有相同的复杂度；
- 循环复杂度没有测量出代码的内聚程度，也没测量出代码在多大程度上遵循[得墨忒耳定律](Law_of_Demeter)；
- 循环复杂度没有考虑递归调用。递归调用应该增加复杂度；
- 循环复杂度没有考虑 try...catch 语句， catch 是一种特殊类型的 if （如果出现异常，就执行以下代码）；
- 循环复杂度只关心代码结构复杂度，没有测量数据复杂度；

上面几点都很有道理，我认为这才是循环复杂度不流行的原因。

接下来介绍另一种测量代码复杂度的理论：[Cognitive Complexity](cognitive-complexity)，以下翻译成`认知复杂度`，它解决了上面七个问题中的四个。

认知复杂度并不复杂，它只有三个基本原则：

- 使用编程语言自带的语法糖(shorthand)并不会增加复杂度；
- 只要打断程序的线性执行流就会增加复杂度，比如 条件判断、循环、跳转、异常捕获、递归调用；
- 在嵌套上下文里打断程序的线性执行流，会带来更多的复杂度。

第一条原则可以用 ecmascript 将会推出的 [optional chaining operator](optional-chaining-operator) 语法来解释。使用传统的方式，以下代码复杂度是 3 ：

```javascript
var person;
if(person && person.profile && person.profile.name) {
  console.log(person.profile.name)
}
```

如果使用 `optional chaining operator` ，代码复杂度是 1 ：

```javascript
var person;
if(person?.profile?.name) {
  console.log(person.profile.name)
}
```

这条原则将语法糖当成是一个——隐藏了具体的实现方式的——方法调用。

第二条原则跟循环复杂度类似，在条件判断之余，还考虑了跳转、异常捕获和递归。

第三条原则考虑了嵌套对复杂度的影响。在越深的嵌套上下文里打断程序线性执行流，增加越多的复杂度。这很符合直觉：嵌套层级越深，代码越难懂。


这个[文档](CognitiveComplexity)能看到上面三条原则映射到实际代码上的具体实现。

参考文章最开始提到的[插件](vscode-codemetrics)的[源码](tsmetrics-core)以及这份文档，不难实现一个测量认知复杂度的工具（我做出来了，因为可能会违反公司政策，暂时不放源码出来）。


在对自己的项目用工具分析过后，发现分析认知复杂度至少有两点积极意义：

- 可以衡量项目的业务复杂度，在接手别人的项目前看看业务是不是很复杂，坑不坑
- 可以看到某个方法的写法是不是有问题，加以改良。如下：
  ```javascript
  // 改良之前，复杂度： 5
  if(sex === 'female') { // +1
    if(age < 18) { // +2 这个 if 处于嵌套上下文中，会增加额外的复杂度
      return age
    } else { // +1
      return 18
    }
  } else { // +1
    return age
  }

  // 改良之后，复杂度：2
  if(sex === 'female' // +1
    && age > 18) { // +1
      return 18 
  }
  return age
  ```

有时间再做一个基于认知复杂度理论的分析代码复杂度的 vscode 插件，一定很有意思。

**参考**

- [vscode codemetrics](vscode-codemetrics)
- [Cognitive Complexity](cognitive-complexity)
- [Cognitive Complexity Paper](CognitiveComplexity)


[vscode-codemetrics]: https://marketplace.visualstudio.com/items?itemName=kisstkondoros.vscode-codemetrics
[Cyclomatic_complexity]: https://en.wikipedia.org/wiki/Cyclomatic_complexity
[chinese-version-cyclomatic-complexity]: http://kaelzhang81.github.io/2017/06/18/详解圈复杂度/
[eslint-complexity]: https://eslint.org/docs/rules/complexity
[complexity-for-javascript]: https://craftsmanshipforsoftware.com/2015/05/25/complexity-for-javascript
[cognitive-complexity]: https://docs.codeclimate.com/docs/cognitive-complexity
[optional-chaining-operator]: https://alligator.io/js/es2020/#optional-chaining-operator
[CognitiveComplexity]: https://www.sonarsource.com/docs/CognitiveComplexity.pdf
[Law_of_Demeter]: https://en.wikipedia.org/wiki/Law_of_Demeter
[tsmetrics-core]: https://github.com/kisstkondoros/tsmetrics-core