# Natsulang text processing language
This is a small text processing language based on Python 3. It is now being used in a software called CJCMCG.
![](https://github.com/CJC-Apps/natsulang/blob/master/NatsulangImage.jpg?raw=true)

## Example
Recently, a Chinese book called <ƽ����> is hot on the Internet. All sentences in this book is in the format of `**ƽ��`. The most famous paragraph translated in English is like this:
```
Born safe. One month safe. 100 days safe. 1 year old safe. 2 years old safe. 3 years old safe. 4 years old safe. 5 years
old safe. 6 years old safe. 7 years old safe. 8 years old safe. 9 years old safe. 10 years old safe...
```
In Chinese, the paragraph is:
```
����ƽ��������ƽ��������ƽ����1��ƽ����2��ƽ����3��ƽ����4��ƽ����5��ƽ����6��ƽ����7��ƽ����8��ƽ����9��ƽ����10��ƽ��...
```
This paragraph is so tidy, that it can be generated with programs. Using natsulang, you can generate this paragraph like below:
```
����ƽ��������ƽ��������ƽ��{s="";for(i:range(1,121))(s+="��"+str(i)+"��ƽ��");s}��
```
Maybe you are headache with your math proofs. This is not a problem in Natsulang. Just use the following program:
```
Input what you want to proof: {name=input();}
Proof:

Proposition A: {name}
Proposition B: Proposition C is false.
Proposition C: At lease one proposition between A and B is true.

Lemma 1: Proposition C is true

Proof: If C is false, then A and B is both false, and B is false, then C is true. This contradicts.

Now start proof:

If A is false, since C is true, B is true, and C is false. This contradicts. So A is true, i.e., {name}

Q.E.D
```
Can you find how this program works?

## Run Natsulang
First, you need to download Python 3 and install. If you're using Windows, you need to add Python 3 to Path.

Then, type `pip install natsulang` in the terminal, and wait for it complete.

Finally, type `natsulang` in the terminal. If no error occurs, the installation is success.

If you need to upgrade natsulang, please use `pip install --upgrade natsulang`.

## Learn
You can learn Natsulang [here](https://github.com/CJC-Apps/natsulang/wiki).

English tutorials are preparing, please wait for some time.
