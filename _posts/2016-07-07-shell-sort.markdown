---
layout: post_with_octocat
title: 写写希尔排序
date: 2016-07-07 08:11:43
excerpt: 为什么知道原理还是写不出正确的程序呢？(系列)
categories: tech
tags:
- algorithm
- shell sort
- ruby

---

希尔排序不应该放在这个系列的，因为并不十分清楚它的原理，想要完整了解的朋友请看[维基百科](https://zh.wikipedia.org/wiki/%E5%B8%8C%E5%B0%94%E6%8E%92%E5%BA%8F)

下面是原理的简单解释：

## 原理

希尔排序是"插入排序的一种更高效的改进版本"，从这个角度理解，它继承了插入排序的优点：

- 对大体已排好序的集合有相当高的效率

解决了插入排序的一点不足：

- 每次比较只能把待排序元素移动一位，如果待排序元素离最终位置比较远，需要多次操作

希尔排序依靠变化的比较、交换步长解决这点不足：先用较大的步长把集合整理在大体有序，最后使用步长为 1 的插入排序整理成完全有序。

## 联想

希尔排序的内核是插入排序，在插入排序的外面再包裹一层循环——让步长从某个初始值逐渐变小到 1 。这个初始值定为待排序集合长度的 1/3 处。


## 用法

    #!/usr/bin/env ruby
    sorted_array = SS.sort(array)

## 大体结构

    #!/usr/bin/env ruby
    class SS
      class << self
        def sort array
          return array if array.size <= 1
          step = (array.size / 3.0).ceil
          while step >= 1
            # insertion sort  
            step -= 1
          end
          array
        end
      end
    end

## 插入排序部分

插入排序可以参考之前写过的[文章](/2016/07/05/insertion-sort/)，要点是对插入排序的内、外两层循环都应用可变步长

    #!/usr/bin/env ruby
    class SS
      class << self
        def sort array
          len = array.size
          return array if len <= 1
          step = (len / 3.0).ceil
          while step >= 1
            tag = step
            while tag < len
              inner_tag = tag
              while inner_tag >= 1 && array[inner_tag] < array[inner_tag - step]
                exchange(array, inner_tag, inner_tag - step)
                inner_tag -= step
              end
              tag += step
            end
            step -= 1
          end
          array
        end
        def exchange array, i, j
          array[i], array[j] = array[j], array[i]
        end
      end
    end

## 完整的代码，加测试用例如下：

    #!/usr/bin/env ruby

    class SS
      class << self
        def sort array
          len = array.size
          return array if len <= 1
          step = (len / 3.0).ceil
          while step >= 1
            tag = step
            while tag < len
              inner_tag = tag
              while inner_tag >= 1 && array[inner_tag] < array[inner_tag - step]
                exchange(array, inner_tag, inner_tag - step)
                inner_tag -= step
              end
              tag += step
            end
            step -= 1
          end
          array
        end
        def exchange array, i, j
          array[i], array[j] = array[j], array[i]
        end
      end
    end

    if __FILE__ == $0

      require 'test/unit'

      class TestSS < Test::Unit::TestCase
        def test_0
          input = []
          expected = []
          assert_equal SS.sort(input), expected, 'empty array not equal'
        end
        def test_1_0
          input = [0]
          expected = [0]
          assert_equal SS.sort(input), expected, 'one item array not equal'    
        end
        def test_1_1
          input = [1]
          expected = [1]
          assert_equal SS.sort(input), expected, 'one item array not equal'    
        end
        def test_2_0
          input = [0,1]
          expected = [0,1]
          assert_equal SS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_1
          input = [1,0]
          expected = [0,1]
          assert_equal SS.sort(input), expected, 'two items array not equal'    
        end
        def test_2_2
          input = [1,1]
          expected = [1,1]
          assert_equal SS.sort(input), expected, 'two items array not equal'    
        end
        def test_3_0
          input = [0,1,2]
          expected = [0,1,2]
          assert_equal SS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_1
          input = [0,2,1]
          expected = [0,1,2]
          assert_equal SS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_2
          input = [2,1,0]
          expected = [0,1,2]
          assert_equal SS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_3
          input = [2,1,1]
          expected = [1,1,2]
          assert_equal SS.sort(input), expected, 'three items array not equal'    
        end
        def test_3_4
          input = [1,1,1]
          expected = [1,1,1]
          assert_equal SS.sort(input), expected, 'three items array not equal'    
        end
        def test_4_0
          input = [0,1,2,3]
          expected = [0,1,2,3]
          assert_equal SS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_1
          input = [3,1,2,0]
          expected = [0,1,2,3]
          assert_equal SS.sort(input), expected, 'four items array not equal'    
        end
        def test_4_2
          input = [3,1,2,1]
          expected = [1,1,2,3]
          assert_equal SS.sort(input), expected, 'four items array not equal'    
        end
        def test_10_0
          input = [9,8,7,6,5,4,3,2,1,0]
          expected = [0,1,2,3,4,5,6,7,8,9]
          assert_equal SS.sort(input), expected, 'four items array not equal'    
        end
        def test_10_1
          input = [9,5,7,3,8,4,6,1,2,0]
          expected = [0,1,2,3,4,5,6,7,8,9]
          assert_equal SS.sort(input), expected, 'four items array not equal'    
        end
      end
    end