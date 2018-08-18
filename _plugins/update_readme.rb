#!/usr/bin/env ruby
# encoding: UTF-8

Jekyll::Hooks.register :site, :post_render do |site, payload|
  filename = "README.md"
  if !File.exist? filename
    puts 'file not exsit!'
    exit 1
  end

  posts_list = site.posts.docs.map { |post| "- [#{post.data['title']}](https://judes.me#{post.url}) \n" }

  posts_list = posts_list.reverse.join('')

  content = <<HEAR
**个人 中文 博客**

关于生活，读书和编程，[网址](https://judes.me)

**文章列表**

#{posts_list}

**更新计划**

见 Issues 
HEAR

  File.open(filename, mode: 'w:UTF-8') do |f|
    f.write content.force_encoding("UTF-8")
  end

  puts "readme updated!"
end