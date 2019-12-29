# kackers-blockchained-notes task

> We found a strange service with secrets that use blockchain-like technology. 
> Evil kackers use it to store their secrets, maybe u can find something interesting.
> <br> http://tasks.open.kksctf.ru:20005/ 
> <br> @thunderstorm8

<details>
  <summary>Hint</summary>
  Next secret is chained to previous, link to next secret contains current location and current secret (except first step)
</details>

---

## Solution

``bash
    git clone github.com/wetox-team/kksctf && cd kackers-blockchained-notes
    pip install requests
    python3 script.py
``

* Первый уровень это страница на http://tasks.open.kksctf.ru:20005/c3e97dd6e97fb5125688c97f36720cbe.php
`"c3e97dd6e97fb5125688c97f36720cbe" == md5("$")` На странице имеется форма, в ней есть скрытое поле hash, 
которое является md5 от капчи с картинки. 
* Спарсив этот хэш находим само значение капчи (заранее надо сгенерировать 
хэши для всех четырехзначных комбинаций символов `0123456789abcdefghijklmnopqrstuvwxyz`). 
* Когда `captcha` найдена, ищем перебором такую строку `x`, что `md5(x)[28:] == captcha`. 
* Отправляем хэш капчи и полученую строку `x` на текущий адрес, получаем страницу со следующим секретным словом `secret`. 
* Пилим ссылку на следующий уровень: 
    `"tasks.open.kksctf.ru:20005/" + md5(current_url_pash + secret) + ".php"`. 
* Повторяем пока не дойдем до конца. Не забываем записывать все секретные слова, среди них затаился флаг.


<details>
  <summary>Secrets</summary>
   Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas in felis iaculis, venenatis enim sed, auctor ipsum. 
   Vestibulum dictum nisl vel faucibus condimentum. Sed eu risus vitae enim tempus efficitur. Maecenas lacinia sodales 
   ipsum sed congue. Sed porttitor tempus libero, sit amet molestie justo. Nullam pulvinar bibendum elit, nec finibus 
   nisl egestas eu. Suspendisse interdum, urna at efficitur pretium, felis tellus efficitur tellus, blandit cursus metus 
   turpis vel enim. Donec nec erat finibus eros fringilla accumsan ac in lectus. Phasellus eu felis consectetur, varius 
</details>
