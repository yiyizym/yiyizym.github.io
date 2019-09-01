---
layout: post
title: 一个定制 vue 输入框组件的思路
date: 2019-08-31 10:20:28
excerpt: 基于现有控件基础上的再定制
categories: 
- fronted
---

之前接到一个任务，要求用一个输入框让用户得以输入商品的折扣，但是折扣的形式根据用户所在的国家地区的不同而不同。具体来说：英语国家可以输入 1 ～ 99 的数值，表示商品的优惠(discount)；中文地区可以输入 0.1 ～ 9.9 的数值，表示商品的折扣(percentage)。

举例来说，英语国家的用户输入 15 ，表示商品会给用户原价 15% 的优惠；而中文地区的用户输入 8.5 ，表示商品实际价格是原价的 85% 。

二者在前端展示时刚好互补，但是后台保存数据时，统一使用英语国家的形式。

也就是说，在展示数据和处理用户的输入时前端可能要转换一下。

这种处理数据的逻辑，我个人有一个倾向：将逻辑向最底层或者最顶层两端推，而不是放在系统的中间。在这个例子中，要么将处理逻辑放在输入组件中，要么在接收数据、发送数据时做转换；这样系统的大部分代码都不用知道这个特殊的逻辑，而且出问题了也容易定位。

出于复用、以及更容易维护代码考虑，将处理逻辑放在输入组件中会更好。

先声明一点：以下具体实现不是本人想出来的，也不是实际业务中运行的代码。虽然也不是什么高深的技巧，但我觉得写得好，分享出来希望能帮到有需要的人。

假设前端项目用的框架是 element ui ，我们要复用这个框架的 el-input 组件，同时要注入以上特殊的业务逻辑，实现一个[基础组件](https://vuejs.org/v2/style-guide/#Base-component-names-strongly-recommended)。

官方有实现基础组件的指南，其中有一点是 [Disabling Attribute Inheritance](https://vuejs.org/v2/guide/components-props.html#Disabling-Attribute-Inheritance)，这样做可以阻止组件的根元素继承上面传下来的属性，再配合使用 [`$attrs`](https://cn.vuejs.org/v2/api/index.html#vm-attrs) 可以将上面传下来的属性(除去 style/class 属性以及在 props 中定义的属性绑定)传给真正需要的组件。

具体来说，我们要实现一个封装了 el-input 组件的基础组件，将上面传下来的属性传进 el-input 。

template 的内容：
```html
<label>
  label: 
  <el-input
    v-bind="$attrs"
    placeholder="请输入内容"/>
</label>
```

script 的内容：
```javascript
export default {
  name: 'CustomInput',
  inheritAttrs: false
}
```

接下来我们要在组件内部维护一个变量，显示输入框的内容，并且在用户输入时向上面触发一个事件。将这个变量命名为 `internalValue` ，作为 `v-model` 指令的属性值传到 el-input 组件。

template 的内容：
```html
<label>
  label: 
  <el-input
    v-model="internalValue"
    v-bind="$attrs"
    placeholder="请输入内容"/>
</label>
```

说一下 `v-model` ，它是一个语法糖，假设你这样写： 

```html
<input v-model="data" />
```

这种写法与下面的写法是造价的：

```html
<input v-bind:value="data" v-on:input="data = $event.target.value" />
```

使用 `v-model` 可以解决输入框显示的问题，但怎样在用户输入时向上面触发一个事件呢？

方法有很多，比如 `watch` 这个 `internalValue` 值，这个值被改变时触发事件；或者在 el-input 组件上使用 `v-on:input` 指令（即使用了 `v-model` 指令，你还可以使用 `v-on:input` 指令，两者不会相互影响）；你甚至可以把 `v-model` 拆散成 `v-bind:value` 和 `v-on:input` 两个指令。

但这些做法都不够聪明。联想到 vue 实例的 computed 属性可以设置 getter 和 setter 。我们可以把 `internalValue` 设置为组件的 computed 属性，在 getter/setter 集中处理业务逻辑。

```javascript
export default {
  name: 'CustomInput',
  inheritAttrs: false,
  computed: {
    internalValue: {
      get() {

      },
      set(rawValue) {

      }
    }
  }
}
```

接下来结合业务逻辑，定义组件的一些属性。

- type 属性，有两个可能值， `discount` 表示处于英语国家， `percent` 表示处于中文地区
- input 属性，由上层传下来的值，永远是 `discount` 形式

根据 type 属性，在 getter/setter 中做数值转换。

```javascript
export default {
  name: 'CustomInput',
  inheritAttrs: false,
  props: {
    type: {
      type: String,
      default: 'discount'
    },
    input: {
      type: String|Number,
      default: ''
    }
  },
  computed: {
    value: {
      get: function() {
        // input is always discount
        return this.type === 'discount' ? Number(this.input) : this.discountToPercent(this.input)
      },
      set: function(rawValue) {
        // always emit discount
        const value = this.type === 'discount' ? Number(rawValue) : this.percentToDiscount(rawValue)
        this.$emit('input', value)
      }
    }
  },

  methods: {
    // 8.5 -> 15
    percentToDiscount(percent) {
      return (10 - percent) * 10
    },

    // 30 -> 7
    discountToPercent(discount) {
      return (100 - discount) / 10
    }
  }
}
```

目前为止，我们的组件已经能实现功能，但是作为基础组件，还缺少了些东西。

我们只把 `$attrs` 传给 el-input 组件，却没有把事件也传递过去，而且出于封装考虑，我们不应该把 input 事件绑定传递给 el-input 。

```html
<label>
  label:
  <el-input
    v-bind="$attrs"
    v-model="value"
    v-on="filteredListener"
    placeholder="请输入内容"/>
</label>
```

```javascript
export default {
  // ...省略部分代码
  computed: {
    filteredListener(){
      const filteredListener = Object.assign({}, this.$listeners)
      delete filteredListener.input
      return filteredListener
    }
    //...省略部分代码
  }
  //...省略部分代码
}
```

最后还得处理用户的输入，比如用户输入小数点/非数字时输入框的回显， javascript 小数精度问题等等。这些都可以在 getter/setter 中处理，不过细节非常多，我也没能一一处理，想了解更多可以看[代码](https://github.com/yiyizym/vue_custom_input)，就不再说了。