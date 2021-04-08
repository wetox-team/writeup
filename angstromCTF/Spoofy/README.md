ångstromCTF 2021


# Spoofy 
## 160 points · 176 solves

Clam decided to switch from repl.it to an actual hosting service like Heroku. In typical clam fashion, [he left a backdoor in](https://actf-spoofy.herokuapp.com/). Unfortunately for him, he should've stayed with repl.it...

[Source](https://files.actf.co/9cb4b04e3973b171a4b8d244152140326dd6474b54b2b040170c2bf2a9d2a509/app.py)
* * *

### Solution

Open the website and realize that it doesn't trust us:
`I don't trust you >:(`

See the response in BurpSuite:


![Screenshot from BurpSuite](https://i.ibb.co/7CNDrBf/Screenshot-from-2021-04-07-22-48-51.png)

Nothing interesting.

Let's take a look at the source code to understand why this happening.   
We are interesting only in **main_page** function. First, it checks if there is **X-Forwarded-For** header in the request:
```python
if "X-Forwarded-For" in request.headers:
	..
else:
    return text_response("Please run the server through a proxy.", 400)
```

In out request there is no such header but we aren't given this 400 error. It happening because server run through a proxy.

Next, it divides the header by comma, checks whether the first ip is equal to the last and whether it is equal to **1.3.3.7**:
```python
ips: List[str] = request.headers["X-Forwarded-For"].split(", ")
if not ips:
   return text_response("How is it even possible to have 0 IPs???", 400)
if ips[0] != ips[-1]:
   return text_response(
                "First and last IPs disagree so I'm just going to not serve this request.",
                400,
            )
ip: str = ips[0]
if ip != "1.3.3.7":
    return text_response("I don't trust you >:(", 401)
return text_response("Hello 1337 haxx0r, here's the flag! " + FLAG)
```
Oh, at first it seems like a simple task, because you just need to send the **X-Forwarded-For** header with **1.3.3.7** value and then you will pass all the conditions. But if we try to do this, we will get this error:
`First and last IPs disagree so I'm just going to not serve this request.`

This happened because Heroku has **router** and the router doesn't overwrite **X-Forwarded-For**, but it does guarantee that the real origin will always be the last item in the list.

You can read a little more about this [here](https://stackoverflow.com/questions/18264304/get-clients-real-ip-address-on-heroku) and [here](https://devcenter.heroku.com/articles/http-routing#heroku-headers).

Next, to play around with the **ips** array, I raised [a copy of the server on Heroku](https://infin-ctf.herokuapp.com/), but I have it output the ips array with each request. And if we just GET this site, we will see that our real ip is in the **ips** array.

After some time, I realized a few things:
- When the **X-Forwarded-For** header is first declare, its value is added as the first element of the array
- Each subsequent ad of this header will concatenate its value to our real IP.
- Adding another value in the second **X-Forwarded-For** header will add it as the last element of the array.

So, the final request looks like this:
```http
GET / HTTP/1.1
Host: actf-spoofy.herokuapp.com
X-Forwarded-For: 1.3.3.7  
X-Forwarded-For: <random_ip>, 1.3.3.7
Upgrade-Insecure-Requests: 1
```

And we get the flag `actf{spoofing_is_quite_spiffy}`!

## P.S.
Some time after solve this task I found out that is called **X-Forwarder-For spoofing**. Yeh, I know that the task was called Spoofy and I could have guessed it, but... I solved this witout knowledge of it xD
