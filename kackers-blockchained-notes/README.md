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
   elit consectetur, feugiat odio. Morbi malesuada tellus ac nisi fringilla iaculis. Sed sed lacus ullamcorper, dictum 
   dui non, mattis purus. Proin fermentum egestas enim non varius. Pellentesque feugiat sapien felis, id efficitur mi 
   tincidunt et. Curabitur eu bibendum orci, sit amet blandit dui. Aliquam porttitor ac nisi eget porttitor. Aliquam 
   eget eleifend quam. Integer hendrerit ligula vel enim sagittis tincidunt. Sed vitae felis a mi sodales sagittis at in 
   diam. Vestibulum scelerisque egestas turpis eget ultrices. Cras quis suscipit mauris. Vivamus egestas mattis metus, 
   a ornare ligula ultrices nec. Duis quis ipsum non arcu placerat fringilla ac a quam. Nam lobortis, erat eget egestas 
   semper, est sem mollis quam, nec gravida purus nisl et nunc. Sed eu est lorem. In venenatis scelerisque justo, ac 
   viverra nibh. Donec non vestibulum dui. Sed pulvinar, nunc non lobortis condimentum, risus leo finibus libero, vel 
   accumsan urna neque a nisi. Phasellus lorem velit, facilisis quis condimentum vitae, fermentum sed mi. Nulla et ipsum 
   eget purus finibus facilisis. Nulla id justo at lorem vehicula efficitur. Suspendisse sagittis nec tellus ac ullamcorper. 
   Duis tincidunt non urna a commodo. Curabitur enim metus, viverra sit amet venenatis eget,
   k k s lbrace d0 _ u _ r34lly _ l1k3 _ w3b _ bl0ckCh4in _ T3ch rbrace consectetur a est. Duis ac velit in risus consectetur
   consectetur. Donec volutpat ipsum tempor efficitur condimentum. Maecenas dictum, eros a ornare efficitur, quam dui mollis 
   ante, nec feugiat risus leo quis augue. Donec ex arcu, malesuada sed bibendum vel, rutrum at purus. Maecenas blandit 
   tristique lorem, sed consequat felis. Praesent faucibus turpis quis vehicula mattis. Ut sed euismod libero. Maecenas 
   non quam eget ex laoreet hendrerit porta vitae arcu. Donec id magna egestas, vehicula libero sed, faucibus tellus. 
   Pellentesque in scelerisque dolor. Aenean vel eros suscipit ligula tincidunt lacinia a eleifend magna. Phasellus 
   interdum nibh et mauris efficitur commodo. Aenean auctor libero fermentum tempus consectetur. Aliquam lobortis molestie 
   imperdiet. Aliquam ut interdum lacus, sed maximus dui. In nunc mi, sagittis ac velit ut, laoreet hendrerit felis. Nunc 
   ante felis, commodo nec aliquam id, posuere ut augue. 
</details>
