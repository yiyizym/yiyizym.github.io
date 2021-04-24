---
layout: post
title: React Native FlatList 性能优化实践
date: 2021-01-27 10:20:28
excerpt: 
lang: zh_CN
categories: 
- frontend
---

**背景**

统计发现有 60% 的商家有使用我司手机端 APP 的习惯，为方便这一部分商家在 APP 上报名参与营销活动，在手机端也实现与现有 PC 端相似的 My Campaign 功能。

其中“可报名活动”页面，展示的活动列表条数有可能会多达几百上千条，在实现功能之前有必要考虑性能问题。
布局选择

在 web 端开发，如果我们页面的内容在垂直方向上超出了页面的尺寸，滚动条会出现；与 web 端不同，手机端(RN)并不会出现滚动条，超出页面的内容会直接被截断。

要在 RN 端显示超过一屏的内容，就要选择合适的「容器」: ScrollView / SectionList / FlatList 。

ScrollView 会将全部内容一次性渲染出来，适用于不太多的内容； 

SectionList 与 FlatList 就像 web 端的无限滚动，只会渲染部分内容，用于展示大量的列表内容，

SectionList适用于分组的列表数据，如联系人列表，FlatList 适用于更通用的场合。

**性能测量**

影响 RN 性能的问题会体现在两个线程上面： JS 线程和原生应用的主线程（UI 线程）。当你打开 RN 的 developer menu ，选择 Show Perf Monitor 就会显示这两个线程对帧率的影响：

![Show Perf Monitor]({{ site.url }}/assets/Show_Perf_Monitor.png)*Show Perf Monitor*
![Show Perf Monitor Threads]({{ site.url }}/assets/Show_Perf_Monitor_Threads.png)*Show Perf Monitor Threads*

可以看到页面静止时，上图无论 UI 还是 JS 的帧率最高都是 60 。

JS 线程对帧率的影响与 web 端的 React 应用类似，定位这方面的问题也与 web 端类似：在 developer menu 中选择 Debug JS Remotely ，在新打开的浏览器中打开开发者控制台，利用 Performance 标签中的功能定位问题。

而 UI 线程一般受图片形变、动画影响，通常不会是性能的瓶颈，出问题也很容易定位。

在测量性能之前，首先要确保你的 RN 应用运行在 production mode 。RN 应用运行在 development mode 时，因为要加入对开发友好的错误提示和类型检查，对 JS 线程的性能影响很大。


**FlatList 性能**

首先关注几个对性能有影响的属性：

- getItemLayout ，可以通过这个属性返回元素高度、宽度。与 web 端的无限滚动类似，如果列表中每个元素的高度都是固定的， FlatList 就可以省去动态计算要渲染的元素高度的步骤（非常耗费性能）；
- initialNumToRender，这个值表示初次需要渲染多少个列表元素，默认值是 10 。但是 10 通常太大，官方建议设置成填满首屏的数量即可，并且初次渲染的这些元素并不会被卸载。因此设置一个比 10 小的数字会提升性能；
- maxToRenderPerBatch，这个值表示每次触发渲染新列表元素时一次性渲染多少个列表元素，默认值是 10 。这个值设置得太小，滚动得快时就容易出现空白页面;设置得太大，内存消耗会变大，响应速度也会变慢；
- updateCellsBatchingPeriod，这个值设置渲染新列表元素的延迟时间，默认值是 50 （毫秒）。如果设置得太大，滚动时就容易出现空白，设置得太小性能亦会下降；
- 更多属性请参考[这里](https://github.com/filipemerker/flatlist-performance-tips/blob/master/README.md)。

**与业务结合的优化实践**

可以通过下面的动画了解需求:

{% include video.html name="react-native-flatList-performance-tuning-1.mp4" %}

总结一下：
- 页面有一个头部信息展示区域
- 当滚动到一定位置时，页面会显示/更新置顶元素
- 列表元素的高度不固定、且用户可以折叠、展开列表元素
- 右下角有一个「一键返回顶部」的按钮
- 页面有两个 tab ，其中第二个 tab 中可以勾选列表元素

![react_native_flatlist_sec_1]({{ site.url }}/assets/react_native_flatlist_sec_1.png)*react native flatlist section 1*
![react_native_flatlist_sec_2]({{ site.url }}/assets/react_native_flatlist_sec_2.png)*react native flatlist section 2*
![react_native_flatlist_sec_3]({{ site.url }}/assets/react_native_flatlist_sec_3.png)*react native flatlist section 3*


我们打开 Show Perf Monitor 看一下性能(in production mode & in iPhone SE(2nd) simulator)：

{% include video.html name="react-native-flatList-performance-tuning-2.mp4" %}

可以看到帧率很稳定，很少低于 60 。（肉眼能看到的卡顿是 simulator 的问题，在真机上不会有这个问题）

简单列举一下所做的性能优化:

1. 当需要使用 FlatList 渲染列表，但是页面包含除了列表之外的页头、页脚时，就可以用 FlatList 的 ListHeaderComponent/ListFooterComponent 属性渲染这些内容；
2. 就算列表元素的高度并不固定，也可以设置 getItemLayout 属性，替 FlatList 计算出渲染元素的高度，实现方式是用一个 map 记录下各个元素渲染时的高宽，避免重复计算；
3. 当用户点击 展开/折叠 按钮，列表元素会展开、折叠，继而触发 onLayout 事件，在这个事件回调中更新上面的 map ；
4. 可以看到，通常只要两个列表元素就能将首屏填满，因此将 initialNumToRender 属性值设置为 3；
5. 为了避免单个元素 展开/折叠 会触发整个 FlatList 重新渲染，在单个元素中用 hooks 管理自身的 展开/折叠 状态，触发渲染；
6. 虽然 FlatList 有设置置顶元素的属性 stickyHeaderIndices ，但是这个属性固定整个列表元素，而我们的需求只是固定列表的某部分；所以实现方式是设置单独的绝对定位元素、与 FlatList 元素并列位于某个容器下面；
7. 为避免频繁触发 FlatList 重新渲染，除了 data 属性之外，所有传入的 FlatList 的属性值都是简单值或者是方法、对象的引用；
8. 为了实现勾选元素时重新渲染列表（不然复选框不会显示选中），使用 extraData 属性值触发重新渲染；
9. 列表元素以及其子孙元素使用  React.memo 包裹，避免不必要的渲染；
10. 一些状态值，如果不涉及重新渲染，则不保存在 State 中，而是保存在组件的 private 属性中；
11. 一些保存在 State 中的状态值（如是否显示「一键返回顶部」按钮），如果计算得出没有发生改变，就不调用 setState 。

参考：
- [reactnative performance](https://archive.reactnative.dev/docs/performance)
- [reactnative flatlist](https://archive.reactnative.dev/docs/flatlist)
- [flatlist-performance-tips](https://github.com/filipemerker/flatlist-performance-tips/blob/master/README.md)
- [scrolling-issues-with-flatlist-when-rows-are-variable-height](https://stackoverflow.com/questions/43709142/scrolling-issues-with-flatlist-when-rows-are-variable-height)