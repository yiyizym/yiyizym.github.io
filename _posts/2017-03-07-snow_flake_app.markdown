---
layout: post
title: 雪花分形，一次从前到后的尝试
date: 2017-03-07 00:06:50
description: 写写我在做雪花分形应用时遇到了什么事
categories: tech
---

**缘起**

很久之前，我写下一篇介绍“雪花分形”写作理论的文章，在那之后，我觉得可以做一个让人方便地用上这个理论写作的工具，甚至一度幻想着可以靠它提供的服务来赚点钱。

**选型**

> 一个刚启动的项目，做成网页的形式最快收获用户。

我打算先做一个原型。原型的话，网页是最容易做的。在技术选型时我不想依靠思维惯性，抓起身边的 Bootstrap 和 jQuery 撸起袖子就是干，这样多没意思啊。

这时听说 vue 出 2.0 ，虽然没怎么用过 vue ，要不试着用一用？将来也好说自己用过 vue 2.0 嘛 =w= 于是，开始一边看着文档，一边敲代码。

*在工作中，这样的选型思路非常危险哦，除非是玩票项目且完全不在乎成败，又想任性一把*

**踩坑**

- 模块化

雪花分形有十一个步骤，大体分为两条线：剧情和人物。随着步骤的进展，剧情和人物都在之前步骤的基础上逐渐清晰丰满。

用两大类组件来展示这些步骤，可以复用很多代码。话虽如此，作为组件骨架的 `html` 却没少写。

vue 文档里的一个坑就是在介绍组件时没同时展示一种很方便的模板语法。文档中一个例子：

```
Vue.component('my-component', {
  template: '<div>A custom component!</div>'
  // 这里的 template 很简单，如果 template 是一大堆的 html ，写起来很累，读起来也很累
})
```

我用字符串拼接的形式写了两个组件的 `html` 之后，太难受，终于忍不住要找点别的写法。但不想引入 es6 的语法（要搭环境、配置、预先编译一道什么的太麻烦）。最理想的是 vue 原生支持的语法，还真找到了：

```
<!--把模板用 `type` 是 `text/x-template` 的 script 标签包着 -->
<script type="text/x-template" id="component-id">
  <div>A custom component!</div>
</script>

<script>
  Vue.component('my-component', {
    template: '#component-id'
  })
</script>
```

- 驼峰与烤串

在书写组合词时，不同语言有各自约定俗成的习惯，因此有不同的写法，如“组件ID”这个词，在 html/css 中，会写成 `component-id` (kebab-case/烤串形)，在 javascript 中，会写成 `componentId` (camelCase/驼峰形)，在 ruby 中，会写成 `component_id` (snake_case/蛇形)。原本这些只是约定，就算不遵守也不会出问题，但在使用 vue 时，不遵守就会出问题。比如把“组件ID”这个词一律写成 `componentId` ，程序不会正常运行，但也不报错。这是个大坑。

避开这个坑的要点是，时刻注意代码身处的语境，在 html/css 语境中用 kebab-case ，在 javascript 语境中就用 camelCase 。举[文档](https://vuejs.org/v2/guide/components.html#camelCase-vs-kebab-case)中的例子说明语境问题：

```
<script>
Vue.component('child', {
  // myMessage 在 JavaScript 中，所以用 camelCase
  props: ['myMessage'],
  template: '<span>{{ myMessage }}</span>'
}) 
</script>

<div>
  <input v-model="parentMsg">
  <br>
  <!-- my-message 在 HTML 中，用 kebab-case  -->
  <!-- parentMsg 在 JavaScript 中，用 camelCase  -->
  <child :my-message="parentMsg"></child>
</div>
```

事件绑定、触发也是类似的写法，但是有一个例外：

```
<div id="app">
  <!-- select-item 在 HTML 中，用 kebab-case  -->
  <!-- alertItem 在 HTML 中，用 camelCase  -->
  <list :list="list" @select-item="alertItem"></list>
</div>

<script type="text/x-template" id="list">
  <ul>
      <!-- 例外！！ select-item 在 JavaScript 中，但在 $emit 时，要跟在上面声明时的保持一样  -->
    <li
      v-for="(item, index) in list"
      @click="$emit('select-item', item)"
    >{{ item }}</li>
  </ul>
</script>

<script>
  Vue.component('list', {
    props: ['list'],
    template: '#list'
  })
  new Vue({
    el: '#app',
    data: {
      list: [1,2,3,4]
    },
    methods: {
      // alertItem 在 HTML 中，用 camelCase
      alertItem: function(item){
        window.alert(item);
      }
    }
  })
</script>
```

使用 vue 时，要经常切换语境，所以很容易搞错。我在写这个应用时，偷了个懒，既不用驼峰，也不用烤串，更不用蛇形，组合词一律小写，比如: `togglemenu` 。工作中千万别这样写。




**加个后台吧**

**后记**