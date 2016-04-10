title: 两个小巧的javascript类工厂
description: "es6才原生支持 class ，来看看在此之前大神们怎样实现类工厂吧"
keywords: "p.js , 原型链"
date: 2015-07-31 23:02:51
categories: frontend
tags: frontend
---

## 阅读前，希望你了解javascript的原型链

## P.js

### [项目地址](https://github.com/jneen/pjs)

### 基础用法：


    var Animal = P(function(animal){
          animal.init = function(name){
              this.name = name;
          };
          animal.move = function(meters){
              console.log(this.name + " moved " + meters + " m.");
          }
      });

    var Snake = P(Animal, function(snake, animal){
            snake.move = function(){
                console.log("Slithering...");
                animal.move.call(this, 5);
            };
        });

    var Horse = P(Animal, function(horse, animal){
            horse.move = function(){
                console.log("Galloping...");
                animal.move.call(this, 45);
            };
        });

    var sam = Snake("Sammy the Python"),
        tom = Horse("Tommy the Palomino");

    sam.move(); 
    // 输出 
    // Slithering...
    // Sammy the Python moved 5 m.
    tom.move();
    // 输出 
    // Galloping...
    // Tommy the Palomino moved 45 m.


### 源码

    //说点题外话，作者利用闭包做了不少事情：

    //传入变量 prototype 是为了能在使用代码压缩工具时缩短代码，例如把 prototype 替换为 p
    //在压缩代码时 obj.prototype 和 obj[prototype] 是不一样的，前者的 prototype 不会被替换，所以要达到压缩变量的目的，还要配合后一种写法

    //ownProperty 是 helper function

    //传入 undefined 是阻止在使用 undefined 时回溯原型链，提高性能

    (function(prototype, ownProperty, undefined) {
        //这个立即执行函数返回 类工厂 P
        //P接受两个参数， 分别对应 父类 和对父类的相关扩展
        //如果只传一个参数，就认为父类是 Object
        return function P(_superclass /* = Object */, definition) {
            // handle the case where no superclass is given
            if (definition === undefined) {
              definition = _superclass;
              _superclass = Object;
            }

            // C is the class to be returned.
            //
            // When called, creates and initializes an instance of C, unless
            // `this` is already an instance of C, then just initializes `this`;
            // either way, returns the instance of C that was initialized.
            //
            //  TODO: the Chrome inspector shows all created objects as `C`
            //        rather than `Object`.  Setting the .name property seems to
            //        have no effect.  Is there a way to override this behavior?

            // C 是 创建好类之后，实例化类时（不管有没有使用new）返回的对象，
            function C() {
                //如果没有使用 new ，则调用 new Bare
                var self = this instanceof C ? this : new Bare;
                self.init.apply(self, arguments);
                return self;
            }

            // C.Bare is a class with a noop constructor.  Its prototype will be
            // the same as C, so that instances of C.Bare are instances of C.
            // `new MyClass.Bare` then creates new instances of C without
            // calling .init().
            //    如果不想在实例化时调用 init() ，可以用 new C.Bare
            function Bare() {}
            C.Bare = Bare;

            // Extend the prototype chain: first use Bare to create an
            // uninitialized instance of the superclass, then set up Bare
            // to create instances of this class.

            //实现类继承，本质上都是用这样的手法：
            //    var TempClass = function(){}
            //    TempClass.prototype = Parent.prototype
            //    Child.prototype = new TempClass()

            var _super = Bare[prototype] = _superclass[prototype];
            var proto = Bare[prototype] = C[prototype] = C.p = new Bare;

            // pre-declaring the iteration variable for the loop below to save
            // a `var` keyword after minification
            // 把 key 声明为变量，方便压缩代码时替换
            var key;

            // set the constructor property on the prototype, for convenience
            //    修正 C 的构造函数，不修正的话会是 Bare
            proto.constructor = C;

            //    extend 返回一个子类
            C.extend = function(def) { return P(C, def); }

            //    这里写得比较复杂，化简一下会是这样 
            //    return (C.open = C)
            //    C.open 用于修改已存在的类的属性
            return (C.open = function(def) {
              if (typeof def === 'function') {
                // call the defining function with all the arguments you need
                // extensions captures the return value.

                //    def 接收的参数有4个
                //    proto为Bare的原型，即Object的原型
                //    _super为父类的原型
                //    C,_superclass

                //如果def返回对象，接下来会把此对象合并到proto里
                def = def.call(C, proto, _super, C, _superclass);
              }

              // ...and extend it
              if (typeof def === 'object') {
                for (key in def) {
                  if (ownProperty.call(def, key)) {
                    proto[key] = def[key];
                  }
                }
              }

              // if no init, assume we're inheriting from a non-Pjs class, so
              // default to using the superclass constructor.
              if (!('init' in proto)) proto.init = _superclass;

              return C;
            })(definition);
        }

      // as a minifier optimization, we've closured in a few helper functions
      // and the string 'prototype' (C[p] is much shorter than C.prototype)
    })('prototype', ({}).hasOwnProperty);

