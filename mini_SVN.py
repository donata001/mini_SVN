import sys
import formatter
from htmllib import HTMLParser
import difflib
import re

#get file names from cmd
old=sys.argv[1]
new=sys.argv[2]
#prepare plain text writer
wre = formatter.DumbWriter() 
fmt = formatter.AbstractFormatter(wre)


#override HTMLParser class method to get parsed data
all_data=[]
class MyHTMLParser(HTMLParser):    
    def handle_data(self,data):
        global all_data
        all_data.append(data)

p = MyHTMLParser(fmt)

#pull original web page data

f=open(old,'r')      
raw_A=''.join(f.readlines())           
f.close()

#pull new web page data

f=open(new,'r')
raw_B=''.join(f.readlines())           
f.close()
  

#add tag to a new file, indicating all the change
def Addtag_to_rawfile(seq):
    result=[]

    
    for opcode,a0,a1,b0,b1 in seq.get_opcodes():
        
        global all_data        
        if opcode=='equal':
            result.append(seq.a[a0:a1])
            
        elif opcode=='insert':
            p.feed(seq.b[b0:b1])  #send to HTML Parser
            
            if all_data:   
                
                text_data=''.join(all_data)                   
                result.append(seq.b[b0:b1])
                text_list=re.split(r'[ \n<>,()]*',text_data)   #remove space,\n,<>,() and send to list
                
                for text in text_list:
                    if text:    
                        try:   #add insert tag
                            result[-1]=re.sub(r'([> ,]*)('+text+')([ ,.<]*)',r'\1<ins>\2</ins>\3',result[-1])                        
                        except:                            
                            continue                                    
            else:
                pass                    
            all_data=[]    #clear all_data buffer
            p.close()
            
        elif opcode=='delete':
            p.feed(seq.a[a0:a1])
            
            if all_data:
                text_data=''.join(all_data)                        
                result.append(seq.a[a0:a1])
                text_list=re.split(r'[ \n<>,()]*',text_data)
                
                for text in text_list:
                    if text:    
                        try:
                            result[-1]=re.sub(r'([> ,]*)('+text+')([ ,.<]*)',r'\1<del>\2</del>\3',result[-1])                        
                        except:                            
                            continue     
            else:
                pass
            all_data=[]
            p.close()

        elif opcode=='replace':
            p.feed(seq.b[b0:b1])
            
            if all_data:
                text_data=''.join(all_data)                        
                result.append(seq.b[b0:b1])
                text_list=re.split(r'[ \n<>,()]*',text_data)
                
                for text in text_list:
                    if text:    
                        try:
                            result[-1]=re.sub(r'([> ,]*)('+text+')([ ,.<]*)',r'\1<mark>\2</mark>\3',result[-1])                        
                        except:                            
                            continue            
            else:
                pass    
            all_data=[]
            p.close()
                
        else:
            raise RuntimeError, "unexpected opcode"
    return ''.join(result)
                
               
rawHTML=difflib.SequenceMatcher(None,raw_A,raw_B)  #load rawdata A B into SM
raw_diff=Addtag_to_rawfile(rawHTML)    #call add tag function


f=open('HTMLdiff.html','w+')
f.write(raw_diff)
f.close()

print 'Done, please check'


