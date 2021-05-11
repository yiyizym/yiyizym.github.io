---
layout: post
title: React Native FlatList performance tuning
date: 2021-02-17 10:20:28
excerpt: Some optimization practices and suggestions
lang: en
categories: 
- frontend
---

**Background**

We found that 60% of the merchants have the habit of using our mobile APP, in order to facilitate these merchants to participate in marketing campaigns on the APP, we want to implement the "My Campaign" functionality on the mobile side similar to the existing PC side.

The number of campaigns displayed on the "Available Campaigns" page may be as many as several thousand. so it is necessary to consider performance issues before implementing functionality.

**Layout**

In web development, if the content of our page exceeds the size of the page vertically, a scroll bar will appear; unlike web-side, the scroll bar does not appear in mobile (RN), and the content that exceeds the page will be truncated directly.

To display more than one screen of content on the RN side, you need to choose a suitable "container": ScrollView / SectionList / FlatList.

ScrollView renders all the content at once, which is suitable for not too much content. 

SectionList and FlatList are like infinite scrolling technique on the web, rendering only part of the content, and are used to display a large amount of list content.

SectionList is suitable for grouped list data, such as contact lists, and FlatList is suitable for more general purposes.

**Performance Measurement**

If RN's performance is affected, it will be shown on two threads: the JS thread and the main thread of the native application (UI thread). When you open RN's developer menu and select Show Perf Monitor it will show you the impact of these two threads on the frame rate.

![Show Perf Monitor]({{ site.url }}/assets/Show_Perf_Monitor.png)*Show Perf Monitor*
![Show Perf Monitor Threads]({{ site.url }}/assets/Show_Perf_Monitor_Threads.png)*Show Perf Monitor Threads*

You can see that the frame rate of both the UI and JS in the above image is up to 60 when the page is stationary.

The impact of JS threads on frame rates is similar to that of web-side React applications, and locating issues in this area is similar to that of the web side: select Debug JS Remotely in the developer menu, open the developer console in a newly opened browser, and use the Performance tab to locate the issue.

UI threads are generally affected by image transforming and animation, and are usually not a bottleneck for performance, so problems are easy to locate.

Before measuring performance, first make sure your RN application is running in production mode. RN applications running in development mode have a significant impact on the performance of JS threads because of the overheads of developer-friendly error hints and type checking.

**FlatList Performance**

First focus on a few properties that have an impact on performance.

- getItemLayout , which gets the height and width of an item. Similar to infinite scrolling on the web, if the height of each item in the list is fixed, the FlatList eliminates the need to dynamically calculate the height of the item to be rendered (which is very performance intensive).
- initialNumToRender, which indicates how many list items need to be rendered initially, defaults to 10. However, 10 is usually too large and the official recommendation is to set it to the number that fills the first screen, and the initial rendered items will not be unmounted. So setting a smaller number than 10 will improve performance.
- maxToRenderPerBatch, which indicates how many list items are rendered at once each time the rendering is triggered; the default value is 10. If this value is set too small, a blank page will easily appear when scrolling fast; if it is set too large, memory consumption will go up and response speed will slow down.
- updateCellsBatchingPeriod, this value sets the delay time for rendering new list items, the default value is 50 (milliseconds). In contrast to maxToRenderPerBatch, if it is set too large, a blank page will easily appear when scrolling fast, and if it is set too small, performance will be degraded.
- [here](https://github.com/filipemerker/flatlist-performance-tips/blob/master/README.md) for more properties.

**Optimization practices with business logic**

the following animation shows the requirements:

{% include video.html name="react-native-flatList-performance-tuning-1.mp4" %}


To summarize.

- The page has a header information display area
- When scrolling to a certain position, the page will display and update the element stick to the top
- The height of the list element is not fixed, and the user can collapse and expand the list element by clicking it
- There is a "back to top" button in the bottom right corner
- The page has two tabs, in the second of which user can select some list elements by ticking them.

![react_native_flatlist_sec_1]({{ site.url }}/assets/react_native_flatlist_sec_1.png)*react native flatlist section 1*
![react_native_flatlist_sec_2]({{ site.url }}/assets/react_native_flatlist_sec_2.png)*react native flatlist section 2*
![react_native_flatlist_sec_3]({{ site.url }}/assets/react_native_flatlist_sec_3.png)*react native flatlist section 3*


我们打开 Show Perf Monitor 看一下性能(in production mode & in iPhone SE(2nd) simulator)：

Let's open Show Perf Monitor to see the performance(in production mode & in iPhone SE(2nd) simulator).

{% include video.html name="react-native-flatList-performance-tuning-2.mp4" %}

You can see that the frame rate is very stable, rarely below 60. (The lag that you can see is a simulator problem, not a problem on the real machine)

A brief list of performance optimizations:

1. when you need to render a list with FlatList, but the page contains headers and footers in addition to the list, you can use the ListHeaderComponent/ListFooterComponent property of FlatList to render these contents.
2. even if the height of the list element is not fixed, you can set the getItemLayout property to calculate the height of the rendered element for the FlatList, by using a map to record the height and width of each element when it is rendered, to avoid repeatedly calculation.
3. when the user clicks the expand/collapse button, the list element will be expanded/collapsed, and then the onLayout event will be triggered, and the map above will be updated in this event callback;
4. it can be seen that usually only two list elements are needed to fill in the first screen, so the initialNumToRender property is set to 3.
5. to avoid the element expanding/collapsing triggering the re-render of the entire FlatList, use react hooks in each element to manage their own expand/collapse state, then trigger the rendering.
6. although the FlatList has the property stickyHeaderIndices to set the sticky element, this property fixes the whole list element to the list top, and our need is to fix only a certain part of the element; so the way to implement it is to create a separate absolutely positioned element, places it with the FlatList element under the same container.
7. to avoid frequent re-rendering of the FlatList, all FlatList property values are immutable values or references to methods or objects, except for the data property.
8. to re-render the list when an element is checked (otherwise the checkbox would not show checked), use the extraData property to trigger re-rendering.
9. using React.memo wrapping for list elements and their descendants to avoid unnecessary rendering.
10. some values, which do not involve re-rendering, are not stored in the State but in the component's private property.
11. If we find that some of the values stored in the State have not changed after some calculations, we do not call setState.

**Reference**

- [reactnative performance](https://archive.reactnative.dev/docs/performance)
- [reactnative flatlist](https://archive.reactnative.dev/docs/flatlist)
- [flatlist-performance-tips](https://github.com/filipemerker/flatlist-performance-tips/blob/master/README.md)
- [scrolling-issues-with-flatlist-when-rows-are-variable-height](https://stackoverflow.com/questions/43709142/scrolling-issues-with-flatlist-when-rows-are-variable-height)