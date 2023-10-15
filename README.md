# command-and-control

### Setup instructions

If the source code has changed since pulling this repository, run
`tar -czvf c2 setup.sh victim.py remove-victim.sh unzip.sh`

Then `scp` the c2 tarball from your computer to the victim week4 machine.

On the victim machine run `tar -xzvf c2` to extract the contents, then run `./setup.sh`.

`scp` attack.py from your computer to the attacker Kali machine if need be.
Edit line 25 in attack.py with the IP address outputted from `ip addr` in the victim machine.

Run `reboot` on the victim machine to open up the backdoor