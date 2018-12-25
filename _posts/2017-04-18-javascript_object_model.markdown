---
layout: post_with_octocat
title: 简单总结 javascript 对象模型
date: 2017-04-18 01:18:27
description: 看过不少 javascript 对象、继承、原型链等知识点，但一直没能把点连成线，今天就来好好总结下。
categories: frontend
---

**更新 2018-12-22**

下文提及的 [`__proto__`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/proto) 原是厂家的自定义属性，后来被大多数厂家支持。但已被标记为 Deprecated ，不再推荐使用。

如果需要获取对象的原型，可使用 `Object.getPrototypeOf(obj)` 代替 `obj.__proto__` 。


**本文假设读者已对 javascript 继承和原型链有所了解，如果没有，可以先到[这里](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)补补课**

最近在整理 javascript 知识点时，逐渐发觉 javascript 所有的对象都在一套基于原型链体系之中，这套体系描述了对象实例与类、子类与父类的关系。

**几乎一切都是对象**

在 javascript 中，几乎一切（除了 `undefined` 和 `null`）都是对象： `42` 这个数字，是 `Number` 类的一个实例对象；`true` 是 `Boolean` 类的一个实例对象。

类同时也是别的类的实例： `Number` 类和 `Boolean` 类是 `Object` 类的实例对象，`Object` 类是 `Function` 类的实例对象，只有 `Function` 类比较特别，它是自己的实例。

**`__proto__`&`prototype`**

所有对象都有一个指向自己的原型的引用，在 javascript 中，对象可以通过 `__proto__` 属性获取对象自己的原型。继续上面的例子：

```
(42).__proto__ 
// Number {constructor: function, toExponential: function, toFixed: function, toPrecision: function, toString: function…}
(true).__proto__ 
// Boolean {[[PrimitiveValue]]: false, constructor: function, toString: function, valueOf: function}
var o = {}
o.__proto__
// Object {__defineGetter__: function, __defineSetter__: function, hasOwnProperty: function, __lookupGetter__: function, __lookupSetter__: function…}
```

对象还有一个 `prototype` 属性，它指向一个有 `constructor` 属性的简单的对象， `constructor` 又指向对象的构造函数：

```
function A(){}
A.prototype
// Object {constructor: function A()}
```

对象的 `__proto__` 属性和 `prototype` 属性是完全不一样的东西，但有关系：在使用 `new` 关键字实例化对象时，对象的 `__proto__` 属性指向它所属的类的 `prototype` 属性，接上例：

```
function A(){}
var a = new A();
a.__proto__ === A.prototype
// true
```

而使用 `Object.create` 方法时，实例对象的 `__proto__` 指向的不是类的 `prototype` ，而是类本身：

```
function A(){}
var aa = Object.create(A)
aa.__proto__ === A.prototype
// false
aa.__proto__ === A
// true
```

使用 `class` 关键字时，生成的原型跟用 `Object.create` 的类似

```
class A(){}
class AA extends A {}
AA.__proto__ === A.prototype
// false
AA.__proto__ === A
// true
```

**原型链**

在 javascript 的原型链体系中，所有对象都是 `Object` 类的实例对象，通过递归调用 `__proto__` 属性可以看到对象的整条原型链：

```
function printProtoOf(obj) {
  var protos = [String(obj)]; // 可能会报错 Function.prototype.toString is not generic ，不是所有的对象都能用 string 表示
  var proto = (obj).__proto__;
  while(proto){
    protos.push(String(proto.constructor));
    proto = (proto).__proto__;
  }
  protos.push(String(proto));
  console.log(protos.join(' -> '))
}

printProtoOf(42)
// 42 -> function Number() { [native code] } -> function Object() { [native code] } -> null
printProtoOf('str')
str -> function String() { [native code] } -> function Object() { [native code] } -> null
function A(){}
var a = new A();
printProtoOf(a)
// [object Object] -> function A(){} -> function Object() { [native code] } -> null
```

**更好的继承**

借助这些细节可以实现更好的继承：

```
// 假设父类是 Animal，要让子类 Cat 继承 Animal

// 先思考继承目标，有两个：属性、方法。前者要复用父类的构造方法，后者要修改子类的原型链。

// 首先复用父类的构造方法，在 Cat 构造函数中调用 Animal 构造函数

function Animal(){}

function Cat(){
  Animal.call(this)
}

// 接下来修改原型链
// 假设 oneCat 是 Cat 的实例对象
// 那么 oneCat 的原型链应该是这样的：
// oneCat.__proto__ === Cat.prototype
// oneCat.__proto__.__proto__ === Animal.prototype

// 实现步骤：

// 1. 新建空白对象
var o = new Object();

// 2. 让空白对象的原型指向 Animal.prototype
o.__proto__ = Animal.prototype

// 以上两步可以使用 Object.create 方法代替，也推荐这样做：
// var o = Objext.create(Animal.prototype)

// 3. 设置空白对象的 `constructor` 属性
o.constructor = Cat

// 4. 让 Cat.prototype 指向这个空白对象
Cat.prototype = o

Animal.prototype.species = '动物';

Cat.prototype.meows = function(){
  console.log('meow meow ~');
}

var oneCat = new Cat();
oneCat.species
// 动物
oneCat.meows()
// meow meow ~

var anotherAnimal = new Animal();
anotherAnimal.species
// 动物
anotherAnimal.meows
// undefined
```