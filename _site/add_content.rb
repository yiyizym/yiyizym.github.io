# encoding: UTF-8
#!/usr/bin/env ruby
Dir.chdir('_posts') do 
  Dir.glob('*.markdown') do |filename|

    File.open(filename, mode: 'r+:UTF-8') do |file|
      content = file.read(file.size)
      # date = content.match(/date: (\d+-\d+-\d+)/)
      # if date.nil?
      #   puts filename
      # else
      #   purename = filename.gsub(/^[\d-]+/,'')
      #   puts purename
      #   File.rename(filename, "#{date[1]}-#{purename}")
      # end

      # if content.start_with? '-'
        
      # else
      #   file.rewind
      #   prepend_text = "---\nlayout: post\n"
      #   file.write (prepend_text + content).force_encoding("UTF-8")
      # end
    end
  end
end