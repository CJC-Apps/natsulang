# Natsulang text processing language
This is a small text processing language based on Python 3. It is now being used in a software called CJCMCG.
![](NatsulangImage.jpg)

## Example
Recently, a Chinese book called <平安经> is hot on the Internet. All sentences in this book is in the format of `**平安`. The most famous paragraph translated in English is like this:
```
Born safe. One month safe. 100 days safe. 1 year old safe. 2 years old safe. 3 years old safe. 4 years old safe. 5 years
old safe. 6 years old safe. 7 years old safe. 8 years old safe. 9 years old safe. 10 years old safe...
```
In chinese, the paragraph is:
```
初生平安，满月平安，百天平安，1岁平安，2岁平安，3岁平安，4岁平安，5岁平安，6岁平安，7岁平安，8岁平安，9岁平安，10岁平安...
```
This paragraph is so tidy, that it can be generated with programs. Using natsulang, you can generate this paragraph like below:
```
初生平安，满月平安，百天平安{s="";for(i:range(1,121))(s+="，"+str(i)+"岁平安");s}。
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

For Unix-based operating systems, download the `natsulang` file and put it into Path directories like `/usr/local/bin`.

For Windows, download the `natsulang` file to your user directory, and use `python natsulang` in the terminal (if the current directory is your user directory).

## Learn
You can learn Natsulang [here](https://github.com/CJC-Apps/natsulang/wiki).

English tutorials are preparing, please wait for some time.
