---
layout: post
title: 读《Effective TypeScript》
date: 2020-02-09 10:20:28
excerpt: 书上有你在各个技术网站都难看到的内容
categories: 
- frontend
---

两个多月前办了个 ACM 的会员，每年要交 100 多块人民币会费。凭借这个会员身份，可以免费看 Oreilly 线上的图书、视频，如果直接办 Oreilly 会员，一年要花 499 美元，两者相差 30 多倍，价格歧视可以这么大，真是大开眼界。

两个月下来，看了三本书，其中一本叫《Effective TypeScript》，这书刚出版不久（2019/10/17），售价 20 美元左右。

光看这本就把会费赚回来了。

书的副标题是： 62 Specific Ways to Improve Your TypeScript ，内容如书名，是一条条建议搭配具体的代码实例分析讲解。十分适合有一定 TypeScript 实际使用经验但又希望提高姿势水平的程序员。

书中有不少对我很有用的建议和启示，以下只列出四点：

**用集合的视角看类型**

在写 Typescript 的时候，经常会遇到类型错误。其中一种类型错误的提示是：`T1 is not assignable to T2` ，意思是说属于类型 `T1` 的变量不能赋值给属于类型 `T2` 的变量。

假设 `T1` 跟 `T2` 有继承关系，看到这个错误提示，你能想到是 `T1` 继承了 `T2` ，还是反过来，`T2` 继承了 `T1` 呢？

如果你有强类型语言的使用经验，就会知道子类可以赋值给父类，反过来却不行。所以上面的情况是 `T2` 继承了(extends) `T1`。

如果你没有相关经验，也可以从另外一个更通用的角度————数学集合————来看待 Typescript 的类型以及它们之间的关系。

先从最简单的全集开始。

TypeScript 中与全集对应的是类型是 unknown ，如果你对某个类型一无所知，那么它就有可能是任何一种类型；

从 unknown 出发，我们知道某个类型的信息越多、越具体，这个集合就会变得越小。

举个例子，我们知道了类型 T1 有一个属性 name ，（通过继承）在 T1 的基础上，我们知道 T2 还有一个属性 age 。从集合的角度讲，T1 包含了 T2 ，因为如果某个变量属于 T2 的话，它一定也属于 T1 ，反过来就不是这样。

```
interface T1 {
  name: string;
}

interface T2 extends T1 {
  age: number;
}
```

如果我们知道一个类型不包含任何可以访问的属性，那么与这个类型对应的集合就是空集。

TypeScript 中与空集对应的是类型是 never ，属于这个类型的变量从代码逻辑上永远都不能被访问。



**Excess Property Checking**

TypeScript 是一种 "duck typing" 的语言，它并不通过声明时指定的类型名称，而是通过值包含的属性以及方法来检查一个值的类型。

举个例子，以下的写法在 "duck typing" 的语言是合法的：

```
type A = {
    title: string;
}

type B = {
    title: string;
}

let a: A = { title: 'a' }

let b: B = a
```

我们声明了两个类型 `A/B` ，它俩都包含相同的属性，因此 TypeScript 实际上认为变量 `a` 与 `b` 同属一个类型。

我曾经遇到过一个问题，就与这个 "duck typing" 的设计相关。借用书中的例子说明。

```
interface Options {
  title: string;
  darkMode?: boolean;
}

function createWindow(options: Options) {
  if (options.darkMode) {
    setDarkMode();
  }
  // ...
}

createWindow({
  title: 'Spider Solitaire',
  darkmode: true
}) // 会报错： darkmode 不存在于 Options 类型定义，你是不是想要写 darkMode ?

const intermediate = { darkmode: true, title: 'Spider Solitaire' }

createWindow(intermediate) // 不会报错，传进去的参数实际是一模一样的

```

上述两种情况说明，TypeScript 对字面量和中间变量有不同的处理。

如果我们忽略 TypeScript 在第一种情况的报错，编译过后的 javascript 是能跑起来的，也就是说 TypeScript 对字面量采取更严格的处理（可以配置开启或关闭），这个处理被称为 `Excess Property Checking` 。

这种处理的好处是防止开发者犯低级错误，例如打错字。

至于为什么不对中间变量也采取相同的处理，是因为这样做的开销会比你想像中的大。因为 "duck typing" 的缘故，被视为与上述类型 `Options` 是同一种类型的其他类型有很多，这些类型的实例都可以当作 `createWindow` 的参数：

```
const o1: Options = document;  // OK
const o2: Options = new HTMLAnchorElement;  // OK
```

这时候要想知道开发者是不是打错字，就得知道 document 实例上有没有 `darkMode` 这个布尔值属性，就得遍历 document 上面几百个属性，还要回溯原型链，这样做开销太大。

在兼故性能和体验后， TypeScript 采用折衷的做法：只对字面量做严格的类型检查。



Types that represent both valid and invalid state are likely to lead to confusing and error-prone code.

Interfaces with multiple properties that are union types are often a mistake because they obscure the relationships between these properties.

