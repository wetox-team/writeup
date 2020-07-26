## Google Cloud \[Network\]

Author: Vlad Roskov ([@mrvos](https://t.me/mrvos))

I am storing some important stuff in Google's cloud.
Nooo no no, not on Google's disks — in the cloud itself.

Check [./gcloud.tar.gz](gcloud.tar.gz)

---

## Solution

1. Get all the values of the data.data fields [data]

2. Leave only those that cannot be converted to ascii text \[nonascii_bytes\]

3. Leave only unique lines, keeping the order \[unique_nonascii_bytes\]

4. Remove values that are the beginning or end of adjacent \[definitely_unique_nonascii_bytes\]

5. Remove the first value \[jpg_bytes\] and write to flag.jpg

Flag is [here](./flag.jpg)

