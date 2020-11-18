## eSick (Web Easy) · Task by Artem Pavlov (@yorxx) · Par time: ~20 min

Have you ever heard about Black Hat Doctors? They have created a fake medical website! Can you h4ck them and get the flag?

I've found [something interesting](./esick_bfac_43da75d1c7.txt), this may come in handy.

---

## solution

Go to the web site of the task and after registration consider "Your patients" tab. Here we can add a sick leave. Let's do this and see that a new patient has been added. 

The task decription contains the output of the bfac utlity. We can download the source code of the page add.php from http://esick.student2020tasks.ctf.su/add.php.txt .

The interesting part of the code is uploading attachment on the site. The *$newname* of the attachment is formed from timestamp, UUID and the file extension that we uploaded hashed by the gost algorithm.
![](https://i.imgur.com/I8vN9v1.png)

The UUID is 32 random bytes so bruteforce won't help. If we look at the html code of the add.php page we may notice a hidden tag with the UUID value.

![](https://i.imgur.com/cthRqQW.png)

Let's write a simple php code that brute force timestamp and searches for the directory with our file. [*brute.php*](./brute.php)

Now upload the web shell, run the code and get access to the system. I used this [php shell](https://github.com/artyuum/Simple-PHP-Web-Shell).

Now, in the system, run the ***cd .. && cat flag.php*** and get the flag!

Flag: ***SPBCTF{php4ndf1l3upl04d4r34b0u7703xpl0d3}***
