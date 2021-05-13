def Ndeletion(input_file,output_file):
    # input_file='./one.fna'
    # output_file=open('./out.txt','w')
    counter=1
    mark=0
    past=1
    with open(input_file) as lines:
        temp=''
        for line in lines:
            if line[0]=='>':
                print('>contig' + str(counter),file=output_file)
                counter+=1
                continue
            for char in line:
                if char not in ['N',' ','\n']:
                    past=0
                    temp+=char
                    mark=0
                elif char=='N':
                    mark=1
            if mark==1 and past==0:
                    past=1
                    mark=0
                    print(temp)
                    print('>contig' + str(counter),file=output_file)
                    if len(temp)<=51:
                        print(temp,file=output_file)
                        temp=''
                    counter+=1
            if len(temp)>51:
                
                
                print(temp[:51],file=output_file)
                temp=temp[51:]
            mark=0
        
    output_file.close()
    