## Simple JavaScript Inheritance

### [地址](http://ejohn.org/blog/simple-javascript-inheritance/)

### 用法

    var Person = Class.extend({
      init: function(isDancing){
        this.dancing = isDancing;
      },
      dance: function(){
        return this.dancing;
      }
    });

    var Ninja = Person.extend({
      init: function(){
        this._super( false );
      },
      dance: function(){
        // Call the inherited version of dance()
        return this._super();
      },
      swingSword: function(){
        return true;
      }
    });

    var p = new Person(true);
    p.dance(); // => true

    var n = new Ninja();
    n.dance(); // => false
    n.swingSword(); // => true

    // Should all be true
    p instanceof Person && p instanceof Class &&
    n instanceof Ninja && n instanceof Person && n instanceof Class


### 源码

    /* Simple JavaScript Inheritance
     * By John Resig http://ejohn.org/
     * MIT Licensed.
     */
    // Inspired by base2 and Prototype
    (function(){

        //fnTest 如果浏览器支持 Function.prototype.toString 打印自身内容，则匹配里面有没有 _super
        //        如果不支持，fnTest匹配结果为 true
      var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

      // The base Class implementation (does nothing)
      this.Class = function(){};

      // Create a new Class that inherits from this class
      Class.extend = function(prop) {
          //先保存当前 Class 的原型
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        //    有一种实现继子的方式是 Child.prototype = new Parent()
        //    这种方式的好处是隔离了 Child.prototype 和 Parent.prototype
        //    坏处是调用了一次 Parent 的构造函数，构造函数中的一些初始化操作对子类来说是多余的
        //    开关 initializing 能控制在 new this() 时不进行初始化操作
        initializing = true;
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {
          // Check if we're overwriting an existing function
          prototype[name] = typeof prop[name] == "function" &&
            typeof _super[name] == "function" && fnTest.test(prop[name]) ?
            //    如果在 proto 里有跟父类同名的函数，而且函数里面有 _super
            //    则用父类的同名函数覆盖 this._super
            (function(name, fn){
              return function() {
                  //    this._super 不一定存在，但先保存下来肯定没错
                var tmp = this._super;

                // Add a new ._super() method that is the same method
                // but on the super-class
                this._super = _super[name];

                // The method only need to be bound temporarily, so we
                // remove it when we're done executing
                //    作者假设 fn 里面调用了 this._super
                //    所以 fn 执行时会调用父类的同名函数
                var ret = fn.apply(this, arguments);        
                this._super = tmp;

                return ret;
              };
            })(name, prop[name]) :
            prop[name];
        }

        // The dummy class constructor
        function Class() {
          // All construction is actually done in the init method
          // 在 extend 时不会调用 this.init
          if ( !initializing && this.init )
            this.init.apply(this, arguments);
        }

        // Populate our constructed prototype object
        Class.prototype = prototype;

        // Enforce the constructor to be what we expect
        Class.prototype.constructor = Class;

        // And make this class extendable
        //    让子类也有 extend 方法
        //    在 es5 严格模式下，禁止使用 arguments.callee ，原因见 https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Functions_and_function_scope/arguments/callee
        //    可以使用命名函数解决此问题
        Class.extend = arguments.callee;

        return Class;
      };
    })();