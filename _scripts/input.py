# coding=utf-8
import time

class ReadFile(object):
    """docstring for ReadFile"""
    def __init__(self, fileToRead):
        super(ReadFile, self).__init__()
        self.fileToRead = fileToRead
        self.fs = {
            'date': '',
            'content': [],
            'link': '',
            'comment': ''
        }
    def read(self):
        try:
            f = open(self.fileToRead,'r')
        except:
            print '\nnot such file.\n'
        for line in f.readlines():
            if len(line):
                if line.startswith('content:'):
                    self.fs['content'].append(line[8:].strip())
                elif line.startswith('link:'):
                    self.fs['link'] = line[5:].strip()
                elif line.startswith('comment:'):
                    self.fs['comment'] = line[8:].strip()
        f.close()
    def getReadFile(self):
        self.read()
        return self.fs

class FormatObj(object):
    """docstring for FormatObj"""
    def __init__(self, raw):
        super(FormatObj, self).__init__()
        self.raw = raw
        self.formatted = []

    def format(self):
        self.setDate()
        self.decorateContent()
        self.decorateLink()
        self.decorateComment()

    def setDate(self):
        self.formatted.append('\n\n' + '**' + time.strftime('%Y-%m-%d') + '**' + '\n')
    def decorateContent(self):
        content = ''
        for item in self.raw['content']:
            content += '\n' + '>' + item + '\n'
        self.formatted.append(content)
    def decorateLink(self):
        self.formatted.append('\n' + '* [出处](' + self.raw['link'] + ')'  + '\n')
    def decorateComment(self):
        if self.raw['comment']:
            self.formatted.append('\n' + '* ' + self.raw['comment']  + '\n\n')
    def getFormatted(self):
        self.format()
        return self.formatted

class WritFile(object):
    """docstring for WritFile"""
    def __init__(self, outputFile, formatted,insertPos):
        super(WritFile, self).__init__()
        self.formatted = formatted
        self.outputFile = outputFile
        self.insertPos = insertPos

    def write(self):
        try:
            r = open(self.outputFile)
        except:
            print '\nnot such file.\n'
        lines = r.readlines()
        r.close()
        lines = lines[:7] + self.formatted + lines[7:]
        try:
            w = open(self.outputFile,'w')
        except:
            print '\nnot such file.\n'
        w.write(''.join(lines))
        w.close()

class CleanIncome(object):
    """docstring for CleanIncome"""
    def __init__(self, income):
        super(CleanIncome, self).__init__()
        self.income = income
    def clean(self):
        try:
            f = open(self.income,'w')
        except:
            print '\nnot such file.\n'
        default = "content:\n\nlink:\n\ncomment:"

        f.write(default)
        f.close()
        
            


class Config(object):
    """docstring for Config"""
    def __init__(self, income, outcome, insertPos):
        super(Config, self).__init__()
        self.income = income
        self.outcome = outcome
        self.insertPos = insertPos

    def getIncomeFile(self):
        return self.income

    def getOutcomeFile(self):
        return self.outcome

    def getInsertPos(self):
        return self.insertPos

        
if __name__ == '__main__':

    config = Config('income.md','../_posts/2017-12-04-DRR201712.markdown',7)

    r = ReadFile(config.getIncomeFile())
    raw = r.getReadFile()
    f = FormatObj(raw)
    formatted = f.getFormatted()
    w = WritFile(config.getOutcomeFile(),formatted,config.getInsertPos())
    w.write()
    c = CleanIncome(config.getIncomeFile())
    c.clean()




