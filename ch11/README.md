The Kali version used at the time of writing was 2020.4 (GCC 10.2.0). Newer Kali/GCC versions breaks the `exploit3.py` and `exploit4.py` because the stack canary validation now affects the rdx register.

Here we've provided:
* A compiled `vuln` binary compiled on Kali 2020.4, to allow you to follow the same steps from the book in your own Kali version.
* A new working exploit (`exploit3-v2.py`) with a workaround to this problem. It should work on newer Kali versions (tested on Kali 2022.1 and Kali 2022.2).