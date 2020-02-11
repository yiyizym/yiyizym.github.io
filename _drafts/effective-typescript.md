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

Excess Property Checking ，安全与效率之间的取舍

Types that represent both valid and invalid state are likely to lead to confusing and error-prone code.

Interfaces with multiple properties that are union types are often a mistake because they obscure the relationships between these properties.

